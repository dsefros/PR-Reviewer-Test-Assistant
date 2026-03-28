from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def _payload(diff: str = "+ return 1;") -> dict:
    return {"diff": diff, "metadata": None, "context": None, "existing_tests": None}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


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
