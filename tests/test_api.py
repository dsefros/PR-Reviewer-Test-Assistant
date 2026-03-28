from fastapi.testclient import TestClient

from src.api.main import create_app
from src.config.models import clear_model_config_cache
from src.config.settings import settings


client = TestClient(create_app())


def _payload(diff: str = "+ return 1;") -> dict:
    return {"diff": diff, "metadata": None, "context": None, "existing_tests": None}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready():
    r = client.get("/ready")
    assert r.status_code == 200
    payload = r.json()
    assert payload["ready"] is True
    assert payload["checks"]["models_config"]["ok"] is True


def test_ready_fails_for_missing_model_profile(monkeypatch):
    original = settings.active_model_profile
    monkeypatch.setattr(settings, "active_model_profile", "missing-profile")
    clear_model_config_cache()
    try:
        r = client.get("/ready")
    finally:
        monkeypatch.setattr(settings, "active_model_profile", original)
        clear_model_config_cache()
    assert r.status_code == 503
    assert r.json()["ready"] is False


def test_review_endpoint_legacy():
    r = client.post("/review", json=_payload("+ if (x) return y;"))
    assert r.status_code == 200
    assert "summary" in r.json()


def test_review_endpoint_v1():
    r = client.post("/api/v1/analyze/review", json=_payload("+ if (x) return y;"))
    assert r.status_code == 200
    assert "summary" in r.json()


def test_test_check_endpoint_v1():
    r = client.post("/api/v1/analyze/test-check", json=_payload())
    assert r.status_code == 200
    assert "test_required" in r.json()


def test_test_scenarios_endpoint_v1():
    r = client.post("/api/v1/analyze/test-scenarios", json=_payload())
    assert r.status_code == 200
    assert "scenarios" in r.json()


def test_invalid_payload_returns_422():
    r = client.post("/api/v1/analyze/review", json={"metadata": {}})
    assert r.status_code == 422
