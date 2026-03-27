import json

from typer.testing import CliRunner

from src.cli.main import app


runner = CliRunner()


def test_cli_review_json_from_file(tmp_path):
    diff = tmp_path / "a.patch"
    diff.write_text("+ if (x) return y;\n")
    result = runner.invoke(app, ["review", "--diff", str(diff), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "summary" in payload


def test_cli_test_check_output_json_flag(tmp_path):
    diff = tmp_path / "a.patch"
    diff.write_text("+ return 1;\n")
    result = runner.invoke(app, ["test-check", "--diff", str(diff), "--output", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "test_required" in payload
