"""Read-only Evidence listing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class EvidenceListError(Exception):
    """Raised when evidence cannot be loaded as minimal valid objects."""


def load_evidence(root: Path) -> list[dict[str, Any]]:
    evidence_dir = root / ".progress" / "evidence"
    if not evidence_dir.is_dir():
        raise EvidenceListError(f"missing evidence directory: {evidence_dir}")

    return [_load_evidence_file(path) for path in sorted(evidence_dir.glob("*.yaml"))]


def render_evidence_list(evidence_items: list[dict[str, Any]]) -> str:
    lines = ["Evidence:"]
    if not evidence_items:
        lines.append("- none")
        return "\n".join(lines)

    for evidence in evidence_items:
        reviewer = evidence["reviewer"]
        lines.append(
            f"- {evidence['id']} [{evidence['evidence_type']}] "
            f"{evidence['run_id']} / {evidence['intervention_id']} ({reviewer['result']})"
        )

    return "\n".join(lines)


def _load_evidence_file(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as evidence_file:
            data = yaml.safe_load(evidence_file)
    except yaml.YAMLError as exc:
        raise EvidenceListError(f"evidence YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise EvidenceListError(f"evidence file must be a YAML mapping: {path}")

    evidence = data.get("evidence")
    if not isinstance(evidence, dict):
        raise EvidenceListError(f"evidence file is missing root mapping 'evidence': {path}")

    evidence_id = evidence.get("id")
    for key in ("id", "run_id", "intervention_id", "evidence_type"):
        if not isinstance(evidence.get(key), str) or not evidence[key]:
            raise EvidenceListError(
                f"evidence {evidence_id or path.name} is missing string field: {key}"
            )

    reviewer = evidence.get("reviewer")
    if not isinstance(reviewer, dict):
        raise EvidenceListError(
            f"evidence {evidence_id or path.name} is missing mapping field: reviewer"
        )
    if not isinstance(reviewer.get("result"), str) or not reviewer["result"]:
        raise EvidenceListError(
            f"evidence {evidence_id or path.name} is missing string field: reviewer.result"
        )

    if not path.name.startswith(evidence["id"]):
        raise EvidenceListError(
            f"evidence filename must start with id {evidence['id']}: {path.name}"
        )

    return evidence
