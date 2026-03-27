from pathlib import Path

import pytest

from src.config.models import load_model_config


def test_load_model_config(tmp_path, monkeypatch):
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
    p = tmp_path / "models.yaml"
    p.write_text("default_model: x\nprofiles: {}")
    with pytest.raises(ValueError):
        load_model_config(str(p))
