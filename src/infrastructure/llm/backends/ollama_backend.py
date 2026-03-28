from __future__ import annotations

import httpx

from src.infrastructure.llm.backends.base import LLMBackend


class OllamaBackend(LLMBackend):
    def __init__(self, base_url: str, model_name: str, temperature: float = 0.1):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.temperature = temperature
        self.client = httpx.Client(timeout=60)

    def generate(self, prompt: str) -> str:
        response = self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": self.temperature,
                },
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("response", "")

    def close(self) -> None:
        self.client.close()
