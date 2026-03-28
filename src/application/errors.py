from __future__ import annotations


class AnalysisError(Exception):
    error_type = "analysis_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidModeError(AnalysisError):
    error_type = "invalid_mode"


class ConfigLoadError(AnalysisError):
    error_type = "config_error"


class BackendInvocationError(AnalysisError):
    error_type = "backend_error"


class PersistenceError(AnalysisError):
    error_type = "persistence_error"
