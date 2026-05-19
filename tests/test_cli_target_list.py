from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_target_list_prints_next_targets_from_project_state(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["target", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Next targets:",
        "- TS-1001 [implementation] sample target (proposed)",
    ]


def test_target_list_returns_2_when_target_file_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "targets" / "TS-1001-sample-target.yaml").unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["target", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing target file for next target: TS-1001" in stderr.getvalue()


def test_target_list_does_not_match_exact_filename_without_slug(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    targets_dir = project_root / ".progress" / "targets"
    (targets_dir / "TS-1001-sample-target.yaml").unlink()
    (targets_dir / "TS-1001.yaml").write_text(
        """
id: TS-1001
name: "exact filename target"
primary_dimension: implementation
status: proposed
desired_state: "This filename does not follow the referenced object convention."
acceptance_criteria: []
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["target", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing target file for next target: TS-1001" in stderr.getvalue()


def test_target_list_returns_2_when_target_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "targets" / "TS-1001-sample-target.yaml").write_text(
        "id: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["target", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "target YAML parse failed" in stderr.getvalue()


def test_target_list_returns_2_when_required_target_fields_are_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "targets" / "TS-1001-sample-target.yaml").write_text(
        """
id: TS-1001
name: sample target
status: proposed
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["target", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "target TS-1001 is missing string field: primary_dimension" in stderr.getvalue()
