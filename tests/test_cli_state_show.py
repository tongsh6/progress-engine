from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_state_show_prints_project_state_summary(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "show"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Project: sample-project",
        "Phase: fixture",
        "Dimensions:",
        "- intent: accepted",
        "- implementation: seed",
        "Open gaps:",
        "- SG-1001",
        "Next target:",
        "- TS-1001",
    ]


def test_state_show_returns_2_when_project_state_is_missing(tmp_path: Path) -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "show"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing Project State file" in stderr.getvalue()


def test_state_show_returns_2_when_project_state_is_malformed(tmp_path: Path) -> None:
    state_dir = tmp_path / ".progress" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "project_state.yaml").write_text("project: [", encoding="utf-8")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "show"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "Project State YAML parse failed" in stderr.getvalue()


def test_state_show_returns_2_when_required_fields_are_missing(tmp_path: Path) -> None:
    state_dir = tmp_path / ".progress" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "project_state.yaml").write_text(
        """
project:
  id: sample-project
state_dimensions:
  implementation:
    summary: "Missing maturity."
open_state_gaps: []
aim_of_next_state: []
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["state", "show"], cwd=tmp_path, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "project is missing string field: current_phase" in stderr.getvalue()
