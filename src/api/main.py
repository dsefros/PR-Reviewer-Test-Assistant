import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.responses import JSONResponse
import uvicorn

from src.api.dependencies import build_orchestrator, get_orchestrator
from src.api.readiness import run_readiness_checks
from src.application.orchestrators.analysis_orchestrator import AnalysisOrchestrator
from src.config.models import clear_model_config_cache
from src.config.settings import settings
from src.domain.models.schemas import AnalysisRequest
from src.infrastructure.logging.setup import configure_logging


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    clear_model_config_cache()
    app.state.orchestrator = build_orchestrator()
    logger.info(
        "API startup config: host=%s port=%s runtime_root=%s models_config=%s prompts=%s logs_dir=%s traces=%s results=%s persistence=%s fsync=%s active_model_profile=%s ollama_base_url_override=%s",
        settings.api_host,
        settings.api_port,
        settings.runtime_root,
        settings.models_config_path,
        settings.prompt_templates_path,
        settings.logs_dir,
        settings.traces_jsonl_path,
        settings.results_jsonl_path,
        settings.persistence_enabled,
        settings.jsonl_fsync_enabled,
        settings.active_model_profile or "<models.yaml default>",
        settings.ollama_base_url_override or "<profile value>",
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="PR Reviewer + Test Assistant", version="0.2.0", lifespan=lifespan)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> JSONResponse:
        is_ready, checks = run_readiness_checks()
        payload = {"ready": is_ready, "checks": checks}
        if is_ready:
            return JSONResponse(status_code=status.HTTP_200_OK, content=payload)
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=payload)

    legacy_router = APIRouter()
    api_v1_router = APIRouter(prefix="/api/v1")
    analysis_router = APIRouter(prefix="/analyze")

    @legacy_router.post("/review")
    def review(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
        return orchestrator.run("review", request)

    @legacy_router.post("/test-check")
    def test_check(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
        return orchestrator.run("test-check", request)

    @legacy_router.post("/test-scenarios")
    def test_scenarios(
        request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)
    ) -> dict:
        return orchestrator.run("test-scenarios", request)

    @legacy_router.post("/test-gen")
    def test_gen(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
        return orchestrator.run("test-gen", request)

    @legacy_router.post("/test-maintain")
    def test_maintain(
        request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)
    ) -> dict:
        return orchestrator.run("test-maintain", request)

    @analysis_router.post("/review")
    def review_v1(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
        return orchestrator.run("review", request)

    @analysis_router.post("/test-check")
    def test_check_v1(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
        return orchestrator.run("test-check", request)

    @analysis_router.post("/test-scenarios")
    def test_scenarios_v1(
        request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)
    ) -> dict:
        return orchestrator.run("test-scenarios", request)

    api_v1_router.include_router(analysis_router)
    app.include_router(legacy_router)
    app.include_router(api_v1_router)
    return app


def main() -> None:
    uvicorn.run(
        "src.api.main:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
    )


if __name__ == "__main__":
    main()
