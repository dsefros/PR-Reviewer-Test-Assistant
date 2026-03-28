from __future__ import annotations

from pathlib import Path


class PromptRenderer:
    _template_cache: dict[Path, str] = {}

    def __init__(self, templates_path: str):
        self.templates_path = Path(templates_path)

    def _load_template(self, mode: str) -> str:
        template_path = self.templates_path / f"{mode}.txt"
        if template_path not in self._template_cache:
            self._template_cache[template_path] = template_path.read_text(encoding="utf-8")
        return self._template_cache[template_path]

    def render(self, mode: str, diff: str, metadata: dict | None, context: dict | None, existing_tests: dict | None) -> str:
        template = self._load_template(mode)
        return template.format(
            diff=diff,
            metadata=metadata or {},
            context=context or {},
            existing_tests=existing_tests or {},
        )
