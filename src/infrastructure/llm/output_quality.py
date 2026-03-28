from __future__ import annotations

from typing import Any

VALID_LEVELS = {"low", "medium", "high"}
GENERIC_PHRASES = (
    "improve code quality",
    "add more tests",
    "consider edge cases",
    "follow best practices",
    "could be improved",
    "make it more robust",
)
GENERIC_LIMITATION = "LLM output may be too generic and not fully grounded in the diff."

_DOC_CONFIG_EXTS = (
    ".md",
    ".rst",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".json",
)


def normalize_payload(mode: str, payload: dict[str, Any], prompt: str) -> dict[str, Any]:
    normalized = dict(payload)
    limitations = _ensure_limitations(normalized)

    if mode == "review":
        _normalize_review(normalized, limitations)
    elif mode == "test-check":
        _normalize_test_check(normalized, limitations)
    elif mode == "test-scenarios":
        _normalize_test_scenarios(normalized, limitations, prompt)

    return normalized


def _normalize_review(payload: dict[str, Any], limitations: list[str]) -> None:
    if not isinstance(payload.get("summary"), str) or not payload.get("summary", "").strip():
        payload["summary"] = "No concrete summary provided by model."
        _append_limitation(limitations, "Model returned an empty summary.")

    payload["confidence"] = _normalize_level(payload.get("confidence"), "medium", limitations, "confidence")

    issues = payload.get("issues", [])
    if not isinstance(issues, list):
        payload["issues"] = []
        _append_limitation(limitations, "Model returned non-list issues; normalized to empty list.")
    else:
        normalized_issues = []
        invalid_issue_found = False
        for issue in issues:
            if not isinstance(issue, dict):
                invalid_issue_found = True
                continue
            severity = issue.get("severity")
            description = issue.get("description")
            location = issue.get("location")
            if severity not in VALID_LEVELS:
                invalid_issue_found = True
                continue
            if not isinstance(description, str) or not description.strip():
                invalid_issue_found = True
                continue
            if not isinstance(location, str) or not location.strip():
                invalid_issue_found = True
                continue
            normalized_issues.append(
                {"severity": severity, "description": description.strip(), "location": location.strip()}
            )
        payload["issues"] = normalized_issues
        if invalid_issue_found:
            _append_limitation(limitations, "Model returned invalid issue entries; kept only schema-compatible issues.")

    if _looks_generic(payload):
        _append_limitation(limitations, GENERIC_LIMITATION)


def _normalize_test_check(payload: dict[str, Any], limitations: list[str]) -> None:
    if not isinstance(payload.get("test_required"), bool):
        payload["test_required"] = bool(payload.get("test_required"))
        _append_limitation(limitations, "Model returned non-boolean test_required; coerced to boolean.")

    payload["priority"] = _normalize_level(payload.get("priority"), "medium", limitations, "priority")
    payload["confidence"] = _normalize_level(payload.get("confidence"), "medium", limitations, "confidence")

    why = _normalize_string_list(payload.get("why"))
    payload["why"] = why
    if payload["test_required"] and not why:
        payload["why"] = ["Model did not provide concrete changed-behavior rationale for required tests."]
        _append_limitation(limitations, "test_required=true but why was empty or invalid.")


def _normalize_test_scenarios(payload: dict[str, Any], limitations: list[str], prompt: str) -> None:
    scenarios = payload.get("scenarios", [])
    normalized_scenarios: list[dict[str, str]] = []
    invalid_scenarios_found = False

    if isinstance(scenarios, list):
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                invalid_scenarios_found = True
                continue
            name = scenario.get("name")
            description = scenario.get("description")
            priority = scenario.get("priority")
            if not isinstance(name, str) or not name.strip():
                invalid_scenarios_found = True
                continue
            if not isinstance(description, str) or not description.strip():
                invalid_scenarios_found = True
                continue
            if priority not in VALID_LEVELS:
                invalid_scenarios_found = True
                continue
            normalized_scenarios.append(
                {
                    "name": name.strip(),
                    "description": description.strip(),
                    "priority": priority,
                }
            )
    else:
        invalid_scenarios_found = True

    payload["scenarios"] = normalized_scenarios
    if invalid_scenarios_found:
        _append_limitation(limitations, "Model returned invalid scenarios; kept only schema-compatible scenarios.")

    if not normalized_scenarios and _prompt_diff_suggests_runtime_change(prompt):
        _append_limitation(limitations, "No scenarios returned despite changed runtime behavior in diff.")


def _normalize_level(value: Any, default: str, limitations: list[str], field_name: str) -> str:
    if value in VALID_LEVELS:
        return value
    _append_limitation(limitations, f"Model returned invalid {field_name}; defaulted to {default}.")
    return default


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _ensure_limitations(payload: dict[str, Any]) -> list[str]:
    limitations = payload.get("limitations")
    if not isinstance(limitations, list):
        payload["limitations"] = []
        return payload["limitations"]
    payload["limitations"] = [item for item in limitations if isinstance(item, str) and item.strip()]
    return payload["limitations"]


def _append_limitation(limitations: list[str], message: str) -> None:
    if message not in limitations:
        limitations.append(message)


def _looks_generic(payload: dict[str, Any]) -> bool:
    text_parts: list[str] = []
    for key in ("summary",):
        value = payload.get(key)
        if isinstance(value, str):
            text_parts.append(value.lower())

    for key in ("recommendations", "risks"):
        values = payload.get(key)
        if isinstance(values, list):
            text_parts.extend(v.lower() for v in values if isinstance(v, str))

    issues = payload.get("issues")
    if isinstance(issues, list):
        for issue in issues:
            if isinstance(issue, dict) and isinstance(issue.get("description"), str):
                text_parts.append(issue["description"].lower())

    full_text = " ".join(text_parts)
    if not full_text.strip():
        return False
    return any(phrase in full_text for phrase in GENERIC_PHRASES)


def _prompt_diff_suggests_runtime_change(prompt: str) -> bool:
    if "Diff:" not in prompt:
        return False

    diff = prompt.split("Diff:", maxsplit=1)[1]
    changed_files: set[str] = set()
    runtime_signal = False

    for raw_line in diff.splitlines():
        line = raw_line.strip()
        if raw_line.startswith("+++ b/") or raw_line.startswith("--- a/"):
            changed_files.add(raw_line.split("/", maxsplit=1)[1])
            continue

        if not (raw_line.startswith("+") or raw_line.startswith("-")):
            continue
        if raw_line.startswith("+++") or raw_line.startswith("---"):
            continue

        candidate = raw_line[1:].strip().lower()
        if not candidate or candidate.startswith("#") or candidate.startswith("//"):
            continue

        if any(token in candidate for token in ("if ", "if(", "elif", "else:", "raise ", "return ", "try:", "except", "validate", "parse", "json.loads", "state", "error")):
            runtime_signal = True
            break

    docs_only_files = bool(changed_files) and all(path.endswith(_DOC_CONFIG_EXTS) for path in changed_files)
    return runtime_signal and not docs_only_files
