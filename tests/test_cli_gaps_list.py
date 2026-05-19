from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_gaps_list_prints_open_gaps_from_project_state(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "gaps" / "SG-1002-resolved-gap.yaml").write_text(
        """
id: SG-1002
dimension: quality
severity: low
status: resolved
current_state: "This gap is not referenced by Project State."
desired_state: "This gap must not be listed."
evidence_refs: []
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["gaps", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "Open gaps:",
        "- SG-1001 [implementation] Fixture implementation gap is listed.",
    ]


def test_gaps_list_returns_2_when_gap_file_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "gaps" / "SG-1001-sample-gap.yaml").unlink()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["gaps", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing gap file for open gap: SG-1001" in stderr.getvalue()


def test_gaps_list_does_not_match_similar_gap_id_prefix(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    gaps_dir = project_root / ".progress" / "gaps"
    (gaps_dir / "SG-1001-sample-gap.yaml").unlink()
    (gaps_dir / "SG-10010-similar-prefix-gap.yaml").write_text(
        """
id: SG-10010
dimension: implementation
severity: medium
status: open
current_state: "This is a different gap."
desired_state: "This similar prefix gap must not satisfy SG-1001."
evidence_refs: []
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["gaps", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "missing gap file for open gap: SG-1001" in stderr.getvalue()


def test_gaps_list_returns_2_when_gap_yaml_is_malformed(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "gaps" / "SG-1001-sample-gap.yaml").write_text(
        "id: [",
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["gaps", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "gap YAML parse failed" in stderr.getvalue()


def test_gaps_list_returns_2_when_required_gap_fields_are_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    (project_root / ".progress" / "gaps" / "SG-1001-sample-gap.yaml").write_text(
        """
id: SG-1001
dimension: implementation
status: open
""".lstrip(),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["gaps", "list"], cwd=project_root, stdout=stdout, stderr=stderr)

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "gap SG-1001 is missing string field: desired_state" in stderr.getvalue()
