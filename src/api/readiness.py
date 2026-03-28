from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from src.config.models import load_model_config
from src.config.settings import settings


def _check_prompts(path: str) -> dict[str, Any]:
    prompt_dir = Path(path)
    if not prompt_dir.exists() or not prompt_dir.is_dir():
        return {"ok": False, "error": f"Prompt templates directory not found: {prompt_dir}"}
    if not any(prompt_dir.glob("*.txt")):
        return {"ok": False, "error": f"No prompt templates found in: {prompt_dir}"}
    return {"ok": True}


def _check_persistence() -> dict[str, Any]:
    if not settings.persistence_enabled:
        return {"ok": True, "enabled": False}

    targets = [Path(settings.traces_jsonl_path), Path(settings.results_jsonl_path)]
    checked_paths: list[str] = []
    for target in targets:
        parent = target.parent
        checked_paths.append(str(target))
        try:
            parent.mkdir(parents=True, exist_ok=True)
            probe = parent / ".write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
        except Exception as exc:
            return {
                "ok": False,
                "error": f"Cannot write to persistence target parent dir {parent} for {target}: {exc}",
            }

    return {"ok": True, "enabled": True, "targets": checked_paths}


def _check_ollama(base_url: str) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=2) as client:
            response = client.get(f"{base_url.rstrip('/')}/api/version")
            response.raise_for_status()
    except Exception as exc:
        return {"ok": False, "error": f"Ollama connectivity failed: {exc}"}
    return {"ok": True}


def _check_llama_cpp(model_path: str) -> dict[str, Any]:
    model = Path(model_path)
    if not model.exists():
        return {"ok": False, "error": f"llama.cpp model file not found: {model}"}
    if not model.is_file():
        return {"ok": False, "error": f"llama.cpp model path is not a file: {model}"}

    try:
        # Validate runtime dependency import without loading full model.
        __import__("llama_cpp")
    except Exception as exc:
        return {"ok": False, "error": f"llama.cpp runtime unavailable: {exc}"}

    return {"ok": True}


def run_readiness_checks() -> tuple[bool, dict[str, Any]]:
    checks: dict[str, Any] = {}
    ready = True

    try:
        _, profile = load_model_config()
        checks["models_config"] = {"ok": True, "active_profile": profile.name, "backend": profile.backend}
    except Exception as exc:
        checks["models_config"] = {"ok": False, "error": str(exc)}
        return False, checks

    checks["prompts"] = _check_prompts(settings.prompt_templates_path)
    checks["persistence"] = _check_persistence()

    if profile.backend == "mock":
        checks["backend"] = {"ok": True, "backend": "mock"}
    elif profile.backend == "ollama":
        checks["backend"] = {
            "backend": "ollama",
            **_check_ollama(profile.base_url),
        }
    elif profile.backend == "llama_cpp":
        checks["backend"] = {
            "backend": "llama_cpp",
            **_check_llama_cpp(profile.model_path),
        }

    for value in checks.values():
        if isinstance(value, dict) and value.get("ok") is False:
            ready = False
            break

    return ready, checks
