import pytest

from src.config.models import clear_model_config_cache
from src.config.settings import settings


@pytest.fixture(autouse=True)
def isolate_test_runtime_env(monkeypatch):
    """Keep tests hermetic from developer .env/shell runtime values."""
    monkeypatch.setattr(settings, "active_model_profile", None)
    monkeypatch.setenv("ACTIVE_MODEL_PROFILE", "mock-default")
    monkeypatch.setenv("MODELS_CONFIG_PATH", "models.yaml")
    monkeypatch.setenv("RUNTIME_ROOT", ".")
    monkeypatch.setenv("PROMPT_TEMPLATES_PATH", "src/infrastructure/prompts/templates")
    monkeypatch.setenv("LOGS_DIR", "logs")
    monkeypatch.setenv("TRACES_JSONL_PATH", "logs/traces.jsonl")
    monkeypatch.setenv("RESULTS_JSONL_PATH", "logs/results.jsonl")
    monkeypatch.setenv("OLLAMA_BASE_URL_OVERRIDE", "")
    clear_model_config_cache()
    yield
    clear_model_config_cache()
