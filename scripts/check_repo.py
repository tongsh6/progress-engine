#!/usr/bin/env python3
"""Basic repository checks for ProgressEngine.

This intentionally stays dependency-light. It validates:
- required files/directories exist;
- YAML templates and .progress files are parseable if PyYAML is installed;
- Markdown local links point to existing files where practical.
"""
from __future__ import annotations

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
    check_markdown_links()


if __name__ == "__main__":
    main()
