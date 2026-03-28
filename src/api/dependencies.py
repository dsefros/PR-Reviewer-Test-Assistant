from fastapi import Request

from src.application.orchestrators.analysis_orchestrator import AnalysisOrchestrator
from src.config.settings import settings
from src.infrastructure.storage.repositories.jsonl import JSONLResultRepository, JSONLTraceRepository


def build_orchestrator() -> AnalysisOrchestrator:
    return AnalysisOrchestrator(
        trace_repo=JSONLTraceRepository(
            settings.traces_jsonl_path,
            fsync_enabled=settings.jsonl_fsync_enabled,
            enabled=settings.persistence_enabled,
        ),
        result_repo=JSONLResultRepository(
            settings.results_jsonl_path,
            fsync_enabled=settings.jsonl_fsync_enabled,
            enabled=settings.persistence_enabled,
        ),
    )


def get_orchestrator(request: Request) -> AnalysisOrchestrator:
    orchestrator: AnalysisOrchestrator | None = getattr(request.app.state, "orchestrator", None)
    if orchestrator is None:
        orchestrator = build_orchestrator()
        request.app.state.orchestrator = orchestrator
    return orchestrator
