from __future__ import annotations

import json

from src.infrastructure.llm.backends.base import LLMBackend


class MockBackend(LLMBackend):
    def __init__(self, mode: str):
        self.mode = mode

    def generate(self, prompt: str) -> str:
        if self.mode == "review":
            payload = {
                "summary": "Changed code updates parsing behavior.",
                "strengths": ["Logic is more explicit."],
                "issues": [
                    {
                        "severity": "medium",
                        "description": "Behavior changed for null input.",
                        "location": "parser.py:10-14",
                    }
                ],
                "risks": ["Existing callers may rely on previous behavior."],
                "recommendations": ["Add tests for null and whitespace handling."],
                "confidence": "medium",
                "limitations": ["Mock backend response."],
            }
        elif self.mode == "test-check":
            payload = {
                "test_required": True,
                "why": ["Behavior for null and trimmed input changed."],
                "missing_scenarios": [
                    "Null input returns fallback value.",
                    "Whitespace is stripped before parsing.",
                ],
                "priority": "high",
                "confidence": "high",
                "limitations": ["Mock backend response."],
            }
        elif self.mode == "test-scenarios":
            payload = {
                "scenarios": [
                    {
                        "name": "Valid input parsing",
                        "description": "Parser returns integer for valid numeric string.",
                        "priority": "high",
                    },
                    {
                        "name": "Null input handling",
                        "description": "Parser returns fallback value for null input.",
                        "priority": "high",
                    },
                ],
                "coverage_gaps": ["Non-integer input handling is not covered."],
                "limitations": ["Mock backend response."],
            }
        elif self.mode == "test-gen":
            payload = {
                "generated_tests": "// mock generated tests",
                "assumptions": ["Mock backend response."],
                "limitations": ["Mock backend response."],
            }
        else:
            payload = {
                "tests_to_review": ["UserServiceTest"],
                "assertions_to_update": ["Expect new error code"],
                "mocks_to_update": ["Repository mock now invoked with flags"],
                "priority_files": ["src/test/..."],
                "limitations": ["Mock backend response."],
            }

        return json.dumps(payload)

    def close(self) -> None:
        return None
