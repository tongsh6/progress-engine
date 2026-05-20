# progress_engine package

Current implemented slice:

<!-- progress-engine-cli-commands:start -->
```bash
progress init --project PROJECT_ID
progress intake --from FILE
progress assess
progress state show
progress state history
progress state refresh [--after-delta SDP-ID]
progress gaps list
progress target list
progress intervention list
progress capsule --intervention IV-ID
progress run start --intervention IV-ID --mode prompt-only
progress run list
progress evidence list
progress verify list
progress delta list
progress delta apply SDP-ID --approved-by NAME
progress delta rollback SDP-ID --approved-by NAME
progress delta reject SDP-ID --approved-by NAME --reason TEXT
progress event list
```
<!-- progress-engine-cli-commands:end -->

`progress init --project PROJECT_ID` is the first controlled write slice. It creates a minimal `.progress/` skeleton only when `.progress/` does not already exist and refuses to overwrite existing state.

`progress intake --from FILE` is a controlled bootstrap write slice. It captures the initial intent into `.progress/artifacts/intent.md` and marks only the Project State intent dimension as `seed`.

`progress assess` is a read-only assessment slice. It summarizes the existing Project State maturity, the open gaps referenced by Project State, and the next targets referenced by Project State.

`progress delta apply SDP-ID --approved-by NAME` is a controlled human-gated write slice. It applies only an already approved State Delta Proposal, updates Project State through an allow-list patch, appends state history, and marks the proposal applied.

`progress delta rollback SDP-ID --approved-by NAME` is a controlled human-gated write slice. It rolls back only the latest applied reversible State Delta Proposal, restores Project State through an allow-list patch, appends state history, and marks the proposal rolled_back.

`progress delta reject SDP-ID --approved-by NAME --reason TEXT` is a controlled human-gated proposal lifecycle write slice. It rejects only a proposed or accepted State Delta Proposal and does not modify Project State or state history.

`progress capsule --intervention IV-ID` is a prompt-only Context Capsule write slice. It reads the existing Project State, State History, Intervention, and Target State, then writes only `.progress/context_capsules/{IV-ID}-context-capsule.md`. It does not call a model, execute the intervention, create evidence, apply state deltas, or modify Project State / state history.

`progress run start --intervention IV-ID --mode prompt-only` is a controlled prompt-only Run lifecycle write slice. It creates an active Run object and generates or reuses the matching Context Capsule. It does not call a model, execute the intervention, create evidence, apply state deltas, or modify Project State / state history.

Read-only slices only read `.progress/state/project_state.yaml`, `.progress/state/state_history.jsonl`, `.progress/gaps/*.yaml`, `.progress/targets/*.yaml`, `.progress/interventions/*.yaml`, `.progress/runs/*.yaml`, `.progress/evidence/*.yaml`, `.progress/deltas/*.yaml`, and `.progress/events/*.yaml`. They do not generate evidence, generate verification artifacts, apply state deltas, write refreshed state, or propagate invalidation.

`progress state refresh [--after-delta SDP-ID]` is a read-only reconciliation slice. It reports the current Project State, latest State History entry, open gaps, and next targets after an apply or rollback, but does not write refreshed state.
