#!/usr/bin/env python3
"""Basic repository checks for ProgressEngine.

This intentionally stays dependency-light. It validates:
- required files/directories exist;
- YAML templates and .progress files are parseable if PyYAML is installed;
- Markdown local links point to existing files where practical.
- .progress objects have minimum required fields and filename/id alignment.
- CLI status documentation does not drift from the implemented slices.
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
    "src/progress_engine/README.md",
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

PROJECT_STATE_MATURITY_VALUES = {
    "unknown",
    "weak",
    "seed",
    "drafted",
    "reviewed",
    "accepted",
    "validated",
}


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
    dimensions = data.get("state_dimensions")
    if not isinstance(dimensions, dict):
        problems.append("project_state.state_dimensions: expected mapping")
    else:
        for name, dimension in dimensions.items():
            if not isinstance(name, str) or not isinstance(dimension, dict):
                problems.append("project_state.state_dimensions: expected dimension mappings")
                continue
            maturity = dimension.get("maturity")
            if maturity not in PROJECT_STATE_MATURITY_VALUES:
                allowed = ", ".join(sorted(PROJECT_STATE_MATURITY_VALUES))
                problems.append(
                    f"project_state.state_dimensions.{name}.maturity: "
                    f"expected one of {allowed}"
                )
            evidence_refs = dimension.get("evidence")
            if not isinstance(evidence_refs, list):
                problems.append(f"project_state.state_dimensions.{name}.evidence: expected list")
                continue
            for index, evidence_ref in enumerate(evidence_refs):
                if not isinstance(evidence_ref, str) or not evidence_ref:
                    problems.append(
                        f"project_state.state_dimensions.{name}.evidence[{index}]: "
                        "expected non-empty string"
                    )
                    continue
                evidence_path = (root / evidence_ref).resolve()
                if root != evidence_path and root not in evidence_path.parents:
                    problems.append(
                        f"project_state.state_dimensions.{name}.evidence[{index}]: "
                        f"ref escapes repository: {evidence_ref}"
                    )
                elif not evidence_path.exists():
                    problems.append(
                        f"project_state.state_dimensions.{name}.evidence[{index}]: "
                        f"missing referenced path {evidence_ref}"
                    )

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


def collect_readme_cli_status_problems(root: Path) -> list[str]:
    readme_path = root / "README.md"
    package_readme_path = root / "src/progress_engine/README.md"
    if not readme_path.exists() or not package_readme_path.exists():
        return []

    readme_text = readme_path.read_text(encoding="utf-8")
    package_readme_text = package_readme_path.read_text(encoding="utf-8")
    problems: list[str] = []

    problems.extend(
        collect_stale_document_phrases(
            readme_text,
            "README.md",
            [
                "尚未进入 CLI 实现",
                "后续 CLI / 核心代码实现位置",
                "后续测试位置",
                "将本包内容复制进仓库根目录后",
                "git commit -m \"docs: bootstrap ProgressEngine project state\"",
                "## 首批推进动作",
            ],
        )
    )

    readme_commands = extract_cli_command_block(readme_text)
    package_commands = extract_cli_command_block(package_readme_text)
    if readme_commands is None:
        problems.append("README.md: missing progress-engine CLI command marker block")
    if package_commands is None:
        problems.append(
            "src/progress_engine/README.md: missing progress-engine CLI command marker block"
        )
    if readme_commands is not None and package_commands is not None:
        if readme_commands != package_commands:
            problems.append(
                "README.md: CLI command marker block must match src/progress_engine/README.md"
            )
    stale_document_rules = {
        "PROJECT_STRUCTURE.md": [
            "当前包仍是项目策划书，不包含实现代码",
            "为后续 CLI 实现预留",
            "src/progressengine/",
        ],
        "decisions/ADR-0001-v0.1-tech-stack.md": [
            "Proposed，等待人工确认",
            "本 ADR 不实现 CLI，也不创建 package 配置",
            "在实现 intervention 中再创建 `pyproject.toml`",
        ],
        "docs/03-system-design/06-system-architecture-and-module-boundaries.md": [
            "本次只冻结技术边界，不创建实现配置文件",
            "这些目录是实现边界，不代表 `IV-0003` 已创建或实现代码",
            "进入代码实现前，需要先完成或确认",
            "实现阶段再创建 `pyproject.toml`",
        ],
    }
    for relative_path, phrases in stale_document_rules.items():
        path = root / relative_path
        if path.exists():
            problems.extend(
                collect_stale_document_phrases(
                    path.read_text(encoding="utf-8"),
                    relative_path,
                    phrases,
                )
            )
    return problems


def collect_stale_document_phrases(
    text: str,
    relative_path: str,
    phrases: list[str],
) -> list[str]:
    problems = []
    for phrase in phrases:
        if phrase in text:
            problems.append(f"{relative_path}: stale implementation status phrase: {phrase}")
    return problems


def extract_cli_command_block(markdown: str) -> list[str] | None:
    start = "<!-- progress-engine-cli-commands:start -->"
    end = "<!-- progress-engine-cli-commands:end -->"
    start_index = markdown.find(start)
    end_index = markdown.find(end)
    if start_index == -1 or end_index == -1 or end_index <= start_index:
        return None

    block = markdown[start_index + len(start) : end_index]
    lines = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("```"):
            continue
        lines.append(stripped)
    return lines


def check_readme_cli_status() -> None:
    problems = collect_readme_cli_status_problems(ROOT)
    if problems:
        fail(
            "CLI status documentation checks failed:\n"
            + "\n".join(f"  - {p}" for p in problems)
        )
    ok("CLI status documentation checks passed")


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
    check_readme_cli_status()


if __name__ == "__main__":
    main()
