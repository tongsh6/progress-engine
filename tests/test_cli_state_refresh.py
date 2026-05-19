from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_state_refresh_prints_current_state_history_gaps_and_targets(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "refresh"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "State refresh:",
        "- project: sample-project",
        "- phase: fixture",
        "- latest state: PS-1001",
        "- latest delta: SDP-1001",
        "",
        "Maturity:",
        "- intent: accepted",
        "- implementation: seed",
        "",
        "Open gaps:",
        "- SG-1001 [implementation] Fixture implementation gap is listed.",
        "",
        "Next targets:",
        "- TS-1001 [implementation] sample target",
        "",
        "Next:",
        "- progress gaps list",
        "- progress target list",
        "- progress intervention list",
    ]


def test_state_refresh_matches_after_delta_against_latest_history(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["state", "refresh", "--after-delta", "SDP-1001"],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert "- requested delta: SDP-1001 (matched)" in stdout.getvalue()


def test_state_refresh_returns_2_when_after_delta_has_wrong_prefix(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["state", "refresh", "--after-delta", "SD-1001"],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "--after-delta must start with SDP-" in stderr.getvalue()


def test_state_refresh_returns_2_when_after_delta_is_not_latest(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    history = project_root / ".progress" / "state" / "state_history.jsonl"
    history.write_text(
        '\n'.join(
            [
                '{"state_version":"PS-1001","applied_delta":"SDP-1001","applied_at":"2026-05-17T22:20:00+08:00","applied_by":"human_user","summary":"first"}',
                '{"state_version":"PS-1002","applied_delta":"SDP-1002","applied_at":"2026-05-17T22:30:00+08:00","applied_by":"human_user","summary":"second"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["state", "refresh", "--after-delta", "SDP-1001"],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "State Delta SDP-1001 is not latest applied delta: latest is SDP-1002" in (
        stderr.getvalue()
    )


def test_state_refresh_returns_2_when_after_delta_is_not_in_history(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["state", "refresh", "--after-delta", "SDP-9999"],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "State Delta SDP-9999 not found in State History" in stderr.getvalue()


def test_state_refresh_returns_2_when_history_file_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "state" / "state_history.jsonl").unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "refresh"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing State History file" in stderr.getvalue()


def test_state_refresh_returns_2_when_open_gap_reference_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "gaps" / "SG-1001-sample-gap.yaml").unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "refresh"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing gap file for open gap: SG-1001" in stderr.getvalue()


def test_state_refresh_returns_2_when_next_target_reference_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "targets" / "TS-1001-sample-target.yaml").unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "refresh"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing target file for next target: TS-1001" in stderr.getvalue()
