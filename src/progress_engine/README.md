# progress_engine package

Current implemented slice:

```bash
progress state show
progress state history
progress gaps list
progress target list
progress intervention list
progress run list
progress evidence list
progress verify list
progress delta list
progress event list
```

These slices only read `.progress/state/project_state.yaml`, `.progress/state/state_history.jsonl`, `.progress/gaps/*.yaml`, `.progress/targets/*.yaml`, `.progress/interventions/*.yaml`, `.progress/runs/*.yaml`, `.progress/evidence/*.yaml`, `.progress/deltas/*.yaml`, and `.progress/events/*.yaml`. They do not modify `.progress/`, generate evidence, generate verification artifacts, apply state deltas, refresh state, or propagate invalidation.
