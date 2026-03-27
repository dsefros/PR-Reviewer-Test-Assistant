from __future__ import annotations

from src.infrastructure.llm.backends.base import LLMBackend


class LlamaCppBackend(LLMBackend):
    def __init__(self, model_path: str, temperature: float = 0.1, n_ctx: int = 4096, max_tokens: int = 1500):
        self.model_path = model_path
        self.temperature = temperature
        self.n_ctx = n_ctx
        self.max_tokens = max_tokens
        self._llm = None

    def _ensure_loaded(self) -> None:
        if self._llm is not None:
            return
        from llama_cpp import Llama  # lazy import

        self._llm = Llama(model_path=self.model_path, n_ctx=self.n_ctx)

    def generate(self, prompt: str) -> str:
        self._ensure_loaded()
        output = self._llm.create_completion(prompt=prompt, max_tokens=self.max_tokens, temperature=self.temperature)
        return output["choices"][0]["text"]
