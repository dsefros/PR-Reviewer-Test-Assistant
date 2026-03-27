from fastapi import Depends, FastAPI

from src.api.dependencies import get_orchestrator
from src.application.orchestrators.analysis_orchestrator import AnalysisOrchestrator
from src.domain.models.schemas import AnalysisRequest

app = FastAPI(title="PR Reviewer + Test Assistant", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    return {"ready": True}


@app.post("/review")
def review(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("review", request)


@app.post("/test-check")
def test_check(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("test-check", request)


@app.post("/test-scenarios")
def test_scenarios(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("test-scenarios", request)


@app.post("/test-gen")
def test_gen(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("test-gen", request)


@app.post("/test-maintain")
def test_maintain(request: AnalysisRequest, orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)) -> dict:
    return orchestrator.run("test-maintain", request)
