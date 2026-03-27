from __future__ import annotations

import json
from typing import Any


def format_output(payload: dict[str, Any], as_json: bool) -> str:
    if as_json:
        return json.dumps(payload, indent=2)

    lines: list[str] = []
    for key, value in payload.items():
        title = key.replace("_", " ").title()
        lines.append(f"## {title}")
        if isinstance(value, list):
            if not value:
                lines.append("- (none)")
            else:
                for item in value:
                    lines.append(f"- {item}")
        elif isinstance(value, dict):
            lines.append("```json")
            lines.append(json.dumps(value, indent=2))
            lines.append("```")
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines).strip()
