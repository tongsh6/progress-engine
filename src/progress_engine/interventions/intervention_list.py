"""Read-only Intervention listing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class InterventionListError(Exception):
    """Raised when interventions cannot be loaded as minimal valid objects."""


def load_active_interventions(root: Path) -> list[dict[str, Any]]:
    interventions_dir = root / ".progress" / "interventions"
    if not interventions_dir.is_dir():
        raise InterventionListError(f"missing interventions directory: {interventions_dir}")

    interventions = [_load_intervention(path) for path in sorted(interventions_dir.glob("*.yaml"))]
    return [intervention for intervention in interventions if intervention["status"] != "completed"]


def render_intervention_list(interventions: list[dict[str, Any]]) -> str:
    lines = ["Interventions:"]
    if not interventions:
        lines.append("- none")
        return "\n".join(lines)

    for intervention in interventions:
        lines.append(
            f"- {intervention['id']} [{intervention['primary_dimension']}] "
            f"{intervention['name']} ({intervention['status']})"
        )

    return "\n".join(lines)


def _load_intervention(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as intervention_file:
            data = yaml.safe_load(intervention_file)
    except yaml.YAMLError as exc:
        raise InterventionListError(f"intervention YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise InterventionListError(f"intervention must be a YAML mapping: {path}")

    intervention_id = data.get("id")
    for key in ("id", "name", "primary_dimension", "target_state_id", "status"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise InterventionListError(
                f"intervention {intervention_id or path.name} is missing string field: {key}"
            )

    if not path.name.startswith(data["id"]):
        raise InterventionListError(
            f"intervention filename must start with id {data['id']}: {path.name}"
        )

    return data
