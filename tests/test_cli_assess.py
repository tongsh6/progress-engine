from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_assess_prints_project_state_open_gaps_and_next_targets(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "gaps" / "SG-1002-unreferenced-gap.yaml").write_text(
        """
id: SG-1002
dimension: quality
severity: low
status: open
current_state: "This gap is not referenced by Project State."
desired_state: "This gap must not be listed."
evidence_refs: []
""".lstrip(),
        encoding="utf-8",
    )
    (project_root / ".progress" / "targets" / "TS-1002-unreferenced-target.yaml").write_text(
        """
id: TS-1002
name: "unreferenced target"
primary_dimension: quality
status: proposed
desired_state: "This target must not be listed."
acceptance_criteria: []
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["assess"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Assessment:",
        "Project: sample-project",
        "Phase: fixture",
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
        "- progress target list",
        "- progress intervention list",
    ]


def test_assess_returns_2_when_project_state_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "state" / "project_state.yaml").unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["assess"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing Project State file" in stderr.getvalue()


def test_assess_returns_2_when_project_state_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "state" / "project_state.yaml").write_text(
        "project: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["assess"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "Project State YAML parse failed" in stderr.getvalue()


def test_assess_returns_2_when_open_gap_reference_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "gaps" / "SG-1001-sample-gap.yaml").unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["assess"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing gap file for open gap: SG-1001" in stderr.getvalue()


def test_assess_returns_2_when_next_target_reference_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "targets" / "TS-1001-sample-target.yaml").unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["assess"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing target file for next target: TS-1001" in stderr.getvalue()


def test_assess_returns_2_when_referenced_gap_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "gaps" / "SG-1001-sample-gap.yaml").write_text(
        "id: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["assess"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "gap YAML parse failed" in stderr.getvalue()


def test_assess_returns_2_when_referenced_target_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "targets" / "TS-1001-sample-target.yaml").write_text(
        "id: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["assess"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "target YAML parse failed" in stderr.getvalue()
