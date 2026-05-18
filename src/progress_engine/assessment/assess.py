"""Read-only project assessment summary."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from progress_engine.gaps.gap_list import load_open_gaps
from progress_engine.state.project_state import load_project_state
from progress_engine.targets.target_list import load_next_targets


def load_assessment(root: Path) -> dict[str, Any]:
    state = load_project_state(root)
    return {
        "state": state,
        "gaps": load_open_gaps(root, state),
        "targets": load_next_targets(root, state),
    }


def render_assessment(assessment: dict[str, Any]) -> str:
    state = assessment["state"]
    gaps = assessment["gaps"]
    targets = assessment["targets"]
    project = state["project"]
    dimensions = state["state_dimensions"]

    lines = [
        "Assessment:",
        f"Project: {project.get('id', 'unknown')}",
        f"Phase: {project.get('current_phase', 'unknown')}",
        "",
        "Maturity:",
    ]

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

    lines.extend(["", "Next:", "- progress target list", "- progress intervention list"])
    return "\n".join(lines)


def _single_line(value: str) -> str:
    return " ".join(value.split())
