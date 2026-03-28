from __future__ import annotations

import hashlib
import time
from typing import Any

from pydantic import ValidationError

from src.application.errors import BackendInvocationError, ConfigLoadError, InvalidModeError
from src.application.orchestrators.mode_registry import MODE_REGISTRY
from src.application.services.diff_processor import DiffProcessor
from src.application.services.secret_masker import mask_secrets
from src.config.models import load_model_config
from src.config.settings import settings
from src.domain.models.schemas import AnalysisRequest
from src.domain.rules.test_requirement import evaluate_test_requirement
from src.infrastructure.llm.adapter import LLMAdapter
from src.infrastructure.prompts.renderer import PromptRenderer
from src.infrastructure.storage.repositories.interfaces import ResultRepository, TraceRepository


class AnalysisOrchestrator:
    def __init__(self, trace_repo: TraceRepository, result_repo: ResultRepository):
        self.trace_repo = trace_repo
        self.result_repo = result_repo
        self.renderer = PromptRenderer(settings.prompt_templates_path)
        self.diff_processor = DiffProcessor(
            max_bytes=settings.max_diff_bytes,
            max_lines=settings.max_diff_lines,
            max_files=settings.max_changed_files,
        )

    def run(self, mode: str, request: AnalysisRequest) -> dict[str, Any]:
        started = time.time()
        trace_payload = self._build_base_trace(mode=mode, raw_diff=request.diff)

        try:
            if mode not in MODE_REGISTRY:
                raise InvalidModeError(f"Unsupported mode: {mode}")

            preprocessed = self._preprocess(mode=mode, request=request, trace_payload=trace_payload)
            raw_json = self._call_llm(mode=mode, prompt=preprocessed["prompt"], trace_payload=trace_payload)
            if mode == "test-check":
                raw_json.setdefault("test_required", preprocessed["rule_result"].test_required)
                raw_json.setdefault("why", preprocessed["rule_result"].why)
                raw_json.setdefault("missing_scenarios", preprocessed["rule_result"].missing_scenarios)
                raw_json.setdefault("priority", preprocessed["rule_result"].priority)
            raw_json.setdefault("limitations", [])
            raw_json["limitations"] = list(raw_json.get("limitations", [])) + preprocessed["limitations"]
            trace_payload["raw_model_response"] = raw_json
            response = self._validate_output(mode=mode, payload=raw_json)
            return self._finalize_response(started=started, trace_payload=trace_payload, root_response=response)
        except (InvalidModeError, ConfigLoadError, BackendInvocationError) as exc:
            root_response = self._error_response(
                error_type=exc.error_type,
                message=exc.message,
                partial=trace_payload.get("raw_model_response", {}),
            )
            trace_payload["error"] = root_response["error"]
            return self._finalize_response(started=started, trace_payload=trace_payload, root_response=root_response)
        except Exception as exc:
            root_response = self._error_response(
                error_type="internal_error",
                message=str(exc),
                partial=trace_payload.get("raw_model_response", {}),
                limitations=["Request handling failed unexpectedly."],
            )
            trace_payload["error"] = root_response["error"]
            return self._finalize_response(started=started, trace_payload=trace_payload, root_response=root_response)

    def _preprocess(self, mode: str, request: AnalysisRequest, trace_payload: dict[str, Any]) -> dict[str, Any]:
        masked_diff = request.diff
        if settings.secret_masking_enabled:
            masked_diff, trace_payload["redactions"] = mask_secrets(masked_diff)

        processed = self.diff_processor.process(masked_diff)
        limitations = list(processed.limitations)
        trace_payload["dropped_lines"] = processed.dropped_lines

        rule_result = evaluate_test_requirement(processed.normalized_diff)
        prompt = self.renderer.render(
            mode=MODE_REGISTRY[mode]["template"],
            diff=processed.normalized_diff,
            metadata=request.metadata,
            context=request.context,
            existing_tests=request.existing_tests,
        )
        trace_payload["prompt"] = prompt
        return {
            "prompt": prompt,
            "limitations": limitations,
            "rule_result": rule_result,
        }

    def _call_llm(self, mode: str, prompt: str, trace_payload: dict[str, Any]) -> dict[str, Any]:
        try:
            _, profile = load_model_config()
        except Exception as exc:
            raise ConfigLoadError(str(exc)) from exc

        adapter: LLMAdapter | None = None
        try:
            adapter = LLMAdapter(profile=profile, mode=mode)
            trace_payload["model"] = adapter.metadata.__dict__
            payload = adapter.generate_json(prompt)
            trace_payload["raw_model_response"] = payload
            return payload
        except Exception as exc:
            raise BackendInvocationError(str(exc)) from exc
        finally:
            if adapter is not None:
                adapter.close()

    def _validate_output(self, mode: str, payload: dict[str, Any]) -> dict[str, Any]:
        schema = MODE_REGISTRY[mode]["schema"]
        try:
            return schema.model_validate(payload).model_dump()
        except ValidationError as exc:
            diagnostics = f"Validation fallback: {exc}"
            fallback = dict(payload)
            fallback["limitations"] = list(payload.get("limitations", [])) + [diagnostics]
            return {
                "partial": fallback,
                "validation_error": diagnostics,
                "limitations": list(fallback.get("limitations", [])),
            }

    def _build_base_trace(self, mode: str, raw_diff: str) -> dict[str, Any]:
        return {
            "mode": mode,
            "diff_hash": hashlib.sha256(raw_diff.encode("utf-8")).hexdigest(),
            "masked": settings.secret_masking_enabled,
            "redactions": 0,
            "dropped_lines": 0,
            "model": {},
            "prompt": "",
            "raw_model_response": {},
        }

    def _attach_persistence_error(self, root_response: dict[str, Any], persistence_message: str) -> dict[str, Any]:
        final_response = dict(root_response)
        final_response["persistence_error"] = {
            "type": "persistence_error",
            "message": persistence_message,
        }
        final_response["limitations"] = list(final_response.get("limitations", [])) + [
            "Failed to persist trace/result payloads."
        ]
        return final_response

    def _finalize_response(self, started: float, trace_payload: dict[str, Any], root_response: dict[str, Any]) -> dict[str, Any]:
        elapsed_ms = int((time.time() - started) * 1000)

        trace_payload["timing_ms"] = elapsed_ms
        trace_payload["final_response"] = root_response

        trace_error: str | None = None
        result_error: str | None = None

        try:
            self.trace_repo.save(trace_payload)
        except Exception as exc:
            trace_error = str(exc)

        result_payload = {
            "mode": trace_payload.get("mode"),
            "parsed": root_response,
            "timing_ms": elapsed_ms,
        }
        try:
            self.result_repo.save(result_payload)
        except Exception as exc:
            result_error = str(exc)

        if not trace_error and not result_error:
            return root_response

        errors = []
        if trace_error:
            errors.append(f"trace save failed: {trace_error}")
        if result_error:
            errors.append(f"result save failed: {result_error}")

        return self._attach_persistence_error(root_response=root_response, persistence_message='; '.join(errors))

    def _error_response(
        self,
        error_type: str,
        message: str,
        partial: dict[str, Any],
        limitations: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "error": {
                "type": error_type,
                "message": message,
            },
            "partial": partial,
            "limitations": list(limitations or []),
        }
