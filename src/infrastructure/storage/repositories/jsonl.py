from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.infrastructure.storage.repositories.interfaces import ResultRepository, TraceRepository


class _JSONLRepository:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, payload: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(payload, ensure_ascii=False) + "\n")


class JSONLTraceRepository(_JSONLRepository, TraceRepository):
    pass


class JSONLResultRepository(_JSONLRepository, ResultRepository):
    pass
