"""Read-only State Gap listing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from progress_engine.state.references import find_referenced_object_file


class GapListError(Exception):
    """Raised when open gaps cannot be loaded as minimal valid objects."""


def load_open_gaps(root: Path, project_state: dict[str, Any]) -> list[dict[str, Any]]:
    gap_ids = project_state["open_state_gaps"]
    gaps_dir = root / ".progress" / "gaps"
    gaps: list[dict[str, Any]] = []

    for gap_id in gap_ids:
        if not isinstance(gap_id, str) or not gap_id:
            raise GapListError("open_state_gaps must contain non-empty strings")
        gap_path = _find_gap_file(gaps_dir, gap_id)
        gaps.append(_load_gap(gap_path, gap_id))

    return gaps


def render_gap_list(gaps: list[dict[str, Any]]) -> str:
    lines = ["Open gaps:"]
    if not gaps:
        lines.append("- none")
        return "\n".join(lines)

    for gap in gaps:
        summary = _single_line(gap["desired_state"])
        lines.append(f"- {gap['id']} [{gap['dimension']}] {summary}")

    return "\n".join(lines)


def _find_gap_file(gaps_dir: Path, gap_id: str) -> Path:
    matches = find_referenced_object_file(gaps_dir, gap_id)
    if not matches:
        raise GapListError(f"missing gap file for open gap: {gap_id}")
    if len(matches) > 1:
        raise GapListError(f"multiple gap files found for open gap: {gap_id}")
    return matches[0]


def _load_gap(path: Path, expected_id: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as gap_file:
            data = yaml.safe_load(gap_file)
    except yaml.YAMLError as exc:
        raise GapListError(f"gap YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise GapListError(f"gap must be a YAML mapping: {path}")

    for key in ("id", "dimension", "status", "desired_state"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise GapListError(f"gap {expected_id} is missing string field: {key}")

    if data["id"] != expected_id:
        raise GapListError(f"gap file id mismatch: expected {expected_id}, got {data['id']}")

    return data


def _single_line(value: str) -> str:
    return " ".join(value.split())
