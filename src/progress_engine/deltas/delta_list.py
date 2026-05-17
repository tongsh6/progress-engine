"""Read-only State Delta Proposal listing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class DeltaListError(Exception):
    """Raised when state delta proposals cannot be loaded as minimal valid objects."""


def load_deltas(root: Path) -> list[dict[str, Any]]:
    deltas_dir = root / ".progress" / "deltas"
    if not deltas_dir.is_dir():
        raise DeltaListError(f"missing deltas directory: {deltas_dir}")

    return [_load_delta(path) for path in sorted(deltas_dir.glob("*.yaml"))]


def render_delta_list(deltas: list[dict[str, Any]]) -> str:
    lines = ["State delta proposals:"]
    if not deltas:
        lines.append("- none")
        return "\n".join(lines)

    for delta in deltas:
        summary = delta["acceptance_summary"]
        lines.append(
            f"- {delta['id']} [{delta['primary_dimension']}] "
            f"{delta['source_intervention']} -> {delta['target_state_id']} "
            f"({delta['status']}; acceptance: {summary['pass']} pass, "
            f"{summary['fail']} fail, {summary['not_tested']} not_tested)"
        )

    return "\n".join(lines)


def _load_delta(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as delta_file:
            data = yaml.safe_load(delta_file)
    except yaml.YAMLError as exc:
        raise DeltaListError(f"state delta YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise DeltaListError(f"state delta file must be a YAML mapping: {path}")

    delta = data.get("state_delta_proposal")
    if not isinstance(delta, dict):
        raise DeltaListError(
            f"state delta file is missing root mapping 'state_delta_proposal': {path}"
        )

    delta_id = delta.get("id")
    for key in ("id", "source_intervention", "target_state_id", "primary_dimension", "status"):
        if not isinstance(delta.get(key), str) or not delta[key]:
            raise DeltaListError(
                f"state delta {delta_id or path.name} is missing string field: {key}"
            )

    summary = delta.get("acceptance_summary")
    if not isinstance(summary, dict):
        raise DeltaListError(
            f"state delta {delta_id or path.name} is missing mapping field: acceptance_summary"
        )
    for key in ("pass", "fail", "not_tested"):
        if not isinstance(summary.get(key), int):
            raise DeltaListError(
                f"state delta {delta_id or path.name} is missing integer field: "
                f"acceptance_summary.{key}"
            )

    if not path.name.startswith(delta["id"]):
        raise DeltaListError(
            f"state delta filename must start with id {delta['id']}: {path.name}"
        )

    return delta
