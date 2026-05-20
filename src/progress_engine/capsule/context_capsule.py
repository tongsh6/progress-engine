"""Prompt-only Context Capsule generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from progress_engine.state.project_state import load_project_state
from progress_engine.state.references import find_referenced_object_file
from progress_engine.state.state_history import load_state_history


class ContextCapsuleError(Exception):
    """Raised when a Context Capsule cannot be generated."""


def generate_context_capsule(root: Path, intervention_id: str) -> dict[str, str]:
    context = load_context_capsule_context(root, intervention_id)
    output_path = context["output_path"]
    if output_path.exists():
        raise ContextCapsuleError(
            f"Context Capsule already exists for intervention {intervention_id}: "
            f"{output_path.relative_to(root)}"
        )

    return write_context_capsule(root, context)


def ensure_context_capsule(root: Path, intervention_id: str) -> dict[str, str]:
    context = load_context_capsule_context(root, intervention_id)
    output_path = context["output_path"]
    if output_path.exists():
        return _capsule_result(root, context)
    return write_context_capsule(root, context)


def write_context_capsule(root: Path, context: dict[str, Any]) -> dict[str, str]:
    output_path = context["output_path"]
    content = render_context_capsule(
        state=context["state"],
        history=context["history"],
        intervention=context["intervention"],
        target=context["target"],
        input_paths=context["input_paths"],
    )
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return _capsule_result(root, context)


def load_context_capsule_context(root: Path, intervention_id: str) -> dict[str, Any]:
    if not intervention_id.startswith("IV-"):
        raise ContextCapsuleError(f"Intervention id must start with IV-: {intervention_id}")

    state = load_project_state(root)
    history = load_state_history(root)
    intervention_path = _find_object_file(
        root,
        root / ".progress" / "interventions",
        intervention_id,
        "Intervention",
    )
    intervention = _load_mapping(intervention_path, "intervention")
    _validate_intervention(intervention, intervention_id, intervention_path)

    target_id = intervention["target_state_id"]
    target_path = _find_object_file(
        root,
        root / ".progress" / "targets",
        target_id,
        "Target State",
    )
    target = _load_mapping(target_path, "target")
    _validate_target(target, target_id, target_path)

    return {
        "state": state,
        "history": history,
        "intervention_path": intervention_path,
        "intervention": intervention,
        "target_path": target_path,
        "target": target,
        "output_path": root
        / ".progress"
        / "context_capsules"
        / f"{intervention_id}-context-capsule.md",
        "input_paths": [
            ".progress/state/project_state.yaml",
            ".progress/state/state_history.jsonl",
            str(intervention_path.relative_to(root)),
            str(target_path.relative_to(root)),
        ],
    }


def render_context_capsule(
    *,
    state: dict[str, Any],
    history: list[dict[str, Any]],
    intervention: dict[str, Any],
    target: dict[str, Any],
    input_paths: list[str],
) -> str:
    project = state["project"]
    dimensions = state["state_dimensions"]
    latest_state_version = history[-1]["state_version"] if history else "none"

    lines = [
        f"# Context Capsule: {intervention['id']}",
        "",
        "## Project Snapshot",
        "",
        f"- Project: {project.get('id', 'unknown')}",
        f"- Phase: {project.get('current_phase', 'unknown')}",
        f"- State Version: {latest_state_version}",
        "- Current Maturity:",
    ]
    for name, dimension in dimensions.items():
        lines.append(f"  - {name}: {dimension.get('maturity', 'unknown')}")

    lines.extend(
        [
            "",
            "## Target State",
            "",
            f"- ID: {target['id']}",
            f"- Dimension: {target['primary_dimension']}",
            f"- Status: {target['status']}",
            f"- Desired State: {_string_value(target.get('desired_state'))}",
            f"- From: {_render_mapping_inline(target.get('from'))}",
            f"- To: {_render_mapping_inline(target.get('to'))}",
            "",
            "## Intervention",
            "",
            f"- ID: {intervention['id']}",
            f"- Title: {intervention['name']}",
            f"- Goal: {intervention['goal']}",
            f"- Status: {intervention['status']}",
            f"- Primary Dimension: {intervention['primary_dimension']}",
            f"- Target State: {intervention['target_state_id']}",
            "",
            "## In Scope",
        ]
    )
    lines.extend(_render_list(intervention.get("in_scope")))

    lines.extend(["", "## Out of Scope"])
    lines.extend(_render_list(intervention.get("out_of_scope")))

    lines.extend(["", "## Inputs"])
    lines.extend(f"- {path}" for path in input_paths)
    lines.extend(_render_prefixed_list("Open Gap", state.get("open_state_gaps")))
    lines.extend(_render_prefixed_list("Next Target", state.get("aim_of_next_state")))

    lines.extend(["", "## Outputs"])
    lines.append(f"- .progress/context_capsules/{intervention['id']}-context-capsule.md")
    lines.append("- Execution artifacts and evidence must be recorded after the intervention runs.")

    lines.extend(["", "## Acceptance Criteria"])
    lines.extend(_render_acceptance_criteria(target.get("acceptance_criteria")))

    lines.extend(["", "## Evidence Required"])
    lines.extend(_render_list(intervention.get("evidence_required")))

    lines.extend(
        [
            "",
            "## Rules",
            "",
            "- Use only this context and referenced files.",
            "- Do not carry forward prior transcript.",
            "- Do not expand scope.",
            "- Do not claim completion without acceptance mapping.",
            "- Do not defer silently.",
            "- Output evidence and remaining gaps.",
            "- Do not modify Project State or state history directly.",
            "",
            "## Failure Handling",
            "",
            "- If required context is missing, stop and report the missing input.",
            "- If scope exceeds this capsule, propose a split intervention.",
            "- If acceptance criteria cannot be satisfied, report remaining gaps.",
            "- Do not create Evidence, Verification, or State Delta objects unless explicitly assigned.",
            "",
        ]
    )

    return "\n".join(lines)


def render_context_capsule_success(result: dict[str, str]) -> str:
    lines = [
        "Context capsule generated:",
        f"- intervention: {result['intervention']}",
        f"- target: {result['target']}",
        f"- capsule: {result['capsule']}",
        "",
        "Next:",
        "- Open the capsule in an AI tool or hand it to a human executor.",
        "- Record evidence after execution.",
    ]
    return "\n".join(lines)


def _capsule_result(root: Path, context: dict[str, Any]) -> dict[str, str]:
    return {
        "intervention": context["intervention"]["id"],
        "target": context["target"]["id"],
        "capsule": str(context["output_path"].relative_to(root)),
    }


def _find_object_file(root: Path, directory: Path, object_id: str, label: str) -> Path:
    matches = find_referenced_object_file(directory, object_id)
    if not matches:
        raise ContextCapsuleError(f"missing {label} id: {object_id}")
    if len(matches) > 1:
        rendered = ", ".join(str(path.relative_to(root)) for path in matches)
        raise ContextCapsuleError(f"{label} id {object_id} matches multiple files: {rendered}")
    return matches[0]


def _load_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as yaml_file:
            data = yaml.safe_load(yaml_file)
    except yaml.YAMLError as exc:
        raise ContextCapsuleError(f"{label} YAML parse failed for {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ContextCapsuleError(f"{label} must be a YAML mapping: {path}")
    return data


def _validate_intervention(data: dict[str, Any], expected_id: str, path: Path) -> None:
    for key in ("id", "name", "primary_dimension", "target_state_id", "status", "goal"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise ContextCapsuleError(
                f"intervention {expected_id} is missing string field: {key}"
            )
    if data["id"] != expected_id:
        raise ContextCapsuleError(
            f"intervention file id mismatch: expected {expected_id}, got {data['id']}"
        )
    if not path.name.startswith(data["id"]):
        raise ContextCapsuleError(
            f"intervention filename must start with id {data['id']}: {path.name}"
        )


def _validate_target(data: dict[str, Any], expected_id: str, path: Path) -> None:
    for key in ("id", "name", "primary_dimension", "status"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise ContextCapsuleError(f"target {expected_id} is missing string field: {key}")
    if data["id"] != expected_id:
        raise ContextCapsuleError(
            f"target file id mismatch: expected {expected_id}, got {data['id']}"
        )
    if not path.name.startswith(data["id"]):
        raise ContextCapsuleError(
            f"target filename must start with id {data['id']}: {path.name}"
        )


def _render_list(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["- none"]
    lines = []
    for item in value:
        if isinstance(item, str):
            lines.append(f"- {item}")
        else:
            lines.append(f"- {_string_value(item)}")
    return lines


def _render_prefixed_list(prefix: str, value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [f"- {prefix}: {item}" for item in value if isinstance(item, str) and item]


def _render_acceptance_criteria(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["- none"]
    lines = []
    for item in value:
        if isinstance(item, dict):
            item_id = item.get("id")
            criterion = item.get("criterion")
            if isinstance(item_id, str) and isinstance(criterion, str):
                lines.append(f"- {item_id}: {criterion}")
            else:
                lines.append(f"- {_string_value(item)}")
        elif isinstance(item, str):
            lines.append(f"- {item}")
        else:
            lines.append(f"- {_string_value(item)}")
    return lines


def _render_mapping_inline(value: Any) -> str:
    if not isinstance(value, dict) or not value:
        return "not specified"
    parts = [f"{key}={_string_value(item)}" for key, item in value.items()]
    return "; ".join(parts)


def _string_value(value: Any) -> str:
    if value in (None, "", []):
        return "not specified"
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True).strip()
