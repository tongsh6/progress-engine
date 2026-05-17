"""Read-only Run listing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class RunListError(Exception):
    """Raised when runs cannot be loaded as minimal valid objects."""


def load_active_runs(root: Path) -> list[dict[str, Any]]:
    runs_dir = root / ".progress" / "runs"
    if not runs_dir.is_dir():
        raise RunListError(f"missing runs directory: {runs_dir}")

    runs = [_load_run(path) for path in sorted(runs_dir.glob("*.yaml"))]
    return [run for run in runs if run["status"] not in {"completed", "abandoned"}]


def render_run_list(runs: list[dict[str, Any]]) -> str:
    lines = ["Runs:"]
    if not runs:
        lines.append("- none")
        return "\n".join(lines)

    for run in runs:
        lines.append(
            f"- {run['id']} [{run['primary_dimension']}] "
            f"{run['intervention_id']} -> {run['target_state_id']} ({run['status']})"
        )

    return "\n".join(lines)


def _load_run(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as run_file:
            data = yaml.safe_load(run_file)
    except yaml.YAMLError as exc:
        raise RunListError(f"run YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise RunListError(f"run must be a YAML mapping: {path}")

    run_id = data.get("id")
    for key in ("id", "intervention_id", "target_state_id", "primary_dimension", "status"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise RunListError(f"run {run_id or path.name} is missing string field: {key}")

    if not path.name.startswith(data["id"]):
        raise RunListError(f"run filename must start with id {data['id']}: {path.name}")

    return data
