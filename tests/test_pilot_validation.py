from __future__ import annotations

from io import StringIO
from pathlib import Path

import yaml

from progress_engine.cli import main


ROOT = Path(__file__).resolve().parents[1]
PILOT_INTENT = ROOT / "examples" / "initial-project" / "intent.md"


def run_cli(args: list[str], cwd: Path) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    exit_code = main(args, cwd=cwd, stdout=stdout, stderr=stderr)
    return exit_code, stdout.getvalue(), stderr.getvalue()


def test_v0_1_pilot_validation_scenario_bootstraps_and_reads_state(tmp_path: Path) -> None:
    exit_code, stdout, stderr = run_cli(
        ["init", "--project", "pilot-initial-project"],
        tmp_path,
    )

    assert exit_code == 0
    assert stderr == ""
    assert "Initialized ProgressEngine project: pilot-initial-project" in stdout

    exit_code, stdout, stderr = run_cli(
        ["intake", "--from", str(PILOT_INTENT)],
        tmp_path,
    )

    assert exit_code == 0
    assert stderr == ""
    assert stdout.splitlines() == [
        "Captured intent: .progress/artifacts/intent.md",
        "Updated Project State intent maturity: seed",
        "Next:",
        "- progress state show",
    ]

    intent_artifact = tmp_path / ".progress" / "artifacts" / "intent.md"
    assert intent_artifact.read_text(encoding="utf-8") == PILOT_INTENT.read_text(
        encoding="utf-8"
    )

    state_path = tmp_path / ".progress" / "state" / "project_state.yaml"
    state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    assert state["project"]["id"] == "pilot-initial-project"
    assert state["state_dimensions"]["intent"]["maturity"] == "seed"
    assert ".progress/artifacts/intent.md" in state["state_dimensions"]["intent"]["evidence"]

    exit_code, state_show, stderr = run_cli(["state", "show"], tmp_path)

    assert exit_code == 0
    assert stderr == ""
    assert state_show.splitlines() == [
        "Project: pilot-initial-project",
        "Phase: initialized",
        "Dimensions:",
        "- intent: seed",
        "- product: unknown",
        "- design: unknown",
        "- architecture: unknown",
        "- implementation: unknown",
        "- quality: unknown",
        "- delivery: unknown",
        "- knowledge: unknown",
        "Open gaps:",
        "- none",
        "Next target:",
        "- none",
    ]

    exit_code, assessment, stderr = run_cli(["assess"], tmp_path)

    assert exit_code == 0
    assert stderr == ""
    assert "Assessment:" in assessment
    assert "Project: pilot-initial-project" in assessment
    assert "- intent: seed" in assessment
    assert "Open gaps:\n- none" in assessment
    assert "Next targets:\n- none" in assessment
