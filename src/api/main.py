from fastapi import APIRouter, Depends, FastAPI
import uvicorn

from src.api.dependencies import get_orchestrator
from src.application.orchestrators.analysis_orchestrator import AnalysisOrchestrator
from src.domain.models.schemas import AnalysisRequest

app = FastAPI(title="PR Reviewer + Test Assistant", version="0.2.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    return {"ready": True}


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
def test_scenarios(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("test-scenarios", request)


@legacy_router.post("/test-gen")
def test_gen(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("test-gen", request)


@legacy_router.post("/test-maintain")
def test_maintain(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("test-maintain", request)


@analysis_router.post("/review")
def review_v1(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("review", request)


@analysis_router.post("/test-check")
def test_check_v1(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("test-check", request)


@analysis_router.post("/test-scenarios")
def test_scenarios_v1(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("test-scenarios", request)


api_v1_router.include_router(analysis_router)
app.include_router(legacy_router)
app.include_router(api_v1_router)


def main() -> None:
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
