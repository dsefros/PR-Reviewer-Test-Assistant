from __future__ import annotations

import json
from dataclasses import dataclass

from src.config.models import ModelProfileBase
from src.infrastructure.llm.backends.base import LLMBackend
from src.infrastructure.llm.output_quality import normalize_payload


@dataclass
class LLMMetadata:
    profile_name: str
    backend: str
    model_name: str


class LLMAdapter:
    def __init__(self, profile: ModelProfileBase, mode: str):
        self.profile = profile
        self.mode = mode
        self._backend: LLMBackend | None = None

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            profile_name=self.profile.name,
            backend=self.profile.backend,
            model_name=self.profile.model_name,
        )

    def _init_backend(self) -> LLMBackend:
        if self._backend:
            return self._backend
        cfg = self.profile.to_backend_config()
        backend = cfg["backend"]

        if backend == "mock":
            from src.infrastructure.llm.backends.mock_backend import MockBackend

            self._backend = MockBackend(mode=self.mode)
        elif backend == "ollama":
            from src.infrastructure.llm.backends.ollama_backend import OllamaBackend

            self._backend = OllamaBackend(
                base_url=cfg["base_url"],
                model_name=cfg["model_name"],
                temperature=cfg.get("temperature", 0.1),
            )
        elif backend == "llama_cpp":
            from src.infrastructure.llm.backends.llama_cpp_backend import LlamaCppBackend

            self._backend = LlamaCppBackend(
                model_path=cfg["model_path"],
                temperature=cfg.get("temperature", 0.1),
                n_ctx=cfg.get("n_ctx", 4096),
                max_tokens=cfg.get("max_tokens", 1500),
            )
        else:
            raise ValueError(f"Unsupported backend: {backend}")

        return self._backend

    def generate(self, prompt: str) -> str:
        return self._init_backend().generate(prompt)

    def generate_json(self, prompt: str) -> dict:
        raw = self.generate(prompt)
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return normalize_payload(mode=self.mode, payload=parsed, prompt=prompt)
            return {"raw_response": raw, "limitations": ["Model output JSON root was not an object."]}
        except json.JSONDecodeError:
            return {"raw_response": raw, "limitations": ["Model output was not valid JSON."]}

    def close(self) -> None:
        if self._backend:
            self._backend.close()
