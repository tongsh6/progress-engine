from __future__ import annotations

from io import StringIO
from pathlib import Path

import yaml

from progress_engine.cli import main


def init_project(tmp_path: Path) -> None:
    stdout = StringIO()
    stderr = StringIO()
    assert main(["init", "--project", "sample-project"], cwd=tmp_path, stdout=stdout, stderr=stderr) == 0


def test_intake_captures_intent_and_updates_project_state(tmp_path: Path) -> None:
    init_project(tmp_path)
    source = tmp_path / "intent.md"
    source.write_text("# Intent\n\nBuild a useful local progress tool.\n", encoding="utf-8")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["intake", "--from", "intent.md"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Captured intent: .progress/artifacts/intent.md",
        "Updated Project State intent maturity: seed",
        "Next:",
        "- progress state show",
    ]
    assert (tmp_path / ".progress" / "artifacts" / "intent.md").read_text(encoding="utf-8") == (
        "# Intent\n\nBuild a useful local progress tool.\n"
    )
    state = yaml.safe_load((tmp_path / ".progress" / "state" / "project_state.yaml").read_text())
    assert state["state_dimensions"]["intent"]["maturity"] == "seed"
    assert ".progress/artifacts/intent.md" in state["state_dimensions"]["intent"]["evidence"]


def test_intake_project_state_can_be_read_by_state_show(tmp_path: Path) -> None:
    init_project(tmp_path)
    (tmp_path / "intent.md").write_text("Build a useful local progress tool.\n", encoding="utf-8")
    intake_stdout = StringIO()
    intake_stderr = StringIO()
    assert (
        main(["intake", "--from", "intent.md"], cwd=tmp_path, stdout=intake_stdout, stderr=intake_stderr)
        == 0
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "show"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert "- intent: seed" in stdout.getvalue().splitlines()


def test_intake_returns_2_when_project_state_is_missing(tmp_path: Path) -> None:
    (tmp_path / "intent.md").write_text("Build a useful local progress tool.\n", encoding="utf-8")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["intake", "--from", "intent.md"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing Project State file" in stderr.getvalue()


def test_intake_returns_2_when_intent_file_is_missing(tmp_path: Path) -> None:
    init_project(tmp_path)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["intake", "--from", "missing.md"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing intent file: missing.md" in stderr.getvalue()


def test_intake_returns_2_when_intent_file_is_empty(tmp_path: Path) -> None:
    init_project(tmp_path)
    (tmp_path / "intent.md").write_text(" \n", encoding="utf-8")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["intake", "--from", "intent.md"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "intent file is empty" in stderr.getvalue()
