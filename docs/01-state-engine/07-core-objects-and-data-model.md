# 核心对象与数据模型

## 1. 对象总览

ProgressEngine 的核心对象不是 Task，而是 Project State 及其变化。

```text
Intent
ProjectState
StateDimension
StateGap
TargetState
Intervention
ContextCapsule
Run
Evidence
Verification
StateDelta
ChangeEvent
Ledger
```

## 2. ProjectState

```yaml
project_state:
  project_id: progressengine
  version: PS-0004
  updated_at: 2026-05-16T10:00:00-07:00
  dimensions:
    intent:
      maturity: accepted
      progress: complete
      summary: "Project direction accepted."
      evidence_refs: [EV-001]
      gaps: []
    product:
      maturity: reviewed
      progress: partial
      summary: "MVP scope reviewed; success metrics need refinement."
      evidence_refs: [EV-002]
      gaps: [G-003]
```

## 3. StateGap

```yaml
state_gap:
  id: G-003
  dimension: product
  severity: high
  current_state: "Success metrics are generic."
  desired_state: "MVP success metrics are measurable and tied to first user workflow."
  evidence_refs: [EV-002]
  impact:
    - "Cannot verify MVP adoption."
    - "QA cannot create release acceptance criteria."
  suggested_targets: [TS-003]
```

## 4. TargetState

```yaml
target_state:
  id: TS-003
  dimension: product
  from_maturity: reviewed
  to_maturity: accepted
  description: "MVP success metrics accepted."
  why_now:
    - "Release readiness depends on measurable success criteria."
  score:
    risk_reduction: 4
    downstream_unlock: 4
    effort: 2
  required_interventions: [IV-007]
  gate_required: true
```

## 5. Intervention

Intervention 是推进动作。Task 只是可执行粒度的 Intervention。

```yaml
intervention:
  id: IV-007
  type: product_clarification
  target_state: TS-003
  dimension: product
  title: "Define measurable MVP success metrics"
  goal: "Turn generic MVP goals into measurable success metrics."
  in_scope:
    - "Define 3-5 success metrics."
    - "Map metrics to release gate."
  out_of_scope:
    - "Do not change MVP feature scope."
  inputs:
    - .progress/artifacts/prd.md
  outputs:
    - .progress/artifacts/prd.md
  acceptance:
    - "Each metric has a measurable threshold."
    - "Each metric maps to a user workflow or system behavior."
  evidence_required:
    - artifact_review
    - checklist_result
  automation:
    mode: supervised
```

## 6. Run

Run 是一次隔离上下文执行。

```yaml
run:
  id: RUN-20260516-001
  intervention_id: IV-007
  status: verifying
  execution_session:
    fresh_context: true
    transcript_carried_forward: false
  verification_session:
    fresh_context: true
  outputs:
    context_capsule: context_capsule.md
    evidence: evidence.yaml
    state_delta_proposal: state_delta_proposal.yaml
```

## 7. Evidence

Evidence 是状态变化证据。

```yaml
evidence:
  id: EV-010
  run_id: RUN-20260516-001
  evidence_type: artifact_review
  claims:
    - dimension: product
      before: "Success metrics generic."
      after: "Success metrics measurable."
      acceptance_mapping:
        - criterion: "Each metric has threshold."
          status: pass
          evidence_ref: ".progress/artifacts/prd.md#success-metrics"
  commands_run: []
  artifacts_changed:
    - .progress/artifacts/prd.md
  reviewer:
    type: product_critic
    result: pass_with_notes
```

## 8. StateDelta

StateDelta 是经过验证后可应用到 Project State 的变化提案。

```yaml
state_delta:
  id: SD-010
  run_id: RUN-20260516-001
  verification_id: VR-010
  status: proposed
  proposed_by: verifier
  proposed_at: 2026-05-16T10:20:00-07:00
  primary_dimension: product
  secondary_dimensions:
    - quality
  before:
    product:
      maturity: reviewed
      summary: "Success metrics weak."
  after:
    product:
      maturity: accepted
      summary: "Success metrics accepted."
  evidence_refs: [EV-010]
  remaining_gaps:
    - G-011
  emitted_events: []
  gate:
    required: true
    approved_by: null
    approved_at: null
  apply:
    applied_by: null
    applied_at: null
    previous_state_version: PS-0003
    next_state_version: null
  rollback:
    reversible: true
    rollback_delta_id: null
```

## 9. ChangeEvent

```yaml
change_event:
  id: EVT-001
  type: implementation_finding
  severity: high
  source:
    run_id: RUN-20260516-002
    intervention_id: IV-008
  summary: "Implementation revealed that Context Capsule requires artifact priority rules."
  affected_dimensions:
    - system_design
    - quality
  affected_artifacts:
    - id: technical_design
      effect: reopen
  invalidates:
    interventions: [IV-009]
    state_claims: [SD-004]
  emitted_gaps: [G-012]
  emitted_targets: [TS-009]
  emitted_interventions: [IV-014]
  requires_human_review: true
```

## 10. ID 约定

| 对象 | 前缀 |
|---|---|
| Project State | PS |
| State Gap | G |
| Target State | TS |
| Intervention | IV |
| Run | RUN |
| Evidence | EV |
| Verification | VR |
| State Delta | SD |
| Change Event | EVT |
| Architecture Decision | ADR |
| Risk | R |

## 11. 状态转移

### Intervention 状态

```text
proposed → approved → ready → running → implemented → verifying → verified → closed
                                             ↓              ↓
                                          blocked        rejected
                                             ↓
                                      stale / needs_review / reopened
```

### StateDelta 状态

```text
proposed → approved → applied
    ↓          ↓          ↓
 rejected   expired   rolled_back
```

### Artifact 状态

```text
seed → drafted → reviewed → accepted → validated
                   ↓           ↓
                 reopened    stale → superseded
```
