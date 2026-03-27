from __future__ import annotations

import re

MASK_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key\s*[=:]\s*)([^\s'\"]+)") ,
    re.compile(r"(?i)(token\s*[=:]\s*)([^\s'\"]+)") ,
    re.compile(r"(?i)(password\s*[=:]\s*)([^\s'\"]+)") ,
    re.compile(r"(?i)(bearer\s+)([a-z0-9\-._~+/]+=*)"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+PRIVATE KEY-----"),
]


def mask_secrets(text: str) -> tuple[str, int]:
    redactions = 0
    masked = text
    for pattern in MASK_PATTERNS:
        if "PRIVATE KEY" in pattern.pattern:
            masked, count = pattern.subn("[MASKED_PRIVATE_KEY]", masked)
        else:
            masked, count = pattern.subn(r"\1[MASKED]", masked)
        redactions += count
    return masked, redactions
