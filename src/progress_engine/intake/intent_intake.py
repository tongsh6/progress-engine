"""Capture an initial intent artifact into a ProgressEngine project."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


INTENT_ARTIFACT = Path(".progress/artifacts/intent.md")


class IntentIntakeError(Exception):
    """Raised when intent intake cannot be completed."""


def load_project_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise IntentIntakeError("missing Project State file: .progress/state/project_state.yaml")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise IntentIntakeError(f"Project State YAML parse failed: {exc}") from exc
    except OSError as exc:
        raise IntentIntakeError(f"failed to read Project State: {exc}") from exc
    if not isinstance(data, dict):
        raise IntentIntakeError("Project State must be a YAML mapping")
    return data


def capture_intent(root: Path, source: Path) -> Path:
    source_path = source if source.is_absolute() else root / source
    if not source_path.exists():
        raise IntentIntakeError(f"missing intent file: {source}")
    if not source_path.is_file():
        raise IntentIntakeError(f"intent source is not a file: {source}")
    try:
        intent_text = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise IntentIntakeError(f"failed to read intent file: {exc}") from exc
    if not intent_text.strip():
        raise IntentIntakeError("intent file is empty")

    state_path = root / ".progress/state/project_state.yaml"
    state = load_project_state(state_path)

    artifacts_dir = root / ".progress/artifacts"
    artifact_path = root / INTENT_ARTIFACT
    try:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(intent_text, encoding="utf-8")
    except OSError as exc:
        raise IntentIntakeError(f"failed to write intent artifact: {exc}") from exc

    dimensions = state.setdefault("state_dimensions", {})
    if not isinstance(dimensions, dict):
        raise IntentIntakeError("Project State field state_dimensions must be a mapping")
    intent = dimensions.setdefault("intent", {})
    if not isinstance(intent, dict):
        raise IntentIntakeError("Project State intent dimension must be a mapping")
    intent["maturity"] = "seed"
    intent["summary"] = "Initial intent captured in .progress/artifacts/intent.md."
    evidence = intent.setdefault("evidence", [])
    if not isinstance(evidence, list):
        raise IntentIntakeError("Project State intent evidence must be a list")
    artifact_ref = str(INTENT_ARTIFACT)
    if artifact_ref not in evidence:
        evidence.append(artifact_ref)

    try:
        with state_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(state, f, sort_keys=False, allow_unicode=True)
    except OSError as exc:
        raise IntentIntakeError(f"failed to write Project State: {exc}") from exc

    return INTENT_ARTIFACT


def render_intake_success(artifact_path: Path) -> str:
    return "\n".join(
        [
            f"Captured intent: {artifact_path}",
            "Updated Project State intent maturity: seed",
            "Next:",
            "- progress state show",
        ]
    )
