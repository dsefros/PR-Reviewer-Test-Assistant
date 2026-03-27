from src.application.orchestrators.analysis_orchestrator import AnalysisOrchestrator
from src.config.settings import settings
from src.infrastructure.storage.repositories.jsonl import JSONLResultRepository, JSONLTraceRepository


_trace_repo = JSONLTraceRepository(settings.traces_jsonl_path)
_result_repo = JSONLResultRepository(settings.results_jsonl_path)
_orchestrator = AnalysisOrchestrator(trace_repo=_trace_repo, result_repo=_result_repo)


def get_orchestrator() -> AnalysisOrchestrator:
    return _orchestrator
