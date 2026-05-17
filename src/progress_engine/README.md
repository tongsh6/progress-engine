# progress_engine package

Current implemented slice:

```bash
progress state show
progress gaps list
progress target list
progress intervention list
progress run list
progress evidence list
```

These slices only read `.progress/state/project_state.yaml`, `.progress/gaps/*.yaml`, `.progress/targets/*.yaml`, `.progress/interventions/*.yaml`, `.progress/runs/*.yaml`, and `.progress/evidence/*.yaml`. They do not modify `.progress/`, generate evidence, run verification, or apply state deltas.
