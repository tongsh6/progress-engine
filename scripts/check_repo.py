#!/usr/bin/env python3
"""Basic repository checks for ProgressEngine.

This intentionally stays dependency-light. It validates:
- required files/directories exist;
- YAML templates and .progress files are parseable if PyYAML is installed;
- Markdown local links point to existing files where practical.
- .progress objects have minimum required fields and filename/id alignment.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "PROJECT_BRIEF.md",
    "PROJECT_STRUCTURE.md",
    "INDEX.md",
    "docs/00-overview/02-core-methodology-state-driven-progress.md",
    "docs/01-state-engine/03-project-state-model-and-maturity-matrix.md",
    "docs/04-protocols/09-fresh-context-isolation-protocol.md",
    "docs/04-protocols/10-evidence-verifier-protocol.md",
    "templates/state/project_state.yaml",
    ".progress/state/project_state.yaml",
    ".github/pull_request_template.md",
]

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

PROGRESS_OBJECT_RULES = [
    {
        "glob": ".progress/targets/*.yaml",
        "prefix": "TS",
        "root": None,
        "required": ["id", "name", "primary_dimension", "status"],
    },
    {
        "glob": ".progress/gaps/*.yaml",
        "prefix": "SG",
        "root": None,
        "required": ["id", "dimension", "current_state", "desired_state"],
    },
    {
        "glob": ".progress/interventions/*.yaml",
        "prefix": "IV",
        "root": None,
        "required": ["id", "name", "primary_dimension", "target_state_id", "status", "goal"],
    },
    {
        "glob": ".progress/runs/*.yaml",
        "prefix": "RUN",
        "root": None,
        "required": ["id", "intervention_id", "target_state_id", "status", "primary_dimension"],
    },
    {
        "glob": ".progress/evidence/*.yaml",
        "prefix": "EV",
        "root": "evidence",
        "required": ["id", "run_id", "intervention_id", "evidence_type", "claims", "reviewer"],
    },
    {
        "glob": ".progress/deltas/*.yaml",
        "prefix": "SDP",
        "root": "state_delta_proposal",
        "required": [
            "id",
            "source_intervention",
            "status",
            "primary_dimension",
            "before",
            "after",
            "evidence_refs",
            "requires_human_approval",
            "do_not_apply_automatically",
        ],
    },
    {
        "glob": ".progress/events/*.yaml",
        "prefix": "EVT",
        "root": "change_event",
        "required": ["id", "type", "severity", "source", "summary", "affected_dimensions"],
    },
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def ok(message: str) -> None:
    print(f"[OK] {message}")


def check_required() -> None:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        fail("Missing required paths:\n" + "\n".join(f"  - {m}" for m in missing))
    ok("required paths exist")


def check_yaml() -> None:
    yaml_files = list(ROOT.rglob("*.yaml")) + list(ROOT.rglob("*.yml"))
    if yaml is None:
        warn("PyYAML not installed; skipped YAML parse checks")
        return
    for path in yaml_files:
        try:
            with path.open("r", encoding="utf-8") as f:
                yaml.safe_load(f)
        except Exception as exc:
            fail(f"YAML parse failed: {path.relative_to(ROOT)}: {exc}")
    ok(f"YAML parse passed for {len(yaml_files)} files")


def load_yaml(path: Path) -> object:
    if yaml is None:
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_progress_objects() -> None:
    if yaml is None:
        warn("PyYAML not installed; skipped .progress object checks")
        return
    problems: list[str] = []
    checked = 0
    for rule in PROGRESS_OBJECT_RULES:
        for path in sorted(ROOT.glob(rule["glob"])):
            checked += 1
            data = load_yaml(path)
            if not isinstance(data, dict):
                problems.append(f"{path.relative_to(ROOT)}: expected YAML mapping")
                continue
            obj = data
            root = rule["root"]
            if root is not None:
                nested = data.get(root)
                if not isinstance(nested, dict):
                    problems.append(f"{path.relative_to(ROOT)}: missing root mapping '{root}'")
                    continue
                obj = nested
            for field in rule["required"]:
                value = obj.get(field)
                if value in (None, "", []):
                    problems.append(f"{path.relative_to(ROOT)}: missing required field '{field}'")
            obj_id = obj.get("id")
            prefix = rule["prefix"]
            if isinstance(obj_id, str):
                if not obj_id.startswith(f"{prefix}-"):
                    problems.append(f"{path.relative_to(ROOT)}: id '{obj_id}' must start with {prefix}-")
                if not path.name.startswith(obj_id):
                    problems.append(f"{path.relative_to(ROOT)}: filename must start with id '{obj_id}'")
    if problems:
        fail(".progress object checks failed:\n" + "\n".join(f"  - {p}" for p in problems[:80]))
    ok(f".progress object checks passed for {checked} files")


def collect_project_state_reference_problems(root: Path) -> list[str]:
    if yaml is None:
        return []

    state_path = root / ".progress/state/project_state.yaml"
    if not state_path.exists():
        return [".progress/state/project_state.yaml: missing Project State file"]

    data = load_yaml(state_path)
    if not isinstance(data, dict):
        return [".progress/state/project_state.yaml: expected YAML mapping"]

    problems: list[str] = []
    reference_rules = [
        ("open_state_gaps", ".progress/gaps", "SG"),
        ("aim_of_next_state", ".progress/targets", "TS"),
    ]
    for field, directory, prefix in reference_rules:
        values = data.get(field)
        if not isinstance(values, list):
            problems.append(f"project_state.{field}: expected list")
            continue
        for index, obj_id in enumerate(values):
            if not isinstance(obj_id, str) or not obj_id:
                problems.append(f"project_state.{field}[{index}]: expected non-empty string")
                continue
            if not obj_id.startswith(f"{prefix}-"):
                problems.append(
                    f"project_state.{field}[{index}]: id '{obj_id}' must start with {prefix}-"
                )
                continue
            matches = sorted((root / directory).glob(f"{obj_id}-*.yaml"))
            if not matches:
                problems.append(f"project_state.{field}: missing referenced id {obj_id}")
            elif len(matches) > 1:
                rendered = ", ".join(str(path.relative_to(root)) for path in matches)
                problems.append(
                    f"project_state.{field}: referenced id {obj_id} matches multiple files: {rendered}"
                )
    return problems


def check_project_state_references() -> None:
    if yaml is None:
        warn("PyYAML not installed; skipped Project State reference checks")
        return
    problems = collect_project_state_reference_problems(ROOT)
    if problems:
        fail("Project State reference checks failed:\n" + "\n".join(f"  - {p}" for p in problems))
    ok("Project State reference checks passed")


def check_jsonl() -> None:
    jsonl_files = list(ROOT.glob(".progress/**/*.jsonl"))
    for path in jsonl_files:
        with path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    json.loads(line)
                except Exception as exc:
                    fail(f"JSONL parse failed: {path.relative_to(ROOT)}:{line_number}: {exc}")
    ok(f"JSONL parse passed for {len(jsonl_files)} files")


def check_markdown_links() -> None:
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    problems: list[str] = []
    for md in ROOT.rglob("*.md"):
        text = md.read_text(encoding="utf-8", errors="ignore")
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if target.startswith("sandbox:"):
                continue
            target_no_anchor = target.split("#", 1)[0]
            if not target_no_anchor:
                continue
            target_path = (md.parent / target_no_anchor).resolve()
            if ROOT not in target_path.parents and target_path != ROOT:
                continue
            if not target_path.exists():
                problems.append(f"{md.relative_to(ROOT)} -> {target}")
    if problems:
        fail("Broken local Markdown links:\n" + "\n".join(f"  - {p}" for p in problems[:50]))
    ok("local Markdown links passed")


def main() -> None:
    check_required()
    check_yaml()
    check_jsonl()
    check_markdown_links()
    check_progress_objects()
    check_project_state_references()


if __name__ == "__main__":
    main()
