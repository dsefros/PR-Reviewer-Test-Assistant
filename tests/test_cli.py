import json

from typer.testing import CliRunner

from src.cli.main import app


runner = CliRunner()


class DummyResponse:
    def __init__(self, status_code: int = 200, payload=None, raise_json: bool = False):
        self.status_code = status_code
        self._payload = payload if payload is not None else {"summary": "ok", "confidence": "medium", "limitations": []}
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            raise ValueError("bad json")
        return self._payload


def test_cli_review_json_local_mode_from_file(tmp_path):
    diff = tmp_path / "a.patch"
    diff.write_text("+ if (x) return y;\n")
    result = runner.invoke(app, ["review", "--transport", "local", "--diff", str(diff), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "summary" in payload


def test_cli_review_http_mode(monkeypatch, tmp_path):
    diff = tmp_path / "a.patch"
    diff.write_text("+ if (x) return y;\n")

    def _post(url, json, timeout):
        assert url.endswith("/api/v1/analyze/review")
        return DummyResponse(payload={"summary": "remote", "confidence": "high", "limitations": []})

    monkeypatch.setattr("httpx.post", _post)
    result = runner.invoke(
        app,
        ["review", "--transport", "http", "--server-url", "http://localhost:8000", "--diff", str(diff), "--json"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["summary"] == "remote"


def test_cli_http_missing_server_url(tmp_path):
    diff = tmp_path / "a.patch"
    diff.write_text("+ return 1;\n")
    result = runner.invoke(app, ["review", "--transport", "http", "--diff", str(diff)])
    assert result.exit_code != 0
    assert "HTTP transport requires --server-url" in result.stderr


def test_cli_http_connection_failure(monkeypatch, tmp_path):
    import httpx

    diff = tmp_path / "a.patch"
    diff.write_text("+ return 1;\n")

    def _post(url, json, timeout):
        raise httpx.ConnectError("down")

    monkeypatch.setattr("httpx.post", _post)
    result = runner.invoke(app, ["review", "--transport", "http", "--server-url", "http://localhost:8000", "--diff", str(diff)])
    assert result.exit_code != 0
    assert "Failed to connect to review server" in result.stderr


def test_cli_http_non_200(monkeypatch, tmp_path):
    diff = tmp_path / "a.patch"
    diff.write_text("+ return 1;\n")

    monkeypatch.setattr("httpx.post", lambda url, json, timeout: DummyResponse(status_code=500))
    result = runner.invoke(app, ["review", "--transport", "http", "--server-url", "http://localhost:8000", "--diff", str(diff)])
    assert result.exit_code != 0
    assert "Review server returned HTTP 500" in result.stderr


def test_cli_http_invalid_json(monkeypatch, tmp_path):
    diff = tmp_path / "a.patch"
    diff.write_text("+ return 1;\n")

    monkeypatch.setattr("httpx.post", lambda url, json, timeout: DummyResponse(raise_json=True))
    result = runner.invoke(app, ["review", "--transport", "http", "--server-url", "http://localhost:8000", "--diff", str(diff)])
    assert result.exit_code != 0
    assert "Invalid response payload from server" in result.stderr


def test_cli_rejects_invalid_transport_value(tmp_path):
    diff = tmp_path / "a.patch"
    diff.write_text("+ return 1;\n")
    result = runner.invoke(app, ["review", "--transport", "grpc", "--diff", str(diff)])
    assert result.exit_code != 0
    assert "Invalid value for '--transport'" in result.stderr
