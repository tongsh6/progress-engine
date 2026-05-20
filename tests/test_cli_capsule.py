from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

import pytest

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"
CAPSULE_PATH = Path(".progress/context_capsules/IV-1001-context-capsule.md")


def test_capsule_generates_prompt_only_markdown_without_state_changes(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    initial_state = (project_root / ".progress/state/project_state.yaml").read_text(
        encoding="utf-8"
    )
    initial_history = (project_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    )

    exit_code, stdout, stderr = _capsule(project_root)

    assert exit_code == 0
    assert stderr == ""
    assert stdout.splitlines() == [
        "Context capsule generated:",
        "- intervention: IV-1001",
        "- target: TS-1001",
        "- capsule: .progress/context_capsules/IV-1001-context-capsule.md",
        "",
        "Next:",
        "- Open the capsule in an AI tool or hand it to a human executor.",
        "- Record evidence after execution.",
    ]

    capsule = (project_root / CAPSULE_PATH).read_text(encoding="utf-8")
    assert "# Context Capsule: IV-1001" in capsule
    assert "## Project Snapshot" in capsule
    assert "- Project: sample-project" in capsule
    assert "- State Version: PS-1001" in capsule
    assert "## Target State" in capsule
    assert "- ID: TS-1001" in capsule
    assert "## Intervention" in capsule
    assert "- ID: IV-1001" in capsule
    assert "## In Scope" in capsule
    assert "## Out of Scope" in capsule
    assert "## Acceptance Criteria" in capsule
    assert "## Evidence Required" in capsule
    assert "## Rules" in capsule
    assert "- Do not carry forward prior transcript." in capsule
    assert "## Failure Handling" in capsule

    assert (project_root / ".progress/state/project_state.yaml").read_text(
        encoding="utf-8"
    ) == initial_state
    assert (project_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    ) == initial_history


def test_capsule_returns_2_when_intervention_is_missing(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)

    exit_code, stdout, stderr = _capsule(project_root, intervention_id="IV-9999")

    assert exit_code == 2
    assert stdout == ""
    assert "missing Intervention id: IV-9999" in stderr
    assert not (project_root / ".progress/context_capsules/IV-9999-context-capsule.md").exists()


def test_capsule_returns_2_when_target_is_missing(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    (project_root / ".progress/targets/TS-1001-sample-target.yaml").unlink()

    exit_code, stdout, stderr = _capsule(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "missing Target State id: TS-1001" in stderr
    assert not (project_root / CAPSULE_PATH).exists()


def test_capsule_returns_2_when_output_already_exists(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    first_exit_code, _, first_stderr = _capsule(project_root)
    assert first_exit_code == 0
    assert first_stderr == ""

    exit_code, stdout, stderr = _capsule(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "Context Capsule already exists for intervention IV-1001" in stderr


def test_capsule_returns_2_when_intervention_id_is_invalid(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)

    exit_code, stdout, stderr = _capsule(project_root, intervention_id="BAD-1001")

    assert exit_code == 2
    assert stdout == ""
    assert "Intervention id must start with IV-: BAD-1001" in stderr


def test_capsule_returns_2_when_project_state_is_missing(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    (project_root / ".progress/state/project_state.yaml").unlink()

    exit_code, stdout, stderr = _capsule(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "missing Project State file" in stderr
    assert not (project_root / CAPSULE_PATH).exists()


def test_capsule_returns_2_when_state_history_is_missing(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    (project_root / ".progress/state/state_history.jsonl").unlink()

    exit_code, stdout, stderr = _capsule(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "missing State History file" in stderr
    assert not (project_root / CAPSULE_PATH).exists()


def _copy_fixture(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    return project_root


def _capsule(
    project_root: Path,
    *,
    intervention_id: str = "IV-1001",
) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    exit_code = main(
        ["capsule", "--intervention", intervention_id],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )
    return exit_code, stdout.getvalue(), stderr.getvalue()
