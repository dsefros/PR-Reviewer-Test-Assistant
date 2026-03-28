import json

from src.config.models import MockModelProfile
from src.infrastructure.llm.adapter import LLMAdapter


def _adapter(mode: str) -> LLMAdapter:
    profile = MockModelProfile(name="mock-default", backend="mock", model_name="mock-v1")
    return LLMAdapter(profile=profile, mode=mode)


def test_review_generic_but_valid_output_adds_grounding_limitation(monkeypatch):
    adapter = _adapter("review")
    weak_payload = {
        "summary": "This change could be improved by following best practices.",
        "strengths": [],
        "issues": [],
        "risks": ["Consider edge cases."],
        "recommendations": ["Add more tests."],
        "confidence": "medium",
        "limitations": [],
    }
    monkeypatch.setattr(adapter, "generate", lambda prompt: json.dumps(weak_payload))

    payload = adapter.generate_json("Diff:\n+ return parsed")

    assert "limitations" in payload
    assert any("too generic" in item for item in payload["limitations"])


def test_review_docs_only_payload_stays_low_signal(monkeypatch):
    adapter = _adapter("review")
    docs_payload = {
        "summary": "Diff is documentation only.",
        "strengths": ["No runtime changes."],
        "issues": [],
        "risks": [],
        "recommendations": [],
        "confidence": "high",
        "limitations": [],
    }
    monkeypatch.setattr(adapter, "generate", lambda prompt: json.dumps(docs_payload))

    payload = adapter.generate_json("Diff:\n+++ b/README.md\n+ Clarify docs")

    assert payload["issues"] == []
    assert payload["recommendations"] == []
    assert payload["confidence"] == "high"


def test_test_check_requires_concrete_why_when_required(monkeypatch):
    adapter = _adapter("test-check")
    weak_payload = {
        "test_required": True,
        "why": [],
        "missing_scenarios": ["check edge cases"],
        "priority": "high",
        "confidence": "medium",
        "limitations": [],
    }
    monkeypatch.setattr(adapter, "generate", lambda prompt: json.dumps(weak_payload))

    payload = adapter.generate_json("Diff:\n+ if timeout <= 0:\n+     raise ValueError('bad timeout')")

    assert payload["test_required"] is True
    assert payload["why"]
    assert any("test_required=true" in item for item in payload["limitations"])


def test_test_scenarios_empty_for_runtime_diff_adds_limitation(monkeypatch):
    adapter = _adapter("test-scenarios")
    weak_payload = {
        "scenarios": [],
        "coverage_gaps": [],
        "limitations": [],
    }
    prompt = """Metadata: {}\nContext: {}\nExisting tests: {}\n\nDiff:\n+++ b/src/parser.py\n@@\n+ if timeout <= 0:\n+     raise ValueError('timeout must be positive')\n"""
    monkeypatch.setattr(adapter, "generate", lambda p: json.dumps(weak_payload))

    payload = adapter.generate_json(prompt)

    assert payload["scenarios"] == []
    assert any("No scenarios returned" in item for item in payload["limitations"])
