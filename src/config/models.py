from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

from src.config.settings import settings


class ModelProfileBase(BaseModel):
    name: str
    backend: Literal["mock", "ollama", "llama_cpp"]
    model_name: str
    temperature: float = 0.1
    max_tokens: int = 1500

    def to_backend_config(self) -> dict:
        return self.model_dump()


class MockModelProfile(ModelProfileBase):
    backend: Literal["mock"]


class OllamaModelProfile(ModelProfileBase):
    backend: Literal["ollama"]
    base_url: str = "http://localhost:11434"


class LlamaCppModelProfile(ModelProfileBase):
    backend: Literal["llama_cpp"]
    model_path: str
    n_ctx: int = 4096


class ModelConfig(BaseModel):
    default_model: str
    profiles: dict[str, dict]


def _parse_profile(name: str, data: dict) -> ModelProfileBase:
    backend = data.get("backend")
    if backend == "mock":
        return MockModelProfile(name=name, **data)
    if backend == "ollama":
        return OllamaModelProfile(name=name, **data)
    if backend == "llama_cpp":
        return LlamaCppModelProfile(name=name, **data)
    raise ValueError(f"Unsupported backend: {backend}")


@lru_cache(maxsize=4)
def _load_model_config_cached(config_path: str) -> ModelConfig:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as fp:
        raw = yaml.safe_load(fp) or {}
    return ModelConfig(**raw)


def clear_model_config_cache() -> None:
    _load_model_config_cached.cache_clear()


def load_model_config(path: str | None = None) -> tuple[ModelConfig, ModelProfileBase]:
    config_path = str(Path(path or settings.models_config_path).resolve())
    cfg = _load_model_config_cached(config_path)

    active = settings.active_model_profile or os.getenv("ACTIVE_MODEL_PROFILE") or cfg.default_model

    if active not in cfg.profiles:
        raise ValueError(f"Active model profile '{active}' not found in models config")

    profile_data = dict(cfg.profiles[active])
    if profile_data.get("backend") == "ollama" and settings.ollama_base_url_override:
        profile_data["base_url"] = settings.ollama_base_url_override
    profile = _parse_profile(active, profile_data)
    return cfg, profile
