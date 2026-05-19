"""Human-gated State Delta rollback support."""

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


class DeltaRollbackError(Exception):
    """Raised when a State Delta Proposal cannot be safely rolled back."""


def rollback_delta(root: Path, delta_id: str, approved_by: str) -> dict[str, str]:
    if not delta_id.startswith("SDP-"):
        raise DeltaRollbackError(f"State Delta Proposal id must start with SDP-: {delta_id}")
    if not approved_by:
        raise DeltaRollbackError("--approved-by must be a non-empty value")

    delta_path = _find_delta_file(root, delta_id)
    document = _load_delta_document(delta_path)
    delta = document["state_delta_proposal"]

    history = load_state_history(root)
    rollback_data = _validate_rollback_ready(delta, delta_id, approved_by, history)

    state = load_project_state(root)
    next_version = next_state_version(history)
    updated_state = _apply_project_state_restore(state, rollback_data["project_state_restore"])

    rolled_back_at = datetime.now().astimezone().isoformat(timespec="seconds")
    history_entry = {
        "state_version": next_version,
        "applied_delta": f"ROLLBACK-{delta['id']}",
        "applied_at": rolled_back_at,
        "applied_by": approved_by,
        "summary": _history_summary(delta, rollback_data),
        "evidence_refs": delta["evidence_refs"],
        "rolled_back_delta": delta["id"],
        "rolled_back_state_version": rollback_data["rolled_back_state"],
        "restored_state_version": rollback_data["restored_state"],
    }
    _validate_history_entry(history_entry)

    rolled_back_document = deepcopy(document)
    rolled_back_delta = rolled_back_document["state_delta_proposal"]
    rolled_back_delta["status"] = "rolled_back"
    rollback_metadata = rolled_back_delta["rollback"]
    rollback_metadata["rolled_back_by"] = approved_by
    rollback_metadata["rolled_back_at"] = rolled_back_at
    rollback_metadata["rolled_back_state_version"] = rollback_data["rolled_back_state"]
    rollback_metadata["restored_state_version"] = rollback_data["restored_state"]
    rollback_metadata["rollback_history_version"] = next_version
    rollback_metadata["project_state_file"] = ".progress/state/project_state.yaml"

    write_project_state(root, updated_state)
    append_state_history(root, history_entry)
    _write_delta_document(delta_path, rolled_back_document)

    return {
        "delta": delta["id"],
        "rolled_back_state": rollback_data["rolled_back_state"],
        "restored_state": rollback_data["restored_state"],
        "new_state": next_version,
        "project_state": ".progress/state/project_state.yaml",
        "state_history": ".progress/state/state_history.jsonl",
    }


def render_delta_rollback_success(result: dict[str, str]) -> str:
    lines = [
        "State delta rolled back:",
        f"- delta: {result['delta']}",
        f"- rolled back state: {result['rolled_back_state']}",
        f"- restored state: {result['restored_state']}",
        f"- new state: {result['new_state']}",
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
        raise DeltaRollbackError(f"missing State Delta Proposal id: {delta_id}")
    if len(matches) > 1:
        rendered = ", ".join(str(path.relative_to(root)) for path in matches)
        raise DeltaRollbackError(
            f"State Delta Proposal id {delta_id} matches multiple files: {rendered}"
        )
    return matches[0]


def _load_delta_document(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as delta_file:
            data = yaml.safe_load(delta_file)
    except yaml.YAMLError as exc:
        raise DeltaRollbackError(f"state delta YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise DeltaRollbackError(f"state delta file must be a YAML mapping: {path}")
    delta = data.get("state_delta_proposal")
    if not isinstance(delta, dict):
        raise DeltaRollbackError(
            f"state delta file is missing root mapping 'state_delta_proposal': {path}"
        )
    return data


def _write_delta_document(path: Path, document: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as delta_file:
        yaml.safe_dump(document, delta_file, sort_keys=False, allow_unicode=True)


def _validate_rollback_ready(
    delta: dict[str, Any],
    expected_id: str,
    approved_by: str,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    for key in ("id", "status", "primary_dimension"):
        if not isinstance(delta.get(key), str) or not delta[key]:
            raise DeltaRollbackError(f"state delta {expected_id} is missing string field: {key}")
    if delta["id"] != expected_id:
        raise DeltaRollbackError(f"state delta file id {delta['id']} does not match {expected_id}")
    if delta["status"] != "applied":
        raise DeltaRollbackError(f"state delta {expected_id} is not rollback-ready: {delta['status']}")

    evidence_refs = delta.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise DeltaRollbackError(f"state delta {expected_id} is missing evidence_refs")

    apply_metadata = delta.get("apply")
    if not isinstance(apply_metadata, dict):
        raise DeltaRollbackError(f"state delta {expected_id} is missing apply metadata")
    restored_state = _require_metadata_string(
        apply_metadata,
        "apply.previous_state_version",
        expected_id,
    )
    rolled_back_state = _require_metadata_string(
        apply_metadata,
        "apply.next_state_version",
        expected_id,
    )

    rollback_metadata = delta.get("rollback")
    if not isinstance(rollback_metadata, dict):
        raise DeltaRollbackError(f"state delta {expected_id} is missing rollback metadata")
    if rollback_metadata.get("reversible") is not True:
        raise DeltaRollbackError(f"state delta {expected_id} is not reversible")

    gate = rollback_metadata.get("gate")
    if not isinstance(gate, dict) or gate.get("required") is not True:
        raise DeltaRollbackError(f"state delta {expected_id} is missing required rollback gate")
    if gate.get("decision") != "approved":
        raise DeltaRollbackError(f"state delta {expected_id} rollback gate is not approved")
    gate_approver = gate.get("approved_by")
    if not isinstance(gate_approver, str) or not gate_approver:
        raise DeltaRollbackError(f"state delta {expected_id} is missing rollback gate approver")
    if gate_approver != approved_by:
        raise DeltaRollbackError(
            f"state delta {expected_id} rollback gate approver does not match --approved-by"
        )

    restore = rollback_metadata.get("project_state_restore")
    if not isinstance(restore, dict):
        raise DeltaRollbackError(f"state delta {expected_id} is missing rollback.project_state_restore")
    _validate_project_state_restore(restore, expected_id)
    _validate_history_alignment(history, expected_id, rolled_back_state, restored_state)

    return {
        "rolled_back_state": rolled_back_state,
        "restored_state": restored_state,
        "project_state_restore": restore,
    }


def _require_metadata_string(metadata: dict[str, Any], key: str, delta_id: str) -> str:
    value: Any = metadata
    for part in key.split(".")[1:]:
        if not isinstance(value, dict):
            raise DeltaRollbackError(f"state delta {delta_id} is missing {key}")
        value = value.get(part)
    if not isinstance(value, str) or not value:
        raise DeltaRollbackError(f"state delta {delta_id} is missing {key}")
    return value


def _validate_history_alignment(
    history: list[dict[str, Any]],
    delta_id: str,
    rolled_back_state: str,
    restored_state: str,
) -> None:
    if not history:
        raise DeltaRollbackError(f"state delta {delta_id} cannot rollback without state history")

    states = {entry["state_version"]: entry for entry in history}
    if restored_state not in states:
        raise DeltaRollbackError(
            f"state delta {delta_id} previous state version is missing from history: {restored_state}"
        )

    rolled_back_entry = states.get(rolled_back_state)
    if rolled_back_entry is None:
        raise DeltaRollbackError(
            f"state delta {delta_id} applied state version is missing from history: {rolled_back_state}"
        )
    if rolled_back_entry.get("applied_delta") != delta_id:
        raise DeltaRollbackError(
            f"state delta {delta_id} applied state history entry does not match delta id"
        )

    latest = history[-1]
    if latest["state_version"] != rolled_back_state:
        raise DeltaRollbackError(
            f"state delta {delta_id} can only rollback the latest state version: {rolled_back_state}"
        )


def _validate_project_state_restore(restore: dict[str, Any], delta_id: str) -> None:
    allowed_top_level = {"state_dimensions", "open_state_gaps", "aim_of_next_state"}
    extra_top_level = sorted(set(restore) - allowed_top_level)
    if extra_top_level:
        raise DeltaRollbackError(
            f"state delta {delta_id} project_state_restore has unsupported fields: "
            + ", ".join(extra_top_level)
        )

    dimensions = restore.get("state_dimensions", {})
    if not isinstance(dimensions, dict):
        raise DeltaRollbackError(
            f"state delta {delta_id} project_state_restore.state_dimensions must be a mapping"
        )
    allowed_dimension_fields = {"maturity", "summary", "evidence"}
    for name, dimension_restore in dimensions.items():
        if not isinstance(name, str) or not isinstance(dimension_restore, dict):
            raise DeltaRollbackError(f"state delta {delta_id} dimension restores must be mappings")
        extra_dimension_fields = sorted(set(dimension_restore) - allowed_dimension_fields)
        if extra_dimension_fields:
            raise DeltaRollbackError(
                f"state delta {delta_id} dimension {name} has unsupported fields: "
                + ", ".join(extra_dimension_fields)
            )
        for key in ("maturity", "summary"):
            if key in dimension_restore and (
                not isinstance(dimension_restore[key], str) or not dimension_restore[key]
            ):
                raise DeltaRollbackError(f"state delta {delta_id} dimension {name}.{key} must be a string")
        if "evidence" in dimension_restore:
            _validate_string_list(
                dimension_restore["evidence"],
                f"dimension {name}.evidence",
                delta_id,
            )

    for key in ("open_state_gaps", "aim_of_next_state"):
        if key in restore:
            _validate_string_list(restore[key], key, delta_id)


def _validate_string_list(value: Any, field: str, delta_id: str) -> None:
    if not isinstance(value, list):
        raise DeltaRollbackError(f"state delta {delta_id} {field} must be a list")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            raise DeltaRollbackError(f"state delta {delta_id} {field}[{index}] must be a non-empty string")


def _apply_project_state_restore(
    state: dict[str, Any],
    restore: dict[str, Any],
) -> dict[str, Any]:
    restored = deepcopy(state)

    for name, dimension_restore in restore.get("state_dimensions", {}).items():
        dimensions = restored.get("state_dimensions")
        if not isinstance(dimensions, dict) or not isinstance(dimensions.get(name), dict):
            raise DeltaRollbackError(f"Project State is missing dimension for restore: {name}")
        dimensions[name].update(dimension_restore)

    for key in ("open_state_gaps", "aim_of_next_state"):
        if key in restore:
            restored[key] = restore[key]

    return restored


def _history_summary(delta: dict[str, Any], rollback_data: dict[str, Any]) -> str:
    rollback_metadata = delta.get("rollback")
    if isinstance(rollback_metadata, dict) and isinstance(rollback_metadata.get("summary"), str):
        return rollback_metadata["summary"]
    return (
        f"Rolled back {delta['id']} from {rollback_data['rolled_back_state']} "
        f"to {rollback_data['restored_state']}."
    )


def _validate_history_entry(entry: dict[str, Any]) -> None:
    for key in ("state_version", "applied_delta", "applied_at", "applied_by", "summary"):
        if not isinstance(entry.get(key), str) or not entry[key]:
            raise DeltaRollbackError(f"State History entry is missing string field: {key}")
