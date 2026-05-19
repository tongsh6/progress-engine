from __future__ import annotations

import json
import shutil
from io import StringIO
from pathlib import Path
from typing import Any

import yaml

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"
DELTA_PATH = Path(".progress/deltas/SDP-1002-apply-ready-delta.yaml")


def test_delta_apply_updates_project_state_history_and_delta_metadata(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["delta", "apply", "SDP-1002", "--approved-by", "human_user"],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "State delta applied:",
        "- delta: SDP-1002",
        "- previous state: PS-1001",
        "- next state: PS-1002",
        "- project_state: .progress/state/project_state.yaml",
        "- state_history: .progress/state/state_history.jsonl",
        "",
        "Next:",
        "- progress state show",
        "- progress assess",
    ]

    state = _read_yaml(project_root / ".progress/state/project_state.yaml")
    implementation = state["state_dimensions"]["implementation"]
    assert implementation["maturity"] == "drafted"
    assert implementation["summary"] == "Implementation was advanced by an apply-ready delta."
    assert implementation["evidence"] == [".progress/evidence/EV-1002-apply-ready.yaml"]
    assert state["open_state_gaps"] == []
    assert state["aim_of_next_state"] == []

    history_entries = [
        json.loads(line)
        for line in (project_root / ".progress/state/state_history.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    ]
    assert history_entries[-1]["state_version"] == "PS-1002"
    assert history_entries[-1]["applied_delta"] == "SDP-1002"
    assert history_entries[-1]["applied_by"] == "human_user"
    assert history_entries[-1]["evidence_refs"] == [".progress/evidence/EV-1002-apply-ready.yaml"]

    delta = _read_delta(project_root)
    assert delta["status"] == "applied"
    assert delta["apply"]["applied_by"] == "human_user"
    assert delta["apply"]["previous_state_version"] == "PS-1001"
    assert delta["apply"]["next_state_version"] == "PS-1002"
    assert delta["apply"]["project_state_file"] == ".progress/state/project_state.yaml"


def test_delta_apply_returns_2_when_gate_is_not_approved(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _mutate_delta(project_root, lambda delta: delta["gate"].update({"decision": "pending"}))

    exit_code, stdout, stderr = _apply(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "is not human gate approved" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_apply_returns_2_when_approved_by_does_not_match_gate(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)

    exit_code, stdout, stderr = _apply(project_root, approved_by="other_user")

    assert exit_code == 2
    assert stdout == ""
    assert "gate approver does not match --approved-by" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_apply_returns_2_when_evidence_ref_is_missing(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    (project_root / ".progress/evidence/EV-1002-apply-ready.yaml").unlink()

    exit_code, stdout, stderr = _apply(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "missing evidence ref" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_apply_returns_2_when_acceptance_is_not_all_pass(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _mutate_delta(project_root, lambda delta: delta["acceptance_summary"].update({"not_tested": 1}))

    exit_code, stdout, stderr = _apply(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "cannot apply with fail or not_tested acceptance" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_apply_returns_2_when_patch_exceeds_allow_list(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _mutate_delta(
        project_root,
        lambda delta: delta["project_state_update"].update({"project": {"current_phase": "bad"}}),
    )

    exit_code, stdout, stderr = _apply(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "unsupported fields: project" in stderr
    _assert_project_state_not_modified(project_root)


def test_delta_apply_returns_2_when_delta_is_already_applied(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _mutate_delta(project_root, lambda delta: delta.update({"status": "applied"}))

    exit_code, stdout, stderr = _apply(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "is not apply-ready: applied" in stderr
    _assert_project_state_not_modified(project_root)


def _copy_fixture(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    return project_root


def _apply(project_root: Path, approved_by: str = "human_user") -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    exit_code = main(
        ["delta", "apply", "SDP-1002", "--approved-by", approved_by],
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


def _read_delta(project_root: Path) -> dict[str, Any]:
    data = _read_yaml(project_root / DELTA_PATH)
    delta = data["state_delta_proposal"]
    assert isinstance(delta, dict)
    return delta


def _mutate_delta(project_root: Path, mutate: Any) -> None:
    path = project_root / DELTA_PATH
    data = _read_yaml(path)
    mutate(data["state_delta_proposal"])
    with path.open("w", encoding="utf-8") as yaml_file:
        yaml.safe_dump(data, yaml_file, sort_keys=False, allow_unicode=True)


def _assert_project_state_not_modified(project_root: Path) -> None:
    state = _read_yaml(project_root / ".progress/state/project_state.yaml")
    implementation = state["state_dimensions"]["implementation"]
    assert implementation["maturity"] == "seed"
    assert implementation["summary"] == "Implementation is seeded."
    assert state["open_state_gaps"] == ["SG-1001"]
    assert state["aim_of_next_state"] == ["TS-1001"]
    history_text = (project_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    )
    assert "PS-1002" not in history_text
