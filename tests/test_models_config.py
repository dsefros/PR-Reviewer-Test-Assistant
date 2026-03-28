from pathlib import Path

import pytest

from src.config.models import clear_model_config_cache, load_model_config


def test_load_model_config(tmp_path, monkeypatch):
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
    monkeypatch.setenv("MODELS_CONFIG_PATH", str(p))
    monkeypatch.setenv("ACTIVE_MODEL_PROFILE", "mock-default")
    _, profile = load_model_config(str(p))
    assert profile.backend == "mock"


def test_invalid_profile_raises(tmp_path):
    clear_model_config_cache()
    p = tmp_path / "models.yaml"
    p.write_text("default_model: x\nprofiles: {}")
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
