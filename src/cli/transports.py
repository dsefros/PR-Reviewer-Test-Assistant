from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from src.application.orchestrators.analysis_orchestrator import AnalysisOrchestrator
from src.config.settings import settings
from src.domain.models.schemas import AnalysisRequest
from src.infrastructure.storage.repositories.jsonl import JSONLResultRepository, JSONLTraceRepository


class TransportError(RuntimeError):
    """Base transport failure for user-facing CLI errors."""


class MissingServerURLError(TransportError):
    pass


class ServerConnectionError(TransportError):
    pass


class ServerHTTPError(TransportError):
    pass


class InvalidResponseError(TransportError):
    pass


class BaseTransport(ABC):
    @abstractmethod
    def send(self, mode: str, request: AnalysisRequest) -> dict[str, Any]:
        raise NotImplementedError


class LocalTransport(BaseTransport):
    def __init__(self) -> None:
        self.orchestrator = AnalysisOrchestrator(
            trace_repo=JSONLTraceRepository(
                settings.traces_jsonl_path,
                fsync_enabled=settings.jsonl_fsync_enabled,
                enabled=settings.persistence_enabled,
            ),
            result_repo=JSONLResultRepository(
                settings.results_jsonl_path,
                fsync_enabled=settings.jsonl_fsync_enabled,
                enabled=settings.persistence_enabled,
            ),
        )

    def send(self, mode: str, request: AnalysisRequest) -> dict[str, Any]:
        return self.orchestrator.run(mode, request)


class HTTPTransport(BaseTransport):
    API_V1_ENDPOINTS = {
        "review": "/api/v1/analyze/review",
        "test-check": "/api/v1/analyze/test-check",
        "test-scenarios": "/api/v1/analyze/test-scenarios",
    }

    def __init__(self, server_url: str | None, timeout: int | None = None) -> None:
        if not server_url:
            raise MissingServerURLError("HTTP transport requires --server-url")
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout or settings.request_timeout_seconds

    def _endpoint_for(self, mode: str) -> str:
        if mode in self.API_V1_ENDPOINTS:
            return self.API_V1_ENDPOINTS[mode]
        return f"/{mode}"

    def send(self, mode: str, request: AnalysisRequest) -> dict[str, Any]:
        endpoint = self._endpoint_for(mode)
        url = f"{self.server_url}{endpoint}"
        payload = request.model_dump()
        try:
            response = httpx.post(url, json=payload, timeout=self.timeout)
        except httpx.RequestError as exc:
            raise ServerConnectionError(f"Failed to connect to review server at {self.server_url}") from exc

        if response.status_code != 200:
            raise ServerHTTPError(f"Review server returned HTTP {response.status_code}")

        try:
            body = response.json()
        except ValueError as exc:
            raise InvalidResponseError("Invalid response payload from server") from exc

        if not isinstance(body, dict):
            raise InvalidResponseError("Invalid response payload from server")
        return body


def build_transport(transport: str, server_url: str | None) -> BaseTransport:
    if transport == "http":
        return HTTPTransport(server_url=server_url)
    if transport == "local":
        return LocalTransport()
    raise TransportError("Invalid transport. Allowed values: http, local")
