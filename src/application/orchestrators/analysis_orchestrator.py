from __future__ import annotations

import hashlib
import time
from typing import Any

from pydantic import ValidationError

from src.application.services.diff_processor import DiffProcessor
from src.application.services.secret_masker import mask_secrets
from src.config.models import load_model_config
from src.config.settings import settings
from src.domain.models.schemas import (
    AnalysisRequest,
    ReviewResponse,
    TestCheckResponse,
    TestGenResponse,
    TestMaintainResponse,
    TestScenariosResponse,
)
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
        profile_cfg, profile = load_model_config()
        masked_diff = request.diff
        redactions = 0
        if settings.secret_masking_enabled:
            masked_diff, redactions = mask_secrets(masked_diff)

        processed = self.diff_processor.process(masked_diff)
        limitations = list(processed.limitations)

        rule_result = evaluate_test_requirement(processed.normalized_diff)
        prompt = self.renderer.render(
            mode=mode,
            diff=processed.normalized_diff,
            metadata=request.metadata,
            context=request.context,
            existing_tests=request.existing_tests,
        )

        adapter = LLMAdapter(profile=profile, mode=mode)
        raw_json = adapter.generate_json(prompt)
        adapter.close()

        if mode == "test-check":
            raw_json.setdefault("test_required", rule_result.test_required)
            raw_json.setdefault("why", rule_result.why)
            raw_json.setdefault("missing_scenarios", rule_result.missing_scenarios)
            raw_json.setdefault("priority", rule_result.priority)

        raw_json.setdefault("limitations", [])
        raw_json["limitations"] = list(raw_json.get("limitations", [])) + limitations

        parsed = self._validate(mode, raw_json)
        elapsed_ms = int((time.time() - started) * 1000)

        trace_payload = {
            "mode": mode,
            "diff_hash": hashlib.sha256(request.diff.encode("utf-8")).hexdigest(),
            "masked": settings.secret_masking_enabled,
            "redactions": redactions,
            "dropped_lines": processed.dropped_lines,
            "model": adapter.metadata.__dict__,
            "prompt": prompt,
            "raw_model_response": raw_json,
            "timing_ms": elapsed_ms,
        }
        result_payload = {
            "mode": mode,
            "parsed": parsed,
            "timing_ms": elapsed_ms,
        }
        self.trace_repo.save(trace_payload)
        self.result_repo.save(result_payload)
        return parsed

    def _validate(self, mode: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            if mode == "review":
                return ReviewResponse.model_validate(payload).model_dump()
            if mode == "test-check":
                return TestCheckResponse.model_validate(payload).model_dump()
            if mode == "test-scenarios":
                return TestScenariosResponse.model_validate(payload).model_dump()
            if mode == "test-gen":
                return TestGenResponse.model_validate(payload).model_dump()
            if mode == "test-maintain":
                return TestMaintainResponse.model_validate(payload).model_dump()
        except ValidationError as exc:
            return {"limitations": [f"Validation fallback: {exc}"]}
        raise ValueError(f"Unsupported mode: {mode}")
