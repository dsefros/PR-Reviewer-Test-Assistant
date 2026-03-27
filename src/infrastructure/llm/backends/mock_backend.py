from __future__ import annotations

import json

from src.infrastructure.llm.backends.base import LLMBackend


class MockBackend(LLMBackend):
    def __init__(self, mode: str = "review"):
        self.mode = mode

    def generate(self, prompt: str) -> str:
        if self.mode == "review":
            return json.dumps(
                {
                    "summary": "Mock review summary.",
                    "strengths": ["Structure is clear."],
                    "issues": [],
                    "risks": ["Potential uncovered logic branches."],
                    "recommendations": ["Add tests for changed branches."],
                    "limitations": ["Mock backend response."],
                }
            )
        if self.mode == "test-check":
            return json.dumps(
                {
                    "test_required": True,
                    "why": ["Behavioral logic changed."],
                    "missing_scenarios": ["Negative path for parser failures."],
                    "priority": "high",
                    "limitations": ["Mock backend response."],
                }
            )
        if self.mode == "test-scenarios":
            return json.dumps(
                {
                    "happy_path": ["Valid input returns expected output."],
                    "negative": ["Invalid input returns error."],
                    "edge_cases": ["Boundary values and null input."],
                    "regression": ["Prior bug reproduction case."],
                    "limitations": ["Mock backend response."],
                }
            )
        if self.mode == "test-gen":
            return json.dumps(
                {
                    "generated_tests": "// Mock generated test draft",
                    "assumptions": ["JUnit5 is available."],
                    "limitations": ["Mock backend response."],
                }
            )
        return json.dumps(
            {
                "tests_to_review": ["UserServiceTest"],
                "assertions_to_update": ["Expect new error code"],
                "mocks_to_update": ["Repository mock now invoked with flags"],
                "priority_files": ["src/test/..."],
                "limitations": ["Mock backend response."],
            }
        )
