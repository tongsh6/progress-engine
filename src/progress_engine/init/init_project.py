"""Create the minimal ProgressEngine project skeleton."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
PROGRESS_DIRS = [
    "state",
    "artifacts",
    "gaps",
    "targets",
    "interventions",
    "runs",
    "evidence",
    "deltas",
    "events",
    "context_capsules",
    "ledger",
]
DIMENSIONS = [
    "intent",
    "product",
    "design",
    "architecture",
    "implementation",
    "quality",
    "delivery",
    "knowledge",
]


class InitProjectError(Exception):
    """Raised when a project cannot be initialized."""


def validate_project_id(project_id: str) -> None:
    if not project_id:
        raise InitProjectError("project id must be a non-empty string")
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise InitProjectError(
            "project id may only contain letters, numbers, dots, underscores, and hyphens"
        )


def build_initial_project_state(project_id: str) -> dict[str, Any]:
    return {
        "project": {
            "id": project_id,
            "name": project_id,
            "repository": None,
            "current_phase": "initialized",
            "operating_principle": "持续推进项目状态，而不是持续完成任务。",
        },
        "state_dimensions": {
            dimension: {
                "maturity": "unknown",
                "summary": "Not assessed yet.",
                "evidence": [],
            }
            for dimension in DIMENSIONS
        },
        "open_state_gaps": [],
        "aim_of_next_state": [],
    }


def init_project(root: Path, project_id: str) -> list[Path]:
    validate_project_id(project_id)

    progress_dir = root / ".progress"
    if progress_dir.exists():
        raise InitProjectError(".progress already exists; refusing to overwrite existing state")

    created: list[Path] = []
    try:
        for directory in PROGRESS_DIRS:
            path = progress_dir / directory
            path.mkdir(parents=True, exist_ok=False)
            created.append(path)

        readme = progress_dir / "README.md"
        readme.write_text(
            f"# ProgressEngine State\n\nProject: `{project_id}`\n",
            encoding="utf-8",
        )
        created.append(readme)

        state_path = progress_dir / "state" / "project_state.yaml"
        with state_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                build_initial_project_state(project_id),
                f,
                sort_keys=False,
                allow_unicode=True,
            )
        created.append(state_path)

        history_path = progress_dir / "state" / "state_history.jsonl"
        history_path.write_text("", encoding="utf-8")
        created.append(history_path)
    except OSError as exc:
        raise InitProjectError(f"failed to initialize .progress: {exc}") from exc

    return created


def render_init_success(project_id: str, created: list[Path], root: Path) -> str:
    rendered_paths = [
        path.relative_to(root)
        for path in created
        if path.name in {"README.md", "project_state.yaml", "state_history.jsonl"}
    ]
    lines = [f"Initialized ProgressEngine project: {project_id}", "Created:"]
    lines.extend(f"- {path}" for path in rendered_paths)
    lines.extend(["Next:", "- progress state show"])
    return "\n".join(lines)
