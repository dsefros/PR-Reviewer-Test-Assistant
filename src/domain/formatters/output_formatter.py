from __future__ import annotations

import json
from typing import Any


def _render_list(items: list[Any]) -> list[str]:
    if not items:
        return ["- (none)"]

    lines: list[str] = []
    for item in items:
        if isinstance(item, dict):
            if {"severity", "description", "location"} <= set(item.keys()):
                lines.append(f'- [{str(item["severity"]).upper()}] {item["description"]} ({item["location"]})')
            elif {"name", "description", "priority"} <= set(item.keys()):
                lines.append(f'- [{str(item["priority"]).upper()}] {item["name"]}: {item["description"]}')
            else:
                lines.append(f"- {json.dumps(item, ensure_ascii=False)}")
        else:
            lines.append(f"- {item}")
    return lines


def _generic_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    for key, value in payload.items():
        title = key.replace("_", " ").title()
        lines.append(f"## {title}")
        if isinstance(value, list):
            if not value:
                lines.append("- (none)")
            else:
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"- {json.dumps(item, ensure_ascii=False)}")
                    else:
                        lines.append(f"- {item}")
        elif isinstance(value, dict):
            lines.append("```json")
            lines.append(json.dumps(value, indent=2, ensure_ascii=False))
            lines.append("```")
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines).strip()


def format_output(payload: dict[str, Any], as_json: bool) -> str:
    if as_json:
        return json.dumps(payload, indent=2, ensure_ascii=False)

    if "summary" in payload:
        lines: list[str] = []

        lines.append("=== SUMMARY ===")
        lines.append(str(payload.get("summary", "")))
        lines.append("")

        lines.append("=== STRENGTHS ===")
        lines.extend(_render_list(payload.get("strengths", [])))
        lines.append("")

        lines.append("=== ISSUES ===")
        lines.extend(_render_list(payload.get("issues", [])))
        lines.append("")

        lines.append("=== RISKS ===")
        lines.extend(_render_list(payload.get("risks", [])))
        lines.append("")

        lines.append("=== RECOMMENDATIONS ===")
        lines.extend(_render_list(payload.get("recommendations", [])))
        lines.append("")

        lines.append("=== CONFIDENCE ===")
        lines.append(str(payload.get("confidence", "")))
        lines.append("")

        lines.append("=== LIMITATIONS ===")
        lines.extend(_render_list(payload.get("limitations", [])))

        return "\n".join(lines).strip()

    if "test_required" in payload:
        lines: list[str] = []

        required = "YES" if payload.get("test_required") else "NO"
        priority = str(payload.get("priority", "")).lower()

        lines.append("=== TEST REQUIRED ===")
        lines.append(f"{required} ({priority} priority)")
        lines.append("")

        lines.append("=== WHY ===")
        lines.extend(_render_list(payload.get("why", [])))
        lines.append("")

        lines.append("=== MISSING SCENARIOS ===")
        lines.extend(_render_list(payload.get("missing_scenarios", [])))
        lines.append("")

        lines.append("=== CONFIDENCE ===")
        lines.append(str(payload.get("confidence", "")))
        lines.append("")

        lines.append("=== LIMITATIONS ===")
        lines.extend(_render_list(payload.get("limitations", [])))

        return "\n".join(lines).strip()

    if "scenarios" in payload:
        lines: list[str] = []

        lines.append("=== SCENARIOS ===")
        lines.extend(_render_list(payload.get("scenarios", [])))
        lines.append("")

        lines.append("=== COVERAGE GAPS ===")
        lines.extend(_render_list(payload.get("coverage_gaps", [])))
        lines.append("")

        lines.append("=== LIMITATIONS ===")
        lines.extend(_render_list(payload.get("limitations", [])))

        return "\n".join(lines).strip()

    return _generic_markdown(payload)
