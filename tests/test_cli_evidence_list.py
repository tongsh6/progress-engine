from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_evidence_list_prints_evidence_objects(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["evidence", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Evidence:",
        "- EV-1001 [artifact_review] RUN-20260517-IV-1001 / IV-1001 (pass_requires_human_gate)",
        "- EV-1002 [artifact_review] RUN-20260517-IV-1001 / IV-1001 (pass_requires_human_gate)",
    ]


def test_evidence_list_prints_none_when_directory_is_empty(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    for path in (project_root / ".progress" / "evidence").glob("*.yaml"):
        path.unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["evidence", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == ["Evidence:", "- none"]


def test_evidence_list_returns_2_when_directory_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    shutil.rmtree(project_root / ".progress" / "evidence")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["evidence", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing evidence directory" in stderr.getvalue()


def test_evidence_list_returns_2_when_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "evidence" / "EV-1001-sample-evidence.yaml").write_text(
        "evidence: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["evidence", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "evidence YAML parse failed" in stderr.getvalue()


def test_evidence_list_returns_2_when_root_mapping_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "evidence" / "EV-1001-sample-evidence.yaml").write_text(
        """
id: EV-1001
run_id: RUN-20260517-IV-1001
intervention_id: IV-1001
evidence_type: artifact_review
reviewer:
  result: pass_requires_human_gate
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["evidence", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing root mapping 'evidence'" in stderr.getvalue()


def test_evidence_list_returns_2_when_required_fields_are_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "evidence" / "EV-1001-sample-evidence.yaml").write_text(
        """
evidence:
  id: EV-1001
  run_id: RUN-20260517-IV-1001
  intervention_id: IV-1001
  reviewer:
    result: pass_requires_human_gate
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["evidence", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "evidence EV-1001 is missing string field: evidence_type" in stderr.getvalue()


def test_evidence_list_returns_2_when_reviewer_result_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "evidence" / "EV-1001-sample-evidence.yaml").write_text(
        """
evidence:
  id: EV-1001
  run_id: RUN-20260517-IV-1001
  intervention_id: IV-1001
  evidence_type: artifact_review
  reviewer:
    type: verifier
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["evidence", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "evidence EV-1001 is missing string field: reviewer.result" in stderr.getvalue()
