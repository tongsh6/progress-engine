"""Prompt-only Run start support."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from progress_engine.capsule.context_capsule import (
    ContextCapsuleError,
    ensure_context_capsule,
    load_context_capsule_context,
)


class RunStartError(Exception):
    """Raised when a prompt-only Run cannot be started."""


def start_run(root: Path, intervention_id: str, mode: str) -> dict[str, str]:
    if mode != "prompt-only":
        raise RunStartError(f"unsupported run mode: {mode}")
    if not intervention_id.startswith("IV-"):
        raise RunStartError(f"Intervention id must start with IV-: {intervention_id}")

    try:
        context = load_context_capsule_context(root, intervention_id)
    except ContextCapsuleError as exc:
        raise RunStartError(str(exc)) from exc

    intervention = context["intervention"]
    target = context["target"]
    _reject_duplicate_active_run(root, intervention_id)

    started_at = datetime.now().astimezone().isoformat(timespec="seconds")
    run_id = _next_run_id(root, intervention_id, started_at)
    run_path = root / ".progress" / "runs" / f"{run_id}.yaml"
    if run_path.exists():
        raise RunStartError(f"Run output path already exists: {run_path.relative_to(root)}")

    try:
        capsule = ensure_context_capsule(root, intervention_id)
    except ContextCapsuleError as exc:
        raise RunStartError(str(exc)) from exc

    run = {
        "id": run_id,
        "intervention_id": intervention_id,
        "target_state_id": intervention["target_state_id"],
        "started_at": started_at,
        "mode": mode,
        "primary_dimension": intervention["primary_dimension"],
        "status": "active",
        "context_capsule": capsule["capsule"],
        "execution_session": {
            "fresh_context": True,
            "transcript_carried_forward": False,
            "mode": mode,
        },
        "outputs": {
            "expected_evidence": intervention.get("evidence_required", []),
        },
    }

    run_path.parent.mkdir(parents=True, exist_ok=True)
    with run_path.open("w", encoding="utf-8") as run_file:
        yaml.safe_dump(run, run_file, sort_keys=False, allow_unicode=True)

    return {
        "run": run_id,
        "intervention": intervention_id,
        "target": target["id"],
        "mode": mode,
        "capsule": capsule["capsule"],
        "run_file": str(run_path.relative_to(root)),
    }


def render_run_start_success(result: dict[str, str]) -> str:
    lines = [
        "Run started:",
        f"- run: {result['run']}",
        f"- intervention: {result['intervention']}",
        f"- target: {result['target']}",
        f"- mode: {result['mode']}",
        f"- capsule: {result['capsule']}",
        f"- run file: {result['run_file']}",
        "",
        "Next:",
        "- Open the capsule in an AI tool or hand it to a human executor.",
        "- Record evidence after execution.",
    ]
    return "\n".join(lines)


def _reject_duplicate_active_run(root: Path, intervention_id: str) -> None:
    runs_dir = root / ".progress" / "runs"
    if not runs_dir.is_dir():
        raise RunStartError(f"missing runs directory: {runs_dir}")

    for path in sorted(runs_dir.glob("*.yaml")):
        run = _load_run(path)
        if (
            run.get("intervention_id") == intervention_id
            and run.get("status") in {"active", "planned"}
        ):
            raise RunStartError(
                f"intervention {intervention_id} already has an active or planned Run: "
                f"{run.get('id')}"
            )


def _next_run_id(root: Path, intervention_id: str, started_at: str) -> str:
    date_part = started_at[:10].replace("-", "")
    base = f"RUN-{date_part}-{intervention_id}"
    runs_dir = root / ".progress" / "runs"
    if not (runs_dir / f"{base}.yaml").exists():
        return base

    suffix = 2
    while (runs_dir / f"{base}-{suffix}.yaml").exists():
        suffix += 1
    return f"{base}-{suffix}"


def _load_run(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as run_file:
            data = yaml.safe_load(run_file)
    except yaml.YAMLError as exc:
        raise RunStartError(f"run YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise RunStartError(f"run must be a YAML mapping: {path}")
    return data
