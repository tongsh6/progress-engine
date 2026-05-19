"""Human-gated State Delta apply support."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from progress_engine.state.project_state import load_project_state, write_project_state
from progress_engine.state.references import find_referenced_object_file
from progress_engine.state.state_history import (
    append_state_history,
    load_state_history,
    next_state_version,
)


class DeltaApplyError(Exception):
    """Raised when a State Delta Proposal cannot be safely applied."""


def apply_delta(root: Path, delta_id: str, approved_by: str) -> dict[str, str]:
    if not delta_id.startswith("SDP-"):
        raise DeltaApplyError(f"State Delta Proposal id must start with SDP-: {delta_id}")
    if not approved_by:
        raise DeltaApplyError("--approved-by must be a non-empty value")

    delta_path = _find_delta_file(root, delta_id)
    document = _load_delta_document(delta_path)
    delta = document["state_delta_proposal"]

    _validate_apply_ready(root, delta, delta_id, approved_by)

    state = load_project_state(root)
    history = load_state_history(root)
    previous_version = history[-1]["state_version"] if history else "PS-0000"
    next_version = next_state_version(history)
    updated_state = _apply_project_state_update(state, delta["project_state_update"])

    applied_at = datetime.now().astimezone().isoformat(timespec="seconds")
    summary = _history_summary(delta)
    history_entry = {
        "state_version": next_version,
        "applied_delta": delta["id"],
        "applied_at": applied_at,
        "applied_by": approved_by,
        "summary": summary,
        "evidence_refs": delta["evidence_refs"],
    }
    _validate_history_entry(history_entry)

    applied_document = deepcopy(document)
    applied_delta = applied_document["state_delta_proposal"]
    applied_delta["status"] = "applied"
    apply_metadata = applied_delta.setdefault("apply", {})
    if not isinstance(apply_metadata, dict):
        raise DeltaApplyError(f"state delta {delta_id} field apply must be a mapping")
    apply_metadata["applied_by"] = approved_by
    apply_metadata["applied_at"] = applied_at
    apply_metadata["previous_state_version"] = previous_version
    apply_metadata["next_state_version"] = next_version
    apply_metadata["project_state_file"] = ".progress/state/project_state.yaml"

    write_project_state(root, updated_state)
    append_state_history(root, history_entry)
    _write_delta_document(delta_path, applied_document)

    return {
        "delta": delta["id"],
        "previous_state": previous_version,
        "next_state": next_version,
        "project_state": ".progress/state/project_state.yaml",
        "state_history": ".progress/state/state_history.jsonl",
    }


def render_delta_apply_success(result: dict[str, str]) -> str:
    lines = [
        "State delta applied:",
        f"- delta: {result['delta']}",
        f"- previous state: {result['previous_state']}",
        f"- next state: {result['next_state']}",
        f"- project_state: {result['project_state']}",
        f"- state_history: {result['state_history']}",
        "",
        "Next:",
        "- progress state show",
        "- progress assess",
    ]
    return "\n".join(lines)


def _find_delta_file(root: Path, delta_id: str) -> Path:
    matches = find_referenced_object_file(root / ".progress" / "deltas", delta_id)
    if not matches:
        raise DeltaApplyError(f"missing State Delta Proposal id: {delta_id}")
    if len(matches) > 1:
        rendered = ", ".join(str(path.relative_to(root)) for path in matches)
        raise DeltaApplyError(f"State Delta Proposal id {delta_id} matches multiple files: {rendered}")
    return matches[0]


def _load_delta_document(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as delta_file:
            data = yaml.safe_load(delta_file)
    except yaml.YAMLError as exc:
        raise DeltaApplyError(f"state delta YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise DeltaApplyError(f"state delta file must be a YAML mapping: {path}")
    delta = data.get("state_delta_proposal")
    if not isinstance(delta, dict):
        raise DeltaApplyError(
            f"state delta file is missing root mapping 'state_delta_proposal': {path}"
        )
    return data


def _write_delta_document(path: Path, document: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as delta_file:
        yaml.safe_dump(document, delta_file, sort_keys=False, allow_unicode=True)


def _validate_apply_ready(
    root: Path,
    delta: dict[str, Any],
    expected_id: str,
    approved_by: str,
) -> None:
    for key in ("id", "status", "primary_dimension"):
        if not isinstance(delta.get(key), str) or not delta[key]:
            raise DeltaApplyError(f"state delta {expected_id} is missing string field: {key}")
    if delta["id"] != expected_id:
        raise DeltaApplyError(f"state delta file id {delta['id']} does not match {expected_id}")
    if delta["status"] not in {"proposed", "accepted"}:
        raise DeltaApplyError(f"state delta {expected_id} is not apply-ready: {delta['status']}")

    if delta.get("requires_human_approval") is not True:
        raise DeltaApplyError(f"state delta {expected_id} must require human approval")
    gate = delta.get("gate")
    if not isinstance(gate, dict) or gate.get("required") is not True:
        raise DeltaApplyError(f"state delta {expected_id} is missing required human gate")
    if gate.get("decision") != "approved":
        raise DeltaApplyError(f"state delta {expected_id} is not human gate approved")
    gate_approver = gate.get("approved_by")
    if not isinstance(gate_approver, str) or not gate_approver:
        raise DeltaApplyError(f"state delta {expected_id} is missing human gate approver")
    if gate_approver != approved_by:
        raise DeltaApplyError(
            f"state delta {expected_id} gate approver does not match --approved-by"
        )

    summary = delta.get("acceptance_summary")
    if not isinstance(summary, dict):
        raise DeltaApplyError(f"state delta {expected_id} is missing acceptance_summary")
    if summary.get("fail") != 0 or summary.get("not_tested") != 0:
        raise DeltaApplyError(
            f"state delta {expected_id} cannot apply with fail or not_tested acceptance"
        )

    evidence_refs = delta.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise DeltaApplyError(f"state delta {expected_id} is missing evidence_refs")
    for index, evidence_ref in enumerate(evidence_refs):
        if not isinstance(evidence_ref, str) or not evidence_ref:
            raise DeltaApplyError(
                f"state delta {expected_id} evidence_refs[{index}] must be a non-empty string"
            )
        evidence_path = (root / evidence_ref).resolve()
        if root != evidence_path and root not in evidence_path.parents:
            raise DeltaApplyError(f"state delta {expected_id} evidence ref escapes repository")
        if not evidence_path.exists():
            raise DeltaApplyError(f"missing evidence ref for state delta {expected_id}: {evidence_ref}")

    if not isinstance(delta.get("project_state_update"), dict):
        raise DeltaApplyError(f"state delta {expected_id} is missing project_state_update")
    _validate_project_state_update(delta["project_state_update"], expected_id)


def _validate_project_state_update(update: dict[str, Any], delta_id: str) -> None:
    allowed_top_level = {"state_dimensions", "open_state_gaps", "aim_of_next_state"}
    extra_top_level = sorted(set(update) - allowed_top_level)
    if extra_top_level:
        raise DeltaApplyError(
            f"state delta {delta_id} project_state_update has unsupported fields: "
            + ", ".join(extra_top_level)
        )

    dimensions = update.get("state_dimensions", {})
    if not isinstance(dimensions, dict):
        raise DeltaApplyError(f"state delta {delta_id} project_state_update.state_dimensions must be a mapping")
    allowed_dimension_fields = {"maturity", "summary", "evidence"}
    for name, dimension_update in dimensions.items():
        if not isinstance(name, str) or not isinstance(dimension_update, dict):
            raise DeltaApplyError(f"state delta {delta_id} dimension updates must be mappings")
        extra_dimension_fields = sorted(set(dimension_update) - allowed_dimension_fields)
        if extra_dimension_fields:
            raise DeltaApplyError(
                f"state delta {delta_id} dimension {name} has unsupported fields: "
                + ", ".join(extra_dimension_fields)
            )
        for key in ("maturity", "summary"):
            if key in dimension_update and (
                not isinstance(dimension_update[key], str) or not dimension_update[key]
            ):
                raise DeltaApplyError(f"state delta {delta_id} dimension {name}.{key} must be a string")
        if "evidence" in dimension_update:
            _validate_string_list(dimension_update["evidence"], f"dimension {name}.evidence", delta_id)

    for key in ("open_state_gaps", "aim_of_next_state"):
        if key in update:
            _validate_string_list(update[key], key, delta_id)


def _validate_string_list(value: Any, field: str, delta_id: str) -> None:
    if not isinstance(value, list):
        raise DeltaApplyError(f"state delta {delta_id} {field} must be a list")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            raise DeltaApplyError(f"state delta {delta_id} {field}[{index}] must be a non-empty string")


def _apply_project_state_update(
    state: dict[str, Any],
    update: dict[str, Any],
) -> dict[str, Any]:
    updated = deepcopy(state)

    for name, dimension_update in update.get("state_dimensions", {}).items():
        dimensions = updated.get("state_dimensions")
        if not isinstance(dimensions, dict) or not isinstance(dimensions.get(name), dict):
            raise DeltaApplyError(f"Project State is missing dimension for update: {name}")
        dimensions[name].update(dimension_update)

    for key in ("open_state_gaps", "aim_of_next_state"):
        if key in update:
            updated[key] = update[key]

    return updated


def _history_summary(delta: dict[str, Any]) -> str:
    apply_metadata = delta.get("apply")
    if isinstance(apply_metadata, dict) and isinstance(apply_metadata.get("summary"), str):
        return apply_metadata["summary"]
    after = delta.get("after")
    if isinstance(after, dict):
        primary = after.get(delta["primary_dimension"])
        if isinstance(primary, dict) and isinstance(primary.get("summary"), str):
            return primary["summary"]
    return f"Applied {delta['id']}."


def _validate_history_entry(entry: dict[str, Any]) -> None:
    for key in ("state_version", "applied_delta", "applied_at", "applied_by", "summary"):
        if not isinstance(entry.get(key), str) or not entry[key]:
            raise DeltaApplyError(f"State History entry is missing string field: {key}")
