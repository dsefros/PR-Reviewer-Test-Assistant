from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TraceRepository(ABC):
    @abstractmethod
    def save(self, payload: dict[str, Any]) -> None:
        raise NotImplementedError


class ResultRepository(ABC):
    @abstractmethod
    def save(self, payload: dict[str, Any]) -> None:
        raise NotImplementedError
