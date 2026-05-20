from __future__ import annotations

import json
import shutil
from io import StringIO
from pathlib import Path
from typing import Any

import yaml

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"


def test_state_delta_lifecycle_pilot_apply_refresh_rollback_and_reject(
    tmp_path: Path,
) -> None:
    apply_root = _copy_fixture(tmp_path, "apply")

    exit_code, apply_out, apply_err = _run(
        ["delta", "apply", "SDP-1002", "--approved-by", "human_user"],
        apply_root,
    )

    assert exit_code == 0
    assert apply_err == ""
    assert "- next state: PS-1002" in apply_out
    apply_state = _read_yaml(apply_root / ".progress/state/project_state.yaml")
    assert apply_state["state_dimensions"]["implementation"]["maturity"] == "drafted"
    apply_history = _read_history(apply_root)
    assert apply_history[-1]["state_version"] == "PS-1002"
    assert apply_history[-1]["applied_delta"] == "SDP-1002"

    exit_code, refresh_out, refresh_err = _run(
        ["state", "refresh", "--after-delta", "SDP-1002"],
        apply_root,
    )

    assert exit_code == 0
    assert refresh_err == ""
    assert "- latest state: PS-1002" in refresh_out
    assert "- latest delta: SDP-1002" in refresh_out
    assert "- requested delta: SDP-1002 (matched)" in refresh_out

    rollback_root = _copy_fixture(tmp_path, "rollback")
    _prepare_rollback_ready_state(rollback_root)

    exit_code, rollback_out, rollback_err = _run(
        ["delta", "rollback", "SDP-1003", "--approved-by", "human_user"],
        rollback_root,
    )

    assert exit_code == 0
    assert rollback_err == ""
    assert "- new state: PS-1003" in rollback_out
    rollback_state = _read_yaml(rollback_root / ".progress/state/project_state.yaml")
    assert rollback_state["state_dimensions"]["implementation"]["maturity"] == "seed"
    rollback_history = _read_history(rollback_root)
    assert rollback_history[-1]["applied_delta"] == "ROLLBACK-SDP-1003"
    rollback_delta = _read_delta(rollback_root, "SDP-1003-rollback-ready-delta.yaml")
    assert rollback_delta["status"] == "rolled_back"

    reject_root = _copy_fixture(tmp_path, "reject")
    reject_state_before = (reject_root / ".progress/state/project_state.yaml").read_text(
        encoding="utf-8"
    )
    reject_history_before = (reject_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    )

    exit_code, reject_out, reject_err = _run(
        [
            "delta",
            "reject",
            "SDP-1004",
            "--approved-by",
            "human_user",
            "--reason",
            "Acceptance evidence failed verifier review.",
        ],
        reject_root,
    )

    assert exit_code == 0
    assert reject_err == ""
    assert "State delta rejected:" in reject_out
    reject_delta = _read_delta(reject_root, "SDP-1004-reject-ready-delta.yaml")
    assert reject_delta["status"] == "rejected"
    assert reject_delta["reject"]["previous_status"] == "accepted"
    assert reject_delta["reject"]["reason"] == "Acceptance evidence failed verifier review."
    assert (reject_root / ".progress/state/project_state.yaml").read_text(
        encoding="utf-8"
    ) == reject_state_before
    assert (reject_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    ) == reject_history_before


def _copy_fixture(tmp_path: Path, name: str) -> Path:
    project_root = tmp_path / name
    shutil.copytree(FIXTURE_ROOT, project_root)
    return project_root


def _run(args: list[str], cwd: Path) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    exit_code = main(args, cwd=cwd, stdout=stdout, stderr=stderr)
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


def _read_delta(project_root: Path, filename: str) -> dict[str, Any]:
    data = _read_yaml(project_root / ".progress" / "deltas" / filename)
    delta = data["state_delta_proposal"]
    assert isinstance(delta, dict)
    return delta


def _prepare_rollback_ready_state(project_root: Path) -> None:
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
                    "applied_delta": "SDP-1003",
                    "applied_at": "2026-05-17T22:45:00+08:00",
                    "applied_by": "human_user",
                    "summary": "Implementation moved from seed to drafted.",
                    "evidence_refs": [".progress/evidence/EV-1003-rollback-ready.yaml"],
                },
                separators=(",", ":"),
            )
        )
        history_file.write("\n")
