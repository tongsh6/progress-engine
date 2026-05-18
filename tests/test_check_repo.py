from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"
CHECK_REPO_PATH = Path(__file__).parents[1] / "scripts" / "check_repo.py"


def load_check_repo_module():
    spec = importlib.util.spec_from_file_location("check_repo", CHECK_REPO_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def copy_fixture(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    return project_root


def test_project_state_reference_check_passes_for_fixture(tmp_path: Path) -> None:
    check_repo = load_check_repo_module()
    project_root = copy_fixture(tmp_path)

    problems = check_repo.collect_project_state_reference_problems(project_root)

    assert problems == []


def test_project_state_reference_check_reports_missing_gap(tmp_path: Path) -> None:
    check_repo = load_check_repo_module()
    project_root = copy_fixture(tmp_path)
    (project_root / ".progress" / "gaps" / "SG-1001-sample-gap.yaml").unlink()

    problems = check_repo.collect_project_state_reference_problems(project_root)

    assert problems == ["project_state.open_state_gaps: missing referenced id SG-1001"]


def test_project_state_reference_check_reports_missing_target(tmp_path: Path) -> None:
    check_repo = load_check_repo_module()
    project_root = copy_fixture(tmp_path)
    (project_root / ".progress" / "targets" / "TS-1001-sample-target.yaml").unlink()

    problems = check_repo.collect_project_state_reference_problems(project_root)

    assert problems == ["project_state.aim_of_next_state: missing referenced id TS-1001"]


def test_project_state_reference_check_reports_non_list_field(tmp_path: Path) -> None:
    check_repo = load_check_repo_module()
    project_root = copy_fixture(tmp_path)
    state_path = project_root / ".progress" / "state" / "project_state.yaml"
    state_path.write_text(
        """
project:
  id: sample-project
  name: Sample Project
  current_phase: fixture
state_dimensions: {}
open_state_gaps: SG-1001
aim_of_next_state:
  - TS-1001
""".lstrip(),
        encoding="utf-8",
    )

    problems = check_repo.collect_project_state_reference_problems(project_root)

    assert problems == ["project_state.open_state_gaps: expected list"]


def test_project_state_reference_check_reports_non_string_reference(tmp_path: Path) -> None:
    check_repo = load_check_repo_module()
    project_root = copy_fixture(tmp_path)
    state_path = project_root / ".progress" / "state" / "project_state.yaml"
    state_path.write_text(
        """
project:
  id: sample-project
  name: Sample Project
  current_phase: fixture
state_dimensions: {}
open_state_gaps:
  - SG-1001
aim_of_next_state:
  - 1001
""".lstrip(),
        encoding="utf-8",
    )

    problems = check_repo.collect_project_state_reference_problems(project_root)

    assert problems == ["project_state.aim_of_next_state[0]: expected non-empty string"]
