import pytest

from src.config.models import clear_model_config_cache, load_model_config


def test_uses_default_model_when_active_profile_unset(tmp_path, monkeypatch):
    clear_model_config_cache()
    p = tmp_path / "models.yaml"
    p.write_text(
        """
default_model: mock-default
profiles:
  mock-default:
    backend: mock
    model_name: mock-v1
""".strip()
    )
    monkeypatch.delenv("ACTIVE_MODEL_PROFILE", raising=False)

    cfg, profile = load_model_config(str(p))

    assert cfg.default_model == "mock-default"
    assert profile.name == "mock-default"
    assert profile.backend == "mock"


def test_uses_active_model_profile_override(tmp_path, monkeypatch):
    clear_model_config_cache()
    p = tmp_path / "models.yaml"
    p.write_text(
        """
default_model: mock-default
profiles:
  mock-default:
    backend: mock
    model_name: mock-v1
  ollama-local-llama3:
    backend: ollama
    model_name: llama3
""".strip()
    )
    monkeypatch.setenv("ACTIVE_MODEL_PROFILE", "mock-default")

    _, profile = load_model_config(str(p))

    assert profile.name == "mock-default"
    assert profile.backend == "mock"


def test_uses_ollama_profile_override(tmp_path, monkeypatch):
    clear_model_config_cache()
    p = tmp_path / "models.yaml"
    p.write_text(
        """
default_model: mock-default
profiles:
  mock-default:
    backend: mock
    model_name: mock-v1
  ollama-local-llama3:
    backend: ollama
    model_name: llama3
""".strip()
    )
    monkeypatch.setenv("ACTIVE_MODEL_PROFILE", "ollama-local-llama3")

    _, profile = load_model_config(str(p))

    assert profile.name == "ollama-local-llama3"
    assert profile.backend == "ollama"


def test_invalid_profile_raises(tmp_path, monkeypatch):
    clear_model_config_cache()
    p = tmp_path / "models.yaml"
    p.write_text("default_model: x\nprofiles: {}")
    monkeypatch.setenv("ACTIVE_MODEL_PROFILE", "missing-profile")
    with pytest.raises(ValueError):
        load_model_config(str(p))


def test_model_config_cache_can_be_cleared(tmp_path, monkeypatch):
    p = tmp_path / "models.yaml"
    p.write_text(
        """
default_model: mock-default
profiles:
  mock-default:
    backend: mock
    model_name: mock-v1
""".strip()
    )
    monkeypatch.setenv("ACTIVE_MODEL_PROFILE", "mock-default")
    clear_model_config_cache()
    _, profile = load_model_config(str(p))
    assert profile.model_name == "mock-v1"

    p.write_text(
        """
default_model: mock-default
profiles:
  mock-default:
    backend: mock
    model_name: mock-v2
""".strip()
    )
    _, still_cached = load_model_config(str(p))
    assert still_cached.model_name == "mock-v1"

    clear_model_config_cache()
    _, refreshed = load_model_config(str(p))
    assert refreshed.model_name == "mock-v2"


def test_ollama_base_url_override_from_settings(tmp_path, monkeypatch):
    from src.config.settings import settings

    clear_model_config_cache()
    p = tmp_path / "models.yaml"
    p.write_text(
        """
default_model: ollama-default
profiles:
  ollama-default:
    backend: ollama
    model_name: llama3
    base_url: http://127.0.0.1:11434
""".strip()
    )
    monkeypatch.setattr(settings, "ollama_base_url_override", "http://ollama.internal:11434")
    monkeypatch.setattr(settings, "active_model_profile", None)
    monkeypatch.delenv("ACTIVE_MODEL_PROFILE", raising=False)
    try:
        _, profile = load_model_config(str(p))
    finally:
        monkeypatch.setattr(settings, "ollama_base_url_override", None)
    assert profile.backend == "ollama"
    assert profile.base_url == "http://ollama.internal:11434"
