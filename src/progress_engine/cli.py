"""Command-line entry points for ProgressEngine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from progress_engine.assessment.assess import load_assessment, render_assessment
from progress_engine.capsule.context_capsule import (
    ContextCapsuleError,
    generate_context_capsule,
    render_context_capsule_success,
)
from progress_engine.deltas.delta_apply import (
    DeltaApplyError,
    apply_delta,
    render_delta_apply_success,
)
from progress_engine.deltas.delta_list import DeltaListError, load_deltas, render_delta_list
from progress_engine.deltas.delta_reject import (
    DeltaRejectError,
    reject_delta,
    render_delta_reject_success,
)
from progress_engine.deltas.delta_rollback import (
    DeltaRollbackError,
    render_delta_rollback_success,
    rollback_delta,
)
from progress_engine.events.event_list import EventListError, load_events, render_event_list
from progress_engine.gaps.gap_list import GapListError, load_open_gaps, render_gap_list
from progress_engine.evidence.evidence_list import (
    EvidenceListError,
    load_evidence,
    render_evidence_list,
)
from progress_engine.interventions.intervention_list import (
    InterventionListError,
    load_active_interventions,
    render_intervention_list,
)
from progress_engine.init.init_project import InitProjectError, init_project, render_init_success
from progress_engine.intake.intent_intake import (
    IntentIntakeError,
    capture_intent,
    render_intake_success,
)
from progress_engine.runs.run_list import RunListError, load_active_runs, render_run_list
from progress_engine.runs.run_start import (
    RunStartError,
    render_run_start_success,
    start_run,
)
from progress_engine.state.project_state import (
    ProjectStateError,
    load_project_state,
    render_state_summary,
)
from progress_engine.state.state_history import (
    StateHistoryError,
    load_state_history,
    render_state_history,
)
from progress_engine.state.state_refresh import (
    StateRefreshError,
    load_state_refresh,
    render_state_refresh,
)
from progress_engine.targets.target_list import TargetListError, load_next_targets, render_target_list
from progress_engine.verification.verify_list import (
    VerificationListError,
    load_verification_reviews,
    render_verification_reviews,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="progress")
    subcommands = parser.add_subparsers(dest="command", required=True)

    init_parser = subcommands.add_parser("init", help="Initialize a ProgressEngine project.")
    init_parser.add_argument("--project", required=True, help="Project id for the new state ledger.")

    intake_parser = subcommands.add_parser("intake", help="Capture project intent.")
    intake_parser.add_argument(
        "--from",
        dest="source",
        required=True,
        help="Intent Markdown file to capture.",
    )

    subcommands.add_parser("assess", help="Show a read-only project assessment summary.")

    state_parser = subcommands.add_parser("state", help="Read project state.")
    state_subcommands = state_parser.add_subparsers(dest="state_command", required=True)
    state_subcommands.add_parser("show", help="Show current project state summary.")
    state_subcommands.add_parser("history", help="Show state history summary.")
    state_refresh_parser = state_subcommands.add_parser(
        "refresh",
        help="Show read-only state reconciliation after a delta.",
    )
    state_refresh_parser.add_argument(
        "--after-delta",
        help="Optional State Delta Proposal id expected to match latest history.",
    )

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

    capsule_parser = subcommands.add_parser("capsule", help="Generate a Context Capsule.")
    capsule_parser.add_argument(
        "--intervention",
        required=True,
        help="Intervention id to render into a prompt-only Context Capsule.",
    )

    run_parser = subcommands.add_parser("run", help="Read runs.")
    run_subcommands = run_parser.add_subparsers(dest="run_command", required=True)
    run_subcommands.add_parser("list", help="List open runs.")
    run_start_parser = run_subcommands.add_parser(
        "start",
        help="Start a prompt-only Run for an intervention.",
    )
    run_start_parser.add_argument(
        "--intervention",
        required=True,
        help="Intervention id to start as a prompt-only Run.",
    )
    run_start_parser.add_argument(
        "--mode",
        required=True,
        help="Run execution mode. v0.1 supports prompt-only.",
    )

    evidence_parser = subcommands.add_parser("evidence", help="Read evidence.")
    evidence_subcommands = evidence_parser.add_subparsers(dest="evidence_command", required=True)
    evidence_subcommands.add_parser("list", help="List evidence objects.")

    verify_parser = subcommands.add_parser("verify", help="Read verification reviews.")
    verify_subcommands = verify_parser.add_subparsers(dest="verify_command", required=True)
    verify_subcommands.add_parser("list", help="List verification review summaries.")

    delta_parser = subcommands.add_parser("delta", help="Read state delta proposals.")
    delta_subcommands = delta_parser.add_subparsers(dest="delta_command", required=True)
    delta_subcommands.add_parser("list", help="List state delta proposals.")
    delta_apply_parser = delta_subcommands.add_parser(
        "apply",
        help="Apply a human-approved state delta proposal.",
    )
    delta_apply_parser.add_argument("delta_id", help="State Delta Proposal id to apply.")
    delta_apply_parser.add_argument(
        "--approved-by",
        required=True,
        help="Human approver recorded for this apply operation.",
    )
    delta_rollback_parser = delta_subcommands.add_parser(
        "rollback",
        help="Rollback a human-approved applied state delta proposal.",
    )
    delta_rollback_parser.add_argument("delta_id", help="State Delta Proposal id to rollback.")
    delta_rollback_parser.add_argument(
        "--approved-by",
        required=True,
        help="Human approver recorded for this rollback operation.",
    )
    delta_reject_parser = delta_subcommands.add_parser(
        "reject",
        help="Reject a human-approved state delta proposal.",
    )
    delta_reject_parser.add_argument("delta_id", help="State Delta Proposal id to reject.")
    delta_reject_parser.add_argument(
        "--approved-by",
        required=True,
        help="Human approver recorded for this reject operation.",
    )
    delta_reject_parser.add_argument(
        "--reason",
        required=True,
        help="Human-readable reason recorded for this reject operation.",
    )

    event_parser = subcommands.add_parser("event", help="Read change events.")
    event_subcommands = event_parser.add_subparsers(dest="event_command", required=True)
    event_subcommands.add_parser("list", help="List change events.")

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

    if args.command == "init":
        root = cwd or Path.cwd()
        try:
            created = init_project(root, args.project)
        except InitProjectError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_init_success(args.project, created, root), file=out)
        return 0

    if args.command == "intake":
        root = cwd or Path.cwd()
        try:
            artifact_path = capture_intent(root, Path(args.source))
        except IntentIntakeError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_intake_success(artifact_path), file=out)
        return 0

    if args.command == "assess":
        root = cwd or Path.cwd()
        try:
            assessment = load_assessment(root)
        except (ProjectStateError, GapListError, TargetListError) as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_assessment(assessment), file=out)
        return 0

    if args.command == "state" and args.state_command == "show":
        root = cwd or Path.cwd()
        try:
            state = load_project_state(root)
        except ProjectStateError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_state_summary(state), file=out)
        return 0

    if args.command == "state" and args.state_command == "history":
        root = cwd or Path.cwd()
        try:
            history = load_state_history(root)
        except StateHistoryError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_state_history(history), file=out)
        return 0

    if args.command == "state" and args.state_command == "refresh":
        root = cwd or Path.cwd()
        try:
            refresh = load_state_refresh(root, args.after_delta)
        except (
            ProjectStateError,
            StateHistoryError,
            GapListError,
            TargetListError,
            StateRefreshError,
        ) as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_state_refresh(refresh), file=out)
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

    if args.command == "capsule":
        root = cwd or Path.cwd()
        try:
            result = generate_context_capsule(root, args.intervention)
        except (ContextCapsuleError, ProjectStateError, StateHistoryError) as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_context_capsule_success(result), file=out)
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

    if args.command == "run" and args.run_command == "start":
        root = cwd or Path.cwd()
        try:
            result = start_run(root, args.intervention, args.mode)
        except (RunStartError, ProjectStateError, StateHistoryError) as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_run_start_success(result), file=out)
        return 0

    if args.command == "evidence" and args.evidence_command == "list":
        root = cwd or Path.cwd()
        try:
            evidence = load_evidence(root)
        except EvidenceListError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_evidence_list(evidence), file=out)
        return 0

    if args.command == "verify" and args.verify_command == "list":
        root = cwd or Path.cwd()
        try:
            reviews = load_verification_reviews(root)
        except VerificationListError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_verification_reviews(reviews), file=out)
        return 0

    if args.command == "delta" and args.delta_command == "list":
        root = cwd or Path.cwd()
        try:
            deltas = load_deltas(root)
        except DeltaListError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_delta_list(deltas), file=out)
        return 0

    if args.command == "delta" and args.delta_command == "apply":
        root = cwd or Path.cwd()
        try:
            result = apply_delta(root, args.delta_id, args.approved_by)
        except (DeltaApplyError, ProjectStateError, StateHistoryError) as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_delta_apply_success(result), file=out)
        return 0

    if args.command == "delta" and args.delta_command == "rollback":
        root = cwd or Path.cwd()
        try:
            result = rollback_delta(root, args.delta_id, args.approved_by)
        except (DeltaRollbackError, ProjectStateError, StateHistoryError) as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_delta_rollback_success(result), file=out)
        return 0

    if args.command == "delta" and args.delta_command == "reject":
        root = cwd or Path.cwd()
        try:
            result = reject_delta(root, args.delta_id, args.approved_by, args.reason)
        except DeltaRejectError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_delta_reject_success(result), file=out)
        return 0

    if args.command == "event" and args.event_command == "list":
        root = cwd or Path.cwd()
        try:
            events = load_events(root)
        except EventListError as exc:
            print(f"error: {exc}", file=err)
            return 2
        print(render_event_list(events), file=out)
        return 0

    parser.error("unsupported command")
    return 2
