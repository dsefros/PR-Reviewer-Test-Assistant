from __future__ import annotations

from pathlib import Path


class PromptRenderer:
    def __init__(self, templates_path: str):
        self.templates_path = Path(templates_path)

    def render(self, mode: str, diff: str, metadata: dict | None, context: dict | None, existing_tests: dict | None) -> str:
        template = (self.templates_path / f"{mode}.txt").read_text(encoding="utf-8")
        return template.format(
            diff=diff,
            metadata=metadata or {},
            context=context or {},
            existing_tests=existing_tests or {},
        )
