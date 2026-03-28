from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

from src.infrastructure.storage.repositories.interfaces import ResultRepository, TraceRepository


class _JSONLRepository:
    def __init__(self, path: str, fsync_enabled: bool = True, enabled: bool = True):
        self.path = Path(path)
        self.fsync_enabled = fsync_enabled
        self.enabled = enabled
        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def save(self, payload: dict[str, Any]) -> None:
        if not self.enabled:
            return
        line = json.dumps(payload, ensure_ascii=False) + "\n"
        with self._lock:
            with self.path.open("a", encoding="utf-8") as fp:
                fp.write(line)
                fp.flush()
                if self.fsync_enabled:
                    os.fsync(fp.fileno())


class JSONLTraceRepository(_JSONLRepository, TraceRepository):
    pass


class JSONLResultRepository(_JSONLRepository, ResultRepository):
    pass
