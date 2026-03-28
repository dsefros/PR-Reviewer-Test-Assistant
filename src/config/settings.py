from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    request_timeout_seconds: int = 45
    max_diff_bytes: int = 300_000
    max_diff_lines: int = 5_000
    max_changed_files: int = 50
    secret_masking_enabled: bool = True
    runtime_root: str = "."
    models_config_path: str = "models.yaml"
    prompt_templates_path: str = "src/infrastructure/prompts/templates"
    logs_dir: str = "logs"
    traces_jsonl_path: str = "logs/traces.jsonl"
    results_jsonl_path: str = "logs/results.jsonl"
    persistence_enabled: bool = True
    jsonl_fsync_enabled: bool = True
    active_model_profile: str | None = None
    ollama_base_url_override: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @model_validator(mode="after")
    def normalize_paths(self) -> "Settings":
        runtime_root = Path(self.runtime_root).resolve()
        self.runtime_root = str(runtime_root)

        self.models_config_path = str(self._resolve_path(self.models_config_path))
        self.prompt_templates_path = str(self._resolve_path(self.prompt_templates_path))
        self.logs_dir = str(self._resolve_path(self.logs_dir))
        self.traces_jsonl_path = str(self._resolve_path(self.traces_jsonl_path))
        self.results_jsonl_path = str(self._resolve_path(self.results_jsonl_path))
        return self

    def _resolve_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return Path(self.runtime_root) / path


settings = Settings()
