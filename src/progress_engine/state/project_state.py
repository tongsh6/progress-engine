"""Project State loading and rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ProjectStateError(Exception):
    """Raised when Project State cannot be read as a valid minimal object."""


def load_project_state(root: Path) -> dict[str, Any]:
    state_path = root / ".progress" / "state" / "project_state.yaml"
    if not state_path.exists():
        raise ProjectStateError(f"missing Project State file: {state_path}")

    try:
        with state_path.open("r", encoding="utf-8") as state_file:
            data = yaml.safe_load(state_file)
    except yaml.YAMLError as exc:
        raise ProjectStateError(f"Project State YAML parse failed: {exc}") from exc

    if not isinstance(data, dict):
        raise ProjectStateError("Project State must be a YAML mapping")

    _require_mapping(data, "project")
    _require_mapping(data, "state_dimensions")
    _require_list(data, "open_state_gaps")
    _require_list(data, "aim_of_next_state")

    project = data["project"]
    _require_string(project, "project", "id")
    _require_string(project, "project", "current_phase")

    dimensions = data["state_dimensions"]
    for name, dimension in dimensions.items():
        if not isinstance(name, str) or not isinstance(dimension, dict):
            raise ProjectStateError("state_dimensions must map names to mappings")
        _require_string(dimension, f"state dimension '{name}'", "maturity")

    return data


def write_project_state(root: Path, state: dict[str, Any]) -> None:
    state_path = root / ".progress" / "state" / "project_state.yaml"
    with state_path.open("w", encoding="utf-8") as state_file:
        yaml.safe_dump(state, state_file, sort_keys=False, allow_unicode=True)


def render_state_summary(state: dict[str, Any]) -> str:
    project = state["project"]
    dimensions = state["state_dimensions"]
    open_gaps = state["open_state_gaps"]
    next_targets = state["aim_of_next_state"]

    lines = [
        f"Project: {project.get('id', 'unknown')}",
        f"Phase: {project.get('current_phase', 'unknown')}",
        "Dimensions:",
    ]

    for name, dimension in dimensions.items():
        lines.append(f"- {name}: {dimension['maturity']}")

    lines.append("Open gaps:")
    if open_gaps:
        lines.extend(f"- {gap}" for gap in open_gaps)
    else:
        lines.append("- none")

    lines.append("Next target:")
    if next_targets:
        lines.extend(f"- {target}" for target in next_targets)
    else:
        lines.append("- none")

    return "\n".join(lines)


def _require_mapping(data: dict[str, Any], key: str) -> None:
    if not isinstance(data.get(key), dict):
        raise ProjectStateError(f"Project State missing mapping field: {key}")


def _require_list(data: dict[str, Any], key: str) -> None:
    if not isinstance(data.get(key), list):
        raise ProjectStateError(f"Project State missing list field: {key}")


def _require_string(data: dict[str, Any], owner: str, key: str) -> None:
    if not isinstance(data.get(key), str) or not data[key]:
        raise ProjectStateError(f"{owner} is missing string field: {key}")
