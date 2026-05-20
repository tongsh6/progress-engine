"""Human-gated State Delta reject support."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from progress_engine.state.references import find_referenced_object_file


class DeltaRejectError(Exception):
    """Raised when a State Delta Proposal cannot be safely rejected."""


def reject_delta(root: Path, delta_id: str, approved_by: str, reason: str) -> dict[str, str]:
    if not delta_id.startswith("SDP-"):
        raise DeltaRejectError(f"State Delta Proposal id must start with SDP-: {delta_id}")
    if not approved_by:
        raise DeltaRejectError("--approved-by must be a non-empty value")
    reason = reason.strip()
    if not reason:
        raise DeltaRejectError("--reason must be a non-empty value")

    delta_path = _find_delta_file(root, delta_id)
    document = _load_delta_document(delta_path)
    delta = document["state_delta_proposal"]

    previous_status = _validate_reject_ready(delta, delta_id, approved_by)

    rejected_at = datetime.now().astimezone().isoformat(timespec="seconds")
    rejected_document = deepcopy(document)
    rejected_delta = rejected_document["state_delta_proposal"]
    rejected_delta["status"] = "rejected"
    reject_metadata = rejected_delta.setdefault("reject", {})
    if not isinstance(reject_metadata, dict):
        raise DeltaRejectError(f"state delta {delta_id} field reject must be a mapping")
    reject_metadata["rejected_by"] = approved_by
    reject_metadata["rejected_at"] = rejected_at
    reject_metadata["reason"] = reason
    reject_metadata["previous_status"] = previous_status

    _write_delta_document(delta_path, rejected_document)

    return {
        "delta": delta["id"],
        "rejected_by": approved_by,
        "reason": reason,
        "proposal": str(delta_path.relative_to(root)),
    }


def render_delta_reject_success(result: dict[str, str]) -> str:
    lines = [
        "State delta rejected:",
        f"- delta: {result['delta']}",
        f"- rejected by: {result['rejected_by']}",
        f"- reason: {result['reason']}",
        f"- proposal: {result['proposal']}",
        "",
        "Next:",
        "- progress delta list",
        "- progress assess",
    ]
    return "\n".join(lines)


def _find_delta_file(root: Path, delta_id: str) -> Path:
    matches = find_referenced_object_file(root / ".progress" / "deltas", delta_id)
    if not matches:
        raise DeltaRejectError(f"missing State Delta Proposal id: {delta_id}")
    if len(matches) > 1:
        rendered = ", ".join(str(path.relative_to(root)) for path in matches)
        raise DeltaRejectError(
            f"State Delta Proposal id {delta_id} matches multiple files: {rendered}"
        )
    return matches[0]


def _load_delta_document(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as delta_file:
            data = yaml.safe_load(delta_file)
    except yaml.YAMLError as exc:
        raise DeltaRejectError(f"state delta YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise DeltaRejectError(f"state delta file must be a YAML mapping: {path}")
    delta = data.get("state_delta_proposal")
    if not isinstance(delta, dict):
        raise DeltaRejectError(
            f"state delta file is missing root mapping 'state_delta_proposal': {path}"
        )
    return data


def _write_delta_document(path: Path, document: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as delta_file:
        yaml.safe_dump(document, delta_file, sort_keys=False, allow_unicode=True)


def _validate_reject_ready(
    delta: dict[str, Any],
    expected_id: str,
    approved_by: str,
) -> str:
    for key in ("id", "status", "primary_dimension"):
        if not isinstance(delta.get(key), str) or not delta[key]:
            raise DeltaRejectError(f"state delta {expected_id} is missing string field: {key}")
    if delta["id"] != expected_id:
        raise DeltaRejectError(f"state delta file id {delta['id']} does not match {expected_id}")
    if delta["status"] not in {"proposed", "accepted"}:
        raise DeltaRejectError(f"state delta {expected_id} is not reject-ready: {delta['status']}")

    if delta.get("requires_human_approval") is not True:
        raise DeltaRejectError(f"state delta {expected_id} must require human approval")

    reject_metadata = delta.get("reject")
    if not isinstance(reject_metadata, dict):
        raise DeltaRejectError(f"state delta {expected_id} is missing reject metadata")
    gate = reject_metadata.get("gate")
    if not isinstance(gate, dict) or gate.get("required") is not True:
        raise DeltaRejectError(f"state delta {expected_id} is missing required reject gate")
    if gate.get("decision") != "approved":
        raise DeltaRejectError(f"state delta {expected_id} reject gate is not approved")
    gate_approver = gate.get("approved_by")
    if not isinstance(gate_approver, str) or not gate_approver:
        raise DeltaRejectError(f"state delta {expected_id} is missing reject gate approver")
    if gate_approver != approved_by:
        raise DeltaRejectError(
            f"state delta {expected_id} reject gate approver does not match --approved-by"
        )

    return delta["status"]
