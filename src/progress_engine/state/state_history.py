"""Read-only State History listing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StateHistoryError(Exception):
    """Raised when state history cannot be loaded as minimal valid entries."""


def load_state_history(root: Path) -> list[dict[str, Any]]:
    history_path = root / ".progress" / "state" / "state_history.jsonl"
    if not history_path.exists():
        raise StateHistoryError(f"missing State History file: {history_path}")

    entries: list[dict[str, Any]] = []
    with history_path.open("r", encoding="utf-8") as history_file:
        for line_number, line in enumerate(history_file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                entry = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise StateHistoryError(
                    f"State History JSONL parse failed at line {line_number}: {exc}"
                ) from exc
            if not isinstance(entry, dict):
                raise StateHistoryError(
                    f"State History entry at line {line_number} must be a JSON object"
                )
            _validate_entry(entry, line_number)
            entries.append(entry)

    return entries


def render_state_history(entries: list[dict[str, Any]]) -> str:
    lines = ["State history:"]
    if not entries:
        lines.append("- none")
        return "\n".join(lines)

    for entry in entries:
        lines.append(
            f"- {entry['state_version']} <- {entry['applied_delta']} "
            f"by {entry['applied_by']} at {entry['applied_at']}"
        )

    return "\n".join(lines)


def _validate_entry(entry: dict[str, Any], line_number: int) -> None:
    for key in ("state_version", "applied_delta", "applied_at", "applied_by", "summary"):
        if not isinstance(entry.get(key), str) or not entry[key]:
            raise StateHistoryError(
                f"State History entry at line {line_number} is missing string field: {key}"
            )
