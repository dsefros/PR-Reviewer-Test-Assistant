import json

from src.infrastructure.storage.repositories.jsonl import JSONLResultRepository


def test_jsonl_repository_writes_records(tmp_path):
    path = tmp_path / "results.jsonl"
    repo = JSONLResultRepository(str(path))
    repo.save({"ok": True})
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["ok"] is True
