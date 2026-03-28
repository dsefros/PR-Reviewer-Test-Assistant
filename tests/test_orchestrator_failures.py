from __future__ import annotations

from src.application.orchestrators.analysis_orchestrator import AnalysisOrchestrator
from src.domain.models.schemas import AnalysisRequest


class InMemoryRepo:
    def __init__(self):
        self.saved = []

    def save(self, payload):
        self.saved.append(payload)


class TraceFailRepo:
    def save(self, payload):
        raise RuntimeError("trace down")


class ResultFailRepo:
    def save(self, payload):
        raise RuntimeError("result down")


def _run_success(trace_repo, result_repo, monkeypatch):
    orchestrator = AnalysisOrchestrator(trace_repo=trace_repo, result_repo=result_repo)
    from src.infrastructure.llm.adapter import LLMAdapter

    monkeypatch.setattr(LLMAdapter, "generate_json", lambda self, prompt: {"summary": "ok", "confidence": "medium", "limitations": []})
    return orchestrator.run("review", AnalysisRequest(diff="+ return 1;"))


def _run_backend_error(trace_repo, result_repo, monkeypatch):
    orchestrator = AnalysisOrchestrator(trace_repo=trace_repo, result_repo=result_repo)

    class BrokenAdapter:
        def __init__(self, profile, mode):
            raise RuntimeError("init fail")

    monkeypatch.setattr("src.application.orchestrators.analysis_orchestrator.LLMAdapter", BrokenAdapter)
    return orchestrator.run("review", AnalysisRequest(diff="+ return 1;"))


def _run_invalid_mode(trace_repo, result_repo):
    orchestrator = AnalysisOrchestrator(trace_repo=trace_repo, result_repo=result_repo)
    return orchestrator.run("bad-mode", AnalysisRequest(diff="+ return 1;"))


def test_success_partial_persistence_is_symmetric_and_additive(monkeypatch):
    trace_failed = _run_success(TraceFailRepo(), InMemoryRepo(), monkeypatch)
    result_failed = _run_success(InMemoryRepo(), ResultFailRepo(), monkeypatch)

    for response in (trace_failed, result_failed):
        assert "summary" in response
        assert "error" not in response
        assert "persistence_error" in response
        assert "limitations" in response


def test_backend_error_partial_persistence_is_symmetric_and_additive(monkeypatch):
    trace_failed = _run_backend_error(TraceFailRepo(), InMemoryRepo(), monkeypatch)
    result_failed = _run_backend_error(InMemoryRepo(), ResultFailRepo(), monkeypatch)

    for response in (trace_failed, result_failed):
        assert response["error"]["type"] == "backend_error"
        assert "persistence_error" in response


def test_invalid_mode_partial_persistence_is_symmetric_and_additive():
    trace_failed = _run_invalid_mode(TraceFailRepo(), InMemoryRepo())
    result_failed = _run_invalid_mode(InMemoryRepo(), ResultFailRepo())

    for response in (trace_failed, result_failed):
        assert response["error"]["type"] == "invalid_mode"
        assert "persistence_error" in response


def test_no_duplicate_reconciliation_records_on_partial_failures(monkeypatch):
    result_repo = InMemoryRepo()
    _run_success(TraceFailRepo(), result_repo, monkeypatch)
    assert len(result_repo.saved) == 1

    trace_repo = InMemoryRepo()
    _run_success(trace_repo, ResultFailRepo(), monkeypatch)
    assert len(trace_repo.saved) == 1


def test_validation_fallback_preserves_partial_payload(monkeypatch):
    trace_repo = InMemoryRepo()
    result_repo = InMemoryRepo()
    orchestrator = AnalysisOrchestrator(trace_repo=trace_repo, result_repo=result_repo)

    from src.infrastructure.llm.adapter import LLMAdapter

    monkeypatch.setattr(LLMAdapter, "generate_json", lambda self, prompt: {"raw_response": "not-json", "limitations": ["bad-json"]})

    response = orchestrator.run("review", AnalysisRequest(diff="+ return 1;"))

    assert "partial" in response
    assert response["partial"]["raw_response"] == "not-json"
    assert "validation_error" in response
    assert "bad-json" in response["limitations"]
