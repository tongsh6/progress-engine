from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_intervention_list_prints_incomplete_interventions(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["intervention", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Interventions:",
        "- IV-1001 [implementation] sample intervention (proposed)",
    ]


def test_intervention_list_returns_2_when_directory_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    shutil.rmtree(project_root / ".progress" / "interventions")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["intervention", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing interventions directory" in stderr.getvalue()


def test_intervention_list_returns_2_when_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "interventions" / "IV-1001-sample-intervention.yaml").write_text(
        "id: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["intervention", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "intervention YAML parse failed" in stderr.getvalue()


def test_intervention_list_returns_2_when_required_fields_are_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "interventions" / "IV-1001-sample-intervention.yaml").write_text(
        """
id: IV-1001
name: sample intervention
target_state_id: TS-1001
status: proposed
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["intervention", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "intervention IV-1001 is missing string field: primary_dimension" in stderr.getvalue()
