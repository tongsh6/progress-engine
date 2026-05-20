from __future__ import annotations

import shutil
from io import StringIO
from pathlib import Path
from typing import Any

import yaml
import pytest

from progress_engine.cli import main


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "minimal_progress_project"
DELTA_PATH = Path(".progress/deltas/SDP-1004-reject-ready-delta.yaml")


def test_delta_reject_updates_only_delta_metadata(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    initial_state = (project_root / ".progress/state/project_state.yaml").read_text(
        encoding="utf-8"
    )
    initial_history = (project_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "delta",
            "reject",
            "SDP-1004",
            "--approved-by",
            "human_user",
            "--reason",
            "Acceptance evidence failed verifier review.",
        ],
        cwd=project_root,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert stdout.getvalue().splitlines() == [
        "State delta rejected:",
        "- delta: SDP-1004",
        "- rejected by: human_user",
        "- reason: Acceptance evidence failed verifier review.",
        "- proposal: .progress/deltas/SDP-1004-reject-ready-delta.yaml",
        "",
        "Next:",
        "- progress delta list",
        "- progress assess",
    ]

    delta = _read_delta(project_root)
    assert delta["status"] == "rejected"
    assert delta["reject"]["rejected_by"] == "human_user"
    assert delta["reject"]["reason"] == "Acceptance evidence failed verifier review."
    assert delta["reject"]["previous_status"] == "accepted"
    assert isinstance(delta["reject"]["rejected_at"], str)

    assert (project_root / ".progress/state/project_state.yaml").read_text(
        encoding="utf-8"
    ) == initial_state
    assert (project_root / ".progress/state/state_history.jsonl").read_text(
        encoding="utf-8"
    ) == initial_history


def test_delta_reject_returns_2_when_delta_is_missing(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)

    exit_code, stdout, stderr = _reject(project_root, delta_id="SDP-9999")

    assert exit_code == 2
    assert stdout == ""
    assert "missing State Delta Proposal id: SDP-9999" in stderr
    _assert_delta_not_rejected(project_root)


@pytest.mark.parametrize("status", ["applied", "rolled_back", "rejected", "unknown"])
def test_delta_reject_returns_2_when_delta_status_is_not_allowed(
    tmp_path: Path,
    status: str,
) -> None:
    project_root = _copy_fixture(tmp_path)
    _mutate_delta(project_root, lambda delta: delta.update({"status": status}))

    exit_code, stdout, stderr = _reject(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert f"is not reject-ready: {status}" in stderr
    _assert_delta_not_rejected(project_root)


def test_delta_reject_returns_2_when_gate_is_not_approved(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _mutate_delta(
        project_root,
        lambda delta: delta["reject"]["gate"].update({"decision": "pending"}),
    )

    exit_code, stdout, stderr = _reject(project_root)

    assert exit_code == 2
    assert stdout == ""
    assert "reject gate is not approved" in stderr
    _assert_delta_not_rejected(project_root)


def test_delta_reject_returns_2_when_approved_by_does_not_match_gate(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)

    exit_code, stdout, stderr = _reject(project_root, approved_by="other_user")

    assert exit_code == 2
    assert stdout == ""
    assert "reject gate approver does not match --approved-by" in stderr
    _assert_delta_not_rejected(project_root)


def test_delta_reject_returns_2_when_reason_is_empty(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)

    exit_code, stdout, stderr = _reject(project_root, reason="   ")

    assert exit_code == 2
    assert stdout == ""
    assert "--reason must be a non-empty value" in stderr
    _assert_delta_not_rejected(project_root)


def _copy_fixture(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    return project_root


def _reject(
    project_root: Path,
    *,
    delta_id: str = "SDP-1004",
    approved_by: str = "human_user",
    reason: str = "Acceptance evidence failed verifier review.",
) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    exit_code = main(
        [
            "delta",
            "reject",
            delta_id,
            "--approved-by",
            approved_by,
            "--reason",
            reason,
        ],
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


def _assert_delta_not_rejected(project_root: Path) -> None:
    delta = _read_delta(project_root)
    assert delta["status"] != "rejected" or "rejected_by" not in delta["reject"]
