from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProcessedDiff:
    normalized_diff: str
    limitations: list[str]
    dropped_lines: int


class DiffProcessor:
    def __init__(self, max_bytes: int, max_lines: int, max_files: int):
        self.max_bytes = max_bytes
        self.max_lines = max_lines
        self.max_files = max_files

    def process(self, diff: str) -> ProcessedDiff:
        limitations: list[str] = []
        lines = diff.splitlines()
        dropped = 0

        file_markers = [ln for ln in lines if ln.startswith("diff --git")]
        if len(file_markers) > self.max_files:
            limitations.append(f"Changed files exceeded limit ({self.max_files}); diff truncated by file count.")
            keep_files = 0
            kept_lines: list[str] = []
            for ln in lines:
                if ln.startswith("diff --git"):
                    keep_files += 1
                if keep_files <= self.max_files:
                    kept_lines.append(ln)
            dropped += len(lines) - len(kept_lines)
            lines = kept_lines

        if len(lines) > self.max_lines:
            limitations.append(f"Diff lines exceeded limit ({self.max_lines}); trailing hunks dropped.")
            dropped += len(lines) - self.max_lines
            lines = lines[: self.max_lines]

        joined = "\n".join(lines)
        if len(joined.encode("utf-8")) > self.max_bytes:
            limitations.append(f"Diff bytes exceeded limit ({self.max_bytes}); payload truncated.")
            encoded = joined.encode("utf-8")[: self.max_bytes]
            joined = encoded.decode("utf-8", errors="ignore")

        return ProcessedDiff(normalized_diff=joined, limitations=limitations, dropped_lines=dropped)
