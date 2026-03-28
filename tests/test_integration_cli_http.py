import json

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from src.api.main import create_app
from src.cli.main import app as cli_app


runner = CliRunner()


def test_cli_http_to_api_mock(monkeypatch, tmp_path):
    client = TestClient(create_app())
    diff = tmp_path / "change.patch"
    diff.write_text("+ return calculate_total(items)\n")

    class BridgeResponse:
        def __init__(self, response):
            self.status_code = response.status_code
            self._response = response

        def json(self):
            return self._response.json()

    def _post(url, json, timeout):
        path = url.replace("http://review-server", "")
        return BridgeResponse(client.post(path, json=json))

    monkeypatch.setattr("httpx.post", _post)

    result = runner.invoke(
        cli_app,
        [
            "review",
            "--transport",
            "http",
            "--server-url",
            "http://review-server",
            "--diff",
            str(diff),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "summary" in payload
    assert "limitations" in payload
