"""Command-line entry points for ProgressEngine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from progress_engine.gaps.gap_list import GapListError, load_open_gaps, render_gap_list
from progress_engine.interventions.intervention_list import (
    InterventionListError,
    load_active_interventions,
    render_intervention_list,
)
from progress_engine.runs.run_list import RunListError, load_active_runs, render_run_list
from progress_engine.state.project_state import (
    ProjectStateError,
    load_project_state,
    render_state_summary,
)
from progress_engine.targets.target_list import TargetListError, load_next_targets, render_target_list


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="progress")
    subcommands = parser.add_subparsers(dest="command", required=True)

    state_parser = subcommands.add_parser("state", help="Read project state.")
    state_subcommands = state_parser.add_subparsers(dest="state_command", required=True)
    state_subcommands.add_parser("show", help="Show current project state summary.")

    gaps_parser = subcommands.add_parser("gaps", help="Read state gaps.")
    gaps_subcommands = gaps_parser.add_subparsers(dest="gaps_command", required=True)
    gaps_subcommands.add_parser("list", help="List open state gaps.")

    target_parser = subcommands.add_parser("target", help="Read target states.")
    target_subcommands = target_parser.add_subparsers(dest="target_command", required=True)
    target_subcommands.add_parser("list", help="List next target states.")

    intervention_parser = subcommands.add_parser("intervention", help="Read interventions.")
    intervention_subcommands = intervention_parser.add_subparsers(
        dest="intervention_command",
        required=True,
    )
    intervention_subcommands.add_parser("list", help="List incomplete interventions.")

    run_parser = subcommands.add_parser("run", help="Read runs.")
    run_subcommands = run_parser.add_subparsers(dest="run_command", required=True)
    run_subcommands.add_parser("list", help="List open runs.")

    return parser


def main(
    argv: list[str] | None = None,
    *,
    cwd: Path | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    out = stdout or sys.stdout
    err = stderr or sys.stderr
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "state" and args.state_command == "show":
        root = cwd or Path.cwd()
        try:
            state = load_project_state(root)
        except ProjectStateError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_state_summary(state), file=out)
        return 0

    if args.command == "gaps" and args.gaps_command == "list":
        root = cwd or Path.cwd()
        try:
            state = load_project_state(root)
            gaps = load_open_gaps(root, state)
        except (ProjectStateError, GapListError) as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_gap_list(gaps), file=out)
        return 0

    if args.command == "target" and args.target_command == "list":
        root = cwd or Path.cwd()
        try:
            state = load_project_state(root)
            targets = load_next_targets(root, state)
        except (ProjectStateError, TargetListError) as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_target_list(targets), file=out)
        return 0

    if args.command == "intervention" and args.intervention_command == "list":
        root = cwd or Path.cwd()
        try:
            interventions = load_active_interventions(root)
        except InterventionListError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_intervention_list(interventions), file=out)
        return 0

    if args.command == "run" and args.run_command == "list":
        root = cwd or Path.cwd()
        try:
            runs = load_active_runs(root)
        except RunListError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_run_list(runs), file=out)
        return 0

    parser.error("unsupported command")
    return 2
