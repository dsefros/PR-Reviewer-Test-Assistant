from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_review_endpoint():
    r = client.post("/review", json={"diff": "+ if (x) return y;", "metadata": None, "context": None, "existing_tests": None})
    assert r.status_code == 200
    assert "summary" in r.json()


def test_test_check_endpoint():
    r = client.post("/test-check", json={"diff": "+ return 1;", "metadata": None, "context": None, "existing_tests": None})
    assert r.status_code == 200
    assert "test_required" in r.json()
