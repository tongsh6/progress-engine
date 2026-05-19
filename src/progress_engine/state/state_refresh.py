"""Read-only State refresh reconciliation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from progress_engine.gaps.gap_list import load_open_gaps
from progress_engine.state.project_state import load_project_state
from progress_engine.state.state_history import load_state_history
from progress_engine.targets.target_list import load_next_targets


class StateRefreshError(Exception):
    """Raised when state refresh inputs are inconsistent."""


def load_state_refresh(root: Path, after_delta: str | None = None) -> dict[str, Any]:
    if after_delta is not None and not after_delta.startswith("SDP-"):
        raise StateRefreshError(f"--after-delta must start with SDP-: {after_delta}")

    state = load_project_state(root)
    history = load_state_history(root)
    latest = history[-1] if history else None
    if after_delta is not None:
        _validate_requested_delta(history, latest, after_delta)

    return {
        "state": state,
        "latest": latest,
        "requested_delta": after_delta,
        "gaps": load_open_gaps(root, state),
        "targets": load_next_targets(root, state),
    }


def render_state_refresh(refresh: dict[str, Any]) -> str:
    state = refresh["state"]
    latest = refresh["latest"]
    gaps = refresh["gaps"]
    targets = refresh["targets"]
    project = state["project"]
    dimensions = state["state_dimensions"]

    latest_state = latest["state_version"] if latest else "none"
    latest_delta = latest["applied_delta"] if latest else "none"

    lines = [
        "State refresh:",
        f"- project: {project.get('id', 'unknown')}",
        f"- phase: {project.get('current_phase', 'unknown')}",
        f"- latest state: {latest_state}",
        f"- latest delta: {latest_delta}",
    ]

    requested_delta = refresh["requested_delta"]
    if requested_delta is not None:
        lines.append(f"- requested delta: {requested_delta} (matched)")

    lines.extend(["", "Maturity:"])
    for name, dimension in dimensions.items():
        lines.append(f"- {name}: {dimension['maturity']}")

    lines.extend(["", "Open gaps:"])
    if gaps:
        for gap in gaps:
            lines.append(
                f"- {gap['id']} [{gap['dimension']}] {_single_line(gap['desired_state'])}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "Next targets:"])
    if targets:
        for target in targets:
            lines.append(f"- {target['id']} [{target['primary_dimension']}] {target['name']}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "Next:",
            "- progress gaps list",
            "- progress target list",
            "- progress intervention list",
        ]
    )
    return "\n".join(lines)


def _validate_requested_delta(
    history: list[dict[str, Any]],
    latest: dict[str, Any] | None,
    after_delta: str,
) -> None:
    if latest is None:
        raise StateRefreshError(f"cannot match --after-delta without State History: {after_delta}")

    if latest["applied_delta"] == after_delta:
        return

    if any(entry["applied_delta"] == after_delta for entry in history):
        raise StateRefreshError(
            f"State Delta {after_delta} is not latest applied delta: "
            f"latest is {latest['applied_delta']}"
        )

    raise StateRefreshError(f"State Delta {after_delta} not found in State History")


def _single_line(value: str) -> str:
    return " ".join(value.split())
