from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_event_list_prints_change_events(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["event", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Change events:",
        "- EVT-1001 [medium] implementation_finding (2 dimensions; human_review=true)",
    ]


def test_event_list_prints_none_when_directory_is_empty(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    for path in (project_root / ".progress" / "events").glob("*.yaml"):
        path.unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["event", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == ["Change events:", "- none"]


def test_event_list_returns_2_when_directory_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    shutil.rmtree(project_root / ".progress" / "events")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["event", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing events directory" in stderr.getvalue()


def test_event_list_returns_2_when_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "events" / "EVT-1001-sample-event.yaml").write_text(
        "change_event: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["event", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "change event YAML parse failed" in stderr.getvalue()


def test_event_list_returns_2_when_root_mapping_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "events" / "EVT-1001-sample-event.yaml").write_text(
        """
id: EVT-1001
type: implementation_finding
severity: medium
summary: sample implementation finding
affected_dimensions:
  - implementation
requires_human_review: true
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["event", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing root mapping 'change_event'" in stderr.getvalue()


def test_event_list_returns_2_when_required_fields_are_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "events" / "EVT-1001-sample-event.yaml").write_text(
        """
change_event:
  id: EVT-1001
  type: implementation_finding
  summary: sample implementation finding
  affected_dimensions:
    - implementation
  requires_human_review: true
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["event", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "change event EVT-1001 is missing string field: severity" in stderr.getvalue()


def test_event_list_returns_2_when_affected_dimensions_are_invalid(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "events" / "EVT-1001-sample-event.yaml").write_text(
        """
change_event:
  id: EVT-1001
  type: implementation_finding
  severity: medium
  summary: sample implementation finding
  affected_dimensions: implementation
  requires_human_review: true
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["event", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing string list field: affected_dimensions" in stderr.getvalue()


def test_event_list_returns_2_when_human_review_flag_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "events" / "EVT-1001-sample-event.yaml").write_text(
        """
change_event:
  id: EVT-1001
  type: implementation_finding
  severity: medium
  summary: sample implementation finding
  affected_dimensions:
    - implementation
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["event", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing boolean field: requires_human_review" in stderr.getvalue()
