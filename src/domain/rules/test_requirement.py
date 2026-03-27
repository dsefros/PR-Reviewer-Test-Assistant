from __future__ import annotations

from dataclasses import dataclass

BEHAVIORAL_KEYWORDS = [
    "if ",
    "else",
    "switch",
    "case",
    "return",
    "throw",
    "catch",
    "validate",
    "parser",
    "calculate",
    "public",
    "endpoint",
]
NON_BEHAVIORAL_KEYWORDS = ["//", "#", "/*", "*", "logger", "log.", "println", "fmt."]


@dataclass
class RuleCheckResult:
    test_required: bool
    why: list[str]
    missing_scenarios: list[str]
    priority: str


def evaluate_test_requirement(diff: str) -> RuleCheckResult:
    lowered = diff.lower()
    added_lines = [line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]

    behavioral_hits = [k for k in BEHAVIORAL_KEYWORDS if k in lowered]
    non_behavioral_only = bool(added_lines) and all(any(tok in ln.lower() for tok in NON_BEHAVIORAL_KEYWORDS) for ln in added_lines)

    if non_behavioral_only and not behavioral_hits:
        return RuleCheckResult(
            test_required=False,
            why=["Diff appears non-behavioral (comments/logging/docs/formatting)."],
            missing_scenarios=[],
            priority="low",
        )

    if behavioral_hits:
        scenarios = [
            "Verify happy path behavior remains correct.",
            "Add negative-path assertions for new/changed branches.",
            "Add regression test covering changed logic path.",
        ]
        return RuleCheckResult(
            test_required=True,
            why=[f"Behavioral indicators detected: {', '.join(sorted(set(behavioral_hits)))}."],
            missing_scenarios=scenarios,
            priority="high",
        )

    return RuleCheckResult(
        test_required=True,
        why=["Unable to prove change is purely mechanical; test coverage is recommended."],
        missing_scenarios=["Add at least one smoke or regression scenario around touched code."],
        priority="medium",
    )
