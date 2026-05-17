from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_run_list_prints_open_runs(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["run", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Runs:",
        "- RUN-20260517-IV-1001 [implementation] IV-1001 -> TS-1001 (active)",
    ]


def test_run_list_returns_2_when_directory_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    shutil.rmtree(project_root / ".progress" / "runs")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["run", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing runs directory" in stderr.getvalue()


def test_run_list_returns_2_when_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "runs" / "RUN-20260517-IV-1001.yaml").write_text(
        "id: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["run", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "run YAML parse failed" in stderr.getvalue()


def test_run_list_returns_2_when_required_fields_are_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "runs" / "RUN-20260517-IV-1001.yaml").write_text(
        """
id: RUN-20260517-IV-1001
intervention_id: IV-1001
target_state_id: TS-1001
status: active
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["run", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "run RUN-20260517-IV-1001 is missing string field: primary_dimension" in stderr.getvalue()
