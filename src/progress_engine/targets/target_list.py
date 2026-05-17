"""Read-only Target State listing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class TargetListError(Exception):
    """Raised when next targets cannot be loaded as minimal valid objects."""


def load_next_targets(root: Path, project_state: dict[str, Any]) -> list[dict[str, Any]]:
    target_ids = project_state["aim_of_next_state"]
    targets_dir = root / ".progress" / "targets"
    targets: list[dict[str, Any]] = []

    for target_id in target_ids:
        if not isinstance(target_id, str) or not target_id:
            raise TargetListError("aim_of_next_state must contain non-empty strings")
        target_path = _find_target_file(targets_dir, target_id)
        targets.append(_load_target(target_path, target_id))

    return targets


def render_target_list(targets: list[dict[str, Any]]) -> str:
    lines = ["Next targets:"]
    if not targets:
        lines.append("- none")
        return "\n".join(lines)

    for target in targets:
        lines.append(
            f"- {target['id']} [{target['primary_dimension']}] "
            f"{target['name']} ({target['status']})"
        )

    return "\n".join(lines)


def _find_target_file(targets_dir: Path, target_id: str) -> Path:
    exact = targets_dir / f"{target_id}.yaml"
    if exact.exists():
        return exact

    matches = sorted(targets_dir.glob(f"{target_id}-*.yaml"))
    if not matches:
        raise TargetListError(f"missing target file for next target: {target_id}")
    if len(matches) > 1:
        raise TargetListError(f"multiple target files found for next target: {target_id}")
    return matches[0]


def _load_target(path: Path, expected_id: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as target_file:
            data = yaml.safe_load(target_file)
    except yaml.YAMLError as exc:
        raise TargetListError(f"target YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise TargetListError(f"target must be a YAML mapping: {path}")

    for key in ("id", "name", "primary_dimension", "status"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise TargetListError(f"target {expected_id} is missing string field: {key}")

    if data["id"] != expected_id:
        raise TargetListError(f"target file id mismatch: expected {expected_id}, got {data['id']}")

    return data
