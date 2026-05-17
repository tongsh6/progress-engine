from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_delta_list_prints_state_delta_proposals(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["delta", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "State delta proposals:",
        "- SDP-1001 [implementation] IV-1001 -> TS-1001 "
        "(proposed; acceptance: 2 pass, 1 fail, 0 not_tested)",
    ]


def test_delta_list_prints_none_when_directory_is_empty(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    for path in (project_root / ".progress" / "deltas").glob("*.yaml"):
        path.unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["delta", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == ["State delta proposals:", "- none"]


def test_delta_list_returns_2_when_directory_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    shutil.rmtree(project_root / ".progress" / "deltas")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["delta", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing deltas directory" in stderr.getvalue()


def test_delta_list_returns_2_when_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "deltas" / "SDP-1001-sample-delta.yaml").write_text(
        "state_delta_proposal: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["delta", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "state delta YAML parse failed" in stderr.getvalue()


def test_delta_list_returns_2_when_root_mapping_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "deltas" / "SDP-1001-sample-delta.yaml").write_text(
        """
id: SDP-1001
source_intervention: IV-1001
target_state_id: TS-1001
primary_dimension: implementation
status: proposed
acceptance_summary:
  pass: 2
  fail: 1
  not_tested: 0
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["delta", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert "missing root mapping 'state_delta_proposal'" in stderr.getvalue()
    assert stdout.getvalue() == ""


def test_delta_list_returns_2_when_required_fields_are_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "deltas" / "SDP-1001-sample-delta.yaml").write_text(
        """
state_delta_proposal:
  id: SDP-1001
  source_intervention: IV-1001
  target_state_id: TS-1001
  status: proposed
  acceptance_summary:
    pass: 2
    fail: 1
    not_tested: 0
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["delta", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "state delta SDP-1001 is missing string field: primary_dimension" in stderr.getvalue()


def test_delta_list_returns_2_when_acceptance_summary_fields_are_missing(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "deltas" / "SDP-1001-sample-delta.yaml").write_text(
        """
state_delta_proposal:
  id: SDP-1001
  source_intervention: IV-1001
  target_state_id: TS-1001
  primary_dimension: implementation
  status: proposed
  acceptance_summary:
    pass: 2
    fail: 1
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["delta", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "state delta SDP-1001 is missing integer field: acceptance_summary.not_tested" in (
        stderr.getvalue()
    )
