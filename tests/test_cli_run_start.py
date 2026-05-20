from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path
from typing import Any

import yaml

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"
CAPSULE_PATH = Path(".progress/context_capsules/IV-1001-context-capsule.md")


def test_run_start_creates_active_run_and_capsule_without_state_changes(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _complete_existing_sample_run(project_root)
    initial_state = (project_root / ".progress/state/project_state.yaml").read_text(
        encoding="utf-8"
    )
    initial_history = (project_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    )

    exit_code, stdout, stderr = _run_start(project_root)

    assert exit_code == 0
    assert stderr == ""
    lines = stdout.splitlines()
    assert lines[0] == "Run started:"
    assert lines[2] == "- intervention: IV-1001"
    assert lines[3] == "- target: TS-1001"
    assert lines[4] == "- mode: prompt-only"
    assert lines[5] == "- capsule: .progress/context_capsules/IV-1001-context-capsule.md"
    assert lines[7:] == [
        "",
        "Next:",
        "- Open the capsule in an AI tool or hand it to a human executor.",
        "- Record evidence after execution.",
    ]

    run_id = lines[1].removeprefix("- run: ")
    run_file = lines[6].removeprefix("- run file: ")
    assert run_id.startswith("RUN-")
    assert run_id.endswith("-IV-1001")
    assert run_file == f".progress/runs/{run_id}.yaml"

    run = _read_yaml(project_root / run_file)
    assert run["id"] == run_id
    assert run["intervention_id"] == "IV-1001"
    assert run["target_state_id"] == "TS-1001"
    assert run["mode"] == "prompt-only"
    assert run["primary_dimension"] == "implementation"
    assert run["status"] == "active"
    assert run["context_capsule"] == ".progress/context_capsules/IV-1001-context-capsule.md"
    assert run["execution_session"]["fresh_context"] is True
    assert run["execution_session"]["transcript_carried_forward"] is False
    assert run["execution_session"]["mode"] == "prompt-only"

    assert (project_root / CAPSULE_PATH).exists()
    assert "# Context Capsule: IV-1001" in (project_root / CAPSULE_PATH).read_text(
        encoding="utf-8"
    )
    assert (project_root / ".progress/state/project_state.yaml").read_text(
        encoding="utf-8"
    ) == initial_state
    assert (project_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    ) == initial_history


def test_run_start_reuses_existing_capsule_without_overwriting(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _complete_existing_sample_run(project_root)
    capsule_path = project_root / CAPSULE_PATH
    capsule_path.write_text("existing capsule\n", encoding="utf-8")

    exit_code, stdout, stderr = _run_start(project_root)

    assert exit_code == 0
    assert stderr == ""
    assert "- capsule: .progress/context_capsules/IV-1001-context-capsule.md" in stdout
    assert capsule_path.read_text(encoding="utf-8") == "existing capsule\n"


def test_run_start_returns_2_when_intervention_is_missing(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)

    exit_code, stdout, stderr = _run_start(project_root, intervention_id="IV-9999")

    assert exit_code == 2
    assert stdout == ""
    assert "missing Intervention id: IV-9999" in stderr
    assert not list((project_root / ".progress/runs").glob("RUN-*-IV-9999*.yaml"))


def test_run_start_returns_2_when_target_is_missing(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _complete_existing_sample_run(project_root)
    (project_root / ".progress/targets/TS-1001-sample-target.yaml").unlink()

    exit_code, stdout, stderr = _run_start(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "missing Target State id: TS-1001" in stderr
    assert not (project_root / CAPSULE_PATH).exists()


def test_run_start_returns_2_when_mode_is_unsupported(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _complete_existing_sample_run(project_root)

    exit_code, stdout, stderr = _run_start(project_root, mode="api-adapter")

    assert exit_code == 2
    assert stdout == ""
    assert "unsupported run mode: api-adapter" in stderr
    assert not (project_root / CAPSULE_PATH).exists()


def test_run_start_returns_2_when_intervention_already_has_active_run(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)

    exit_code, stdout, stderr = _run_start(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "intervention IV-1001 already has an active or planned Run" in stderr
    assert not (project_root / CAPSULE_PATH).exists()


def test_run_start_returns_2_when_intervention_id_is_invalid(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)

    exit_code, stdout, stderr = _run_start(project_root, intervention_id="BAD-1001")

    assert exit_code == 2
    assert stdout == ""
    assert "Intervention id must start with IV-: BAD-1001" in stderr


def _copy_fixture(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    return project_root


def _run_start(
    project_root: Path,
    *,
    intervention_id: str = "IV-1001",
    mode: str = "prompt-only",
) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    exit_code = main(
        ["run", "start", "--intervention", intervention_id, "--mode", mode],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )
    return exit_code, stdout.getvalue(), stderr.getvalue()


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as yaml_file:
        data = yaml.safe_load(yaml_file)
    assert isinstance(data, dict)
    return data


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as yaml_file:
        yaml.safe_dump(data, yaml_file, sort_keys=False, allow_unicode=True)


def _complete_existing_sample_run(project_root: Path) -> None:
    path = project_root / ".progress/runs/RUN-20260517-IV-1001.yaml"
    run = _read_yaml(path)
    run["status"] = "completed"
    _write_yaml(path, run)
