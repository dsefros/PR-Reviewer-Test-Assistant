from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    request_timeout_seconds: int = 45
    max_diff_bytes: int = 300_000
    max_diff_lines: int = 5_000
    max_changed_files: int = 50
    secret_masking_enabled: bool = True
    models_config_path: str = "models.yaml"
    active_model_profile: str | None = None
    model_backend: str | None = None
    prompt_templates_path: str = "src/infrastructure/prompts/templates"
    logs_dir: str = "logs"
    traces_jsonl_path: str = "logs/traces.jsonl"
    results_jsonl_path: str = "logs/results.jsonl"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
