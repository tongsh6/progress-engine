# progress_engine package

Current implemented slice:

<!-- progress-engine-cli-commands:start -->
```bash
progress init --project PROJECT_ID
progress intake --from FILE
progress assess
progress state show
progress state history
progress gaps list
progress target list
progress intervention list
progress run list
progress evidence list
progress verify list
progress delta list
progress delta apply SDP-ID --approved-by NAME
progress event list
```
<!-- progress-engine-cli-commands:end -->

`progress init --project PROJECT_ID` is the first controlled write slice. It creates a minimal `.progress/` skeleton only when `.progress/` does not already exist and refuses to overwrite existing state.

`progress intake --from FILE` is a controlled bootstrap write slice. It captures the initial intent into `.progress/artifacts/intent.md` and marks only the Project State intent dimension as `seed`.

`progress assess` is a read-only assessment slice. It summarizes the existing Project State maturity, the open gaps referenced by Project State, and the next targets referenced by Project State.

`progress delta apply SDP-ID --approved-by NAME` is a controlled human-gated write slice. It applies only an already approved State Delta Proposal, updates Project State through an allow-list patch, appends state history, and marks the proposal applied.

Read-only slices only read `.progress/state/project_state.yaml`, `.progress/state/state_history.jsonl`, `.progress/gaps/*.yaml`, `.progress/targets/*.yaml`, `.progress/interventions/*.yaml`, `.progress/runs/*.yaml`, `.progress/evidence/*.yaml`, `.progress/deltas/*.yaml`, and `.progress/events/*.yaml`. They do not generate evidence, generate verification artifacts, apply state deltas, refresh state, or propagate invalidation.
