from __future__ import annotations

import json
import shutil
from io import StringIO
from pathlib import Path
from typing import Any

import yaml

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"
DELTA_PATH = Path(".progress/deltas/SDP-1003-rollback-ready-delta.yaml")


def test_delta_rollback_restores_project_state_history_and_delta_metadata(
    tmp_path: Path,
) -> None:
    project_root = _copy_fixture(tmp_path)
    _prepare_rollback_ready_state(project_root)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["delta", "rollback", "SDP-1003", "--approved-by", "human_user"],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "State delta rolled back:",
        "- delta: SDP-1003",
        "- rolled back state: PS-1002",
        "- restored state: PS-1001",
        "- new state: PS-1003",
        "- project_state: .progress/state/project_state.yaml",
        "- state_history: .progress/state/state_history.jsonl",
        "",
        "Next:",
        "- progress state show",
        "- progress assess",
    ]

    state = _read_yaml(project_root / ".progress/state/project_state.yaml")
    implementation = state["state_dimensions"]["implementation"]
    assert implementation["maturity"] == "seed"
    assert implementation["summary"] == "Implementation is seeded."
    assert implementation["evidence"] == []
    assert state["open_state_gaps"] == ["SG-1001"]
    assert state["aim_of_next_state"] == ["TS-1001"]

    history_entries = _read_history(project_root)
    assert history_entries[-1]["state_version"] == "PS-1003"
    assert history_entries[-1]["applied_delta"] == "ROLLBACK-SDP-1003"
    assert history_entries[-1]["applied_by"] == "human_user"
    assert history_entries[-1]["rolled_back_delta"] == "SDP-1003"
    assert history_entries[-1]["rolled_back_state_version"] == "PS-1002"
    assert history_entries[-1]["restored_state_version"] == "PS-1001"

    delta = _read_delta(project_root)
    assert delta["status"] == "rolled_back"
    assert delta["apply"]["next_state_version"] == "PS-1002"
    assert delta["rollback"]["rolled_back_by"] == "human_user"
    assert delta["rollback"]["rolled_back_state_version"] == "PS-1002"
    assert delta["rollback"]["restored_state_version"] == "PS-1001"
    assert delta["rollback"]["rollback_history_version"] == "PS-1003"
    assert delta["rollback"]["project_state_file"] == ".progress/state/project_state.yaml"


def test_delta_rollback_returns_2_when_delta_is_not_applied(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _prepare_rollback_ready_state(project_root)
    _mutate_delta(project_root, lambda delta: delta.update({"status": "proposed"}))

    exit_code, stdout, stderr = _rollback(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "is not rollback-ready: proposed" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_rollback_returns_2_when_delta_is_not_reversible(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _prepare_rollback_ready_state(project_root)
    _mutate_delta(project_root, lambda delta: delta["rollback"].update({"reversible": False}))

    exit_code, stdout, stderr = _rollback(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "is not reversible" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_rollback_returns_2_when_gate_is_not_approved(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _prepare_rollback_ready_state(project_root)
    _mutate_delta(
        project_root,
        lambda delta: delta["rollback"]["gate"].update({"decision": "pending"}),
    )

    exit_code, stdout, stderr = _rollback(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "rollback gate is not approved" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_rollback_returns_2_when_approved_by_does_not_match_gate(
    tmp_path: Path,
) -> None:
    project_root = _copy_fixture(tmp_path)
    _prepare_rollback_ready_state(project_root)

    exit_code, stdout, stderr = _rollback(project_root, approved_by="other_user")

    assert exit_code == 2
    assert stdout == ""
    assert "rollback gate approver does not match --approved-by" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_rollback_returns_2_when_apply_metadata_is_missing(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _prepare_rollback_ready_state(project_root)
    _mutate_delta(project_root, lambda delta: delta.pop("apply"))

    exit_code, stdout, stderr = _rollback(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "is missing apply metadata" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_rollback_returns_2_when_history_does_not_match_delta(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _prepare_rollback_ready_state(project_root, applied_delta="SDP-OTHER")

    exit_code, stdout, stderr = _rollback(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "applied state history entry does not match delta id" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_rollback_returns_2_when_patch_exceeds_allow_list(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _prepare_rollback_ready_state(project_root)
    _mutate_delta(
        project_root,
        lambda delta: delta["rollback"]["project_state_restore"].update(
            {"project": {"current_phase": "bad"}}
        ),
    )

    exit_code, stdout, stderr = _rollback(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "unsupported fields: project" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_rollback_returns_2_when_delta_is_already_rolled_back(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _prepare_rollback_ready_state(project_root)
    _mutate_delta(project_root, lambda delta: delta.update({"status": "rolled_back"}))

    exit_code, stdout, stderr = _rollback(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "is not rollback-ready: rolled_back" in stderr
    _assert_project_state_not_modified(project_root)


def _copy_fixture(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    return project_root


def _prepare_rollback_ready_state(project_root: Path, applied_delta: str = "SDP-1003") -> None:
    state = _read_yaml(project_root / ".progress/state/project_state.yaml")
    implementation = state["state_dimensions"]["implementation"]
    implementation["maturity"] = "drafted"
    implementation["summary"] = "Implementation was advanced by a rollback-ready delta."
    implementation["evidence"] = [".progress/evidence/EV-1003-rollback-ready.yaml"]
    state["open_state_gaps"] = []
    state["aim_of_next_state"] = []
    _write_yaml(project_root / ".progress/state/project_state.yaml", state)

    history_path = project_root / ".progress/state/state_history.jsonl"
    with history_path.open("a", encoding="utf-8") as history_file:
        history_file.write(
            json.dumps(
                {
                    "state_version": "PS-1002",
                    "applied_delta": applied_delta,
                    "applied_at": "2026-05-17T22:45:00+08:00",
                    "applied_by": "human_user",
                    "summary": "Implementation moved from seed to drafted.",
                    "evidence_refs": [".progress/evidence/EV-1003-rollback-ready.yaml"],
                },
                separators=(",", ":"),
            )
        )
        history_file.write("\n")


def _rollback(project_root: Path, approved_by: str = "human_user") -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    exit_code = main(
        ["delta", "rollback", "SDP-1003", "--approved-by", approved_by],
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


def _read_history(project_root: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (project_root / ".progress/state/state_history.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    ]


def _read_delta(project_root: Path) -> dict[str, Any]:
    data = _read_yaml(project_root / DELTA_PATH)
    delta = data["state_delta_proposal"]
    assert isinstance(delta, dict)
    return delta


def _mutate_delta(project_root: Path, mutate: Any) -> None:
    path = project_root / DELTA_PATH
    data = _read_yaml(path)
    mutate(data["state_delta_proposal"])
    _write_yaml(path, data)


def _assert_project_state_not_modified(project_root: Path) -> None:
    state = _read_yaml(project_root / ".progress/state/project_state.yaml")
    implementation = state["state_dimensions"]["implementation"]
    assert implementation["maturity"] == "drafted"
    assert implementation["summary"] == "Implementation was advanced by a rollback-ready delta."
    assert state["open_state_gaps"] == []
    assert state["aim_of_next_state"] == []
    history_text = (project_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    )
    assert "ROLLBACK-SDP-1003" not in history_text
