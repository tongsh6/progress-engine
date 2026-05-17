from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_state_history_prints_history_entries(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "history"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "State history:",
        "- PS-1001 <- SDP-1001 by human_user at 2026-05-17T22:20:00+08:00",
    ]


def test_state_history_prints_none_when_file_is_empty(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "state" / "state_history.jsonl").write_text(
        "\n",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "history"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == ["State history:", "- none"]


def test_state_history_returns_2_when_file_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "state" / "state_history.jsonl").unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "history"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing State History file" in stderr.getvalue()


def test_state_history_returns_2_when_jsonl_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "state" / "state_history.jsonl").write_text(
        '{"state_version":',
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "history"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "State History JSONL parse failed at line 1" in stderr.getvalue()


def test_state_history_returns_2_when_jsonl_entry_is_not_object(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "state" / "state_history.jsonl").write_text(
        '["not", "an", "object"]\n',
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "history"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "State History entry at line 1 must be a JSON object" in stderr.getvalue()


def test_state_history_returns_2_when_required_fields_are_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "state" / "state_history.jsonl").write_text(
        '{"state_version":"PS-1001","applied_delta":"SDP-1001","applied_by":"human_user","summary":"sample"}\n',
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "history"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "State History entry at line 1 is missing string field: applied_at" in (
        stderr.getvalue()
    )
