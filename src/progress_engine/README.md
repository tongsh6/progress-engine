# progress_engine package

Current implemented slice:

```bash
progress state show
progress gaps list
progress target list
progress intervention list
progress run list
```

These slices only read `.progress/state/project_state.yaml`, `.progress/gaps/*.yaml`, `.progress/targets/*.yaml`, `.progress/interventions/*.yaml`, and `.progress/runs/*.yaml`. They do not modify `.progress/`, generate evidence, or apply state deltas.
