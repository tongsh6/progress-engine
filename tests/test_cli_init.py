from __future__ import annotations

from io import StringIO
from pathlib import Path

from progress_engine.cli import main


def test_init_creates_minimal_progress_skeleton(tmp_path: Path) -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["init", "--project", "sample-project"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Initialized ProgressEngine project: sample-project",
        "Created:",
        "- .progress/README.md",
        "- .progress/state/project_state.yaml",
        "- .progress/state/state_history.jsonl",
        "Next:",
        "- progress state show",
    ]
    assert (tmp_path / ".progress" / "state" / "project_state.yaml").exists()
    assert (tmp_path / ".progress" / "state" / "state_history.jsonl").read_text(
        encoding="utf-8"
    ) == ""
    for directory in [
        "gaps",
        "artifacts",
        "targets",
        "interventions",
        "runs",
        "evidence",
        "deltas",
        "events",
        "context_capsules",
        "ledger",
    ]:
        assert (tmp_path / ".progress" / directory).is_dir()


def test_init_project_state_can_be_read_by_state_show(tmp_path: Path) -> None:
    init_stdout = StringIO()
    init_stderr = StringIO()
    assert (
        main(["init", "--project", "sample-project"], cwd=tmp_path, stdout=init_stdout, stderr=init_stderr)
        == 0
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "show"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Project: sample-project",
        "Phase: initialized",
        "Dimensions:",
        "- intent: unknown",
        "- product: unknown",
        "- design: unknown",
        "- architecture: unknown",
        "- implementation: unknown",
        "- quality: unknown",
        "- delivery: unknown",
        "- knowledge: unknown",
        "Open gaps:",
        "- none",
        "Next target:",
        "- none",
    ]


def test_init_refuses_to_overwrite_existing_progress(tmp_path: Path) -> None:
    progress_dir = tmp_path / ".progress"
    progress_dir.mkdir()
    marker = progress_dir / "marker.txt"
    marker.write_text("keep", encoding="utf-8")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["init", "--project", "sample-project"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert ".progress already exists" in stderr.getvalue()
    assert marker.read_text(encoding="utf-8") == "keep"


def test_init_rejects_invalid_project_id(tmp_path: Path) -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["init", "--project", "bad project"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "project id may only contain" in stderr.getvalue()
