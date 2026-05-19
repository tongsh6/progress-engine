from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_verify_list_prints_verification_reviews(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["verify", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Verification reviews:",
        "- EV-1001 RUN-20260517-IV-1001 / IV-1001 "
        "(pass_requires_human_gate; acceptance: 1 pass, 1 fail, 1 not_tested)",
        "- EV-1002 RUN-20260517-IV-1001 / IV-1001 "
        "(pass_requires_human_gate; acceptance: 1 pass, 0 fail, 0 not_tested)",
        "- EV-1003 RUN-20260517-IV-1001 / IV-1001 "
        "(pass_requires_human_gate; acceptance: 1 pass, 0 fail, 0 not_tested)",
    ]


def test_verify_list_prints_none_when_evidence_directory_is_empty(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    for path in (project_root / ".progress" / "evidence").glob("*.yaml"):
        path.unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["verify", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == ["Verification reviews:", "- none"]


def test_verify_list_returns_2_when_evidence_directory_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    shutil.rmtree(project_root / ".progress" / "evidence")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["verify", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing evidence directory" in stderr.getvalue()


def test_verify_list_returns_2_when_evidence_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "evidence" / "EV-1001-sample-evidence.yaml").write_text(
        "evidence: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["verify", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "evidence YAML parse failed" in stderr.getvalue()


def test_verify_list_returns_2_when_required_evidence_fields_are_missing(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "evidence" / "EV-1001-sample-evidence.yaml").write_text(
        """
evidence:
  id: EV-1001
  run_id: RUN-20260517-IV-1001
  intervention_id: IV-1001
  evidence_type: artifact_review
  claims:
    - acceptance_mapping:
        - status: pass
  reviewer:
    type: verifier
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["verify", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "evidence EV-1001 is missing string field: reviewer.result" in stderr.getvalue()


def test_verify_list_returns_2_when_acceptance_mapping_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "evidence" / "EV-1001-sample-evidence.yaml").write_text(
        """
evidence:
  id: EV-1001
  run_id: RUN-20260517-IV-1001
  intervention_id: IV-1001
  evidence_type: artifact_review
  claims:
    - dimension: implementation
      before: sample before
      after: sample after
  reviewer:
    type: verifier
    result: pass_requires_human_gate
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["verify", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "claim 1 is missing list field: acceptance_mapping" in stderr.getvalue()


def test_verify_list_returns_2_when_acceptance_status_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "evidence" / "EV-1001-sample-evidence.yaml").write_text(
        """
evidence:
  id: EV-1001
  run_id: RUN-20260517-IV-1001
  intervention_id: IV-1001
  evidence_type: artifact_review
  claims:
    - dimension: implementation
      before: sample before
      after: sample after
      acceptance_mapping:
        - criterion: sample criterion
          evidence_ref: null
  reviewer:
    type: verifier
    result: pass_requires_human_gate
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["verify", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "claim 1 mapping 1 is missing string field: status" in stderr.getvalue()
