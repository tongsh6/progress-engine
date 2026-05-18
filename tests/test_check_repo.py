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


def test_readme_cli_status_check_passes_when_marker_blocks_match(tmp_path: Path) -> None:
    check_repo = load_check_repo_module()
    project_root = tmp_path / "project"
    package_root = project_root / "src" / "progress_engine"
    package_root.mkdir(parents=True)
    readme_block = """
<!-- progress-engine-cli-commands:start -->
```bash
progress assess
progress state show
```
<!-- progress-engine-cli-commands:end -->
""".lstrip()
    (project_root / "README.md").write_text(readme_block, encoding="utf-8")
    (package_root / "README.md").write_text(readme_block, encoding="utf-8")

    problems = check_repo.collect_readme_cli_status_problems(project_root)

    assert problems == []


def test_readme_cli_status_check_reports_stale_status_phrase(tmp_path: Path) -> None:
    check_repo = load_check_repo_module()
    project_root = tmp_path / "project"
    package_root = project_root / "src" / "progress_engine"
    package_root.mkdir(parents=True)
    readme_block = """
当前仓库尚未进入 CLI 实现。

<!-- progress-engine-cli-commands:start -->
```bash
progress assess
```
<!-- progress-engine-cli-commands:end -->
""".lstrip()
    (project_root / "README.md").write_text(readme_block, encoding="utf-8")
    (package_root / "README.md").write_text(readme_block, encoding="utf-8")

    problems = check_repo.collect_readme_cli_status_problems(project_root)

    assert problems == ["README.md: stale implementation status phrase: 尚未进入 CLI 实现"]


def test_readme_cli_status_check_reports_stale_bootstrap_instructions(
    tmp_path: Path,
) -> None:
    check_repo = load_check_repo_module()
    project_root = tmp_path / "project"
    package_root = project_root / "src" / "progress_engine"
    package_root.mkdir(parents=True)
    readme_text = """
<!-- progress-engine-cli-commands:start -->
```bash
progress assess
```
<!-- progress-engine-cli-commands:end -->

# 将本包内容复制进仓库根目录后：
git commit -m "docs: bootstrap ProgressEngine project state"
## 首批推进动作
""".lstrip()
    package_readme_text = """
<!-- progress-engine-cli-commands:start -->
```bash
progress assess
```
<!-- progress-engine-cli-commands:end -->
""".lstrip()
    (project_root / "README.md").write_text(readme_text, encoding="utf-8")
    (package_root / "README.md").write_text(package_readme_text, encoding="utf-8")

    problems = check_repo.collect_readme_cli_status_problems(project_root)

    assert problems == [
        "README.md: stale implementation status phrase: 将本包内容复制进仓库根目录后",
        "README.md: stale implementation status phrase: "
        'git commit -m "docs: bootstrap ProgressEngine project state"',
        "README.md: stale implementation status phrase: ## 首批推进动作",
    ]


def test_readme_cli_status_check_reports_mismatched_command_blocks(tmp_path: Path) -> None:
    check_repo = load_check_repo_module()
    project_root = tmp_path / "project"
    package_root = project_root / "src" / "progress_engine"
    package_root.mkdir(parents=True)
    (project_root / "README.md").write_text(
        """
<!-- progress-engine-cli-commands:start -->
```bash
progress assess
```
<!-- progress-engine-cli-commands:end -->
""".lstrip(),
        encoding="utf-8",
    )
    (package_root / "README.md").write_text(
        """
<!-- progress-engine-cli-commands:start -->
```bash
progress state show
```
<!-- progress-engine-cli-commands:end -->
""".lstrip(),
        encoding="utf-8",
    )

    problems = check_repo.collect_readme_cli_status_problems(project_root)

    assert problems == [
        "README.md: CLI command marker block must match src/progress_engine/README.md"
    ]


def test_readme_cli_status_check_reports_stale_project_structure_phrase(
    tmp_path: Path,
) -> None:
    check_repo = load_check_repo_module()
    project_root = tmp_path / "project"
    package_root = project_root / "src" / "progress_engine"
    package_root.mkdir(parents=True)
    readme_block = """
<!-- progress-engine-cli-commands:start -->
```bash
progress assess
```
<!-- progress-engine-cli-commands:end -->
""".lstrip()
    (project_root / "README.md").write_text(readme_block, encoding="utf-8")
    (package_root / "README.md").write_text(readme_block, encoding="utf-8")
    (project_root / "PROJECT_STRUCTURE.md").write_text(
        "src/ tests/ schemas/\n  为后续 CLI 实现预留。\n",
        encoding="utf-8",
    )

    problems = check_repo.collect_readme_cli_status_problems(project_root)

    assert problems == [
        "PROJECT_STRUCTURE.md: stale implementation status phrase: 为后续 CLI 实现预留"
    ]


def test_readme_cli_status_check_reports_stale_adr_status(tmp_path: Path) -> None:
    check_repo = load_check_repo_module()
    project_root = tmp_path / "project"
    package_root = project_root / "src" / "progress_engine"
    decisions_root = project_root / "decisions"
    package_root.mkdir(parents=True)
    decisions_root.mkdir()
    readme_block = """
<!-- progress-engine-cli-commands:start -->
```bash
progress assess
```
<!-- progress-engine-cli-commands:end -->
""".lstrip()
    (project_root / "README.md").write_text(readme_block, encoding="utf-8")
    (package_root / "README.md").write_text(readme_block, encoding="utf-8")
    (decisions_root / "ADR-0001-v0.1-tech-stack.md").write_text(
        "## 状态\n\nProposed，等待人工确认。\n",
        encoding="utf-8",
    )

    problems = check_repo.collect_readme_cli_status_problems(project_root)

    assert problems == [
        "decisions/ADR-0001-v0.1-tech-stack.md: "
        "stale implementation status phrase: Proposed，等待人工确认"
    ]
