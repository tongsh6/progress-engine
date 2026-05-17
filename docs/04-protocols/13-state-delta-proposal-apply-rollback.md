# State Delta 提案、应用与回滚协议

## 1. 目的

State Delta 是项目状态变化的正式声明。为了防止状态账本被污染，所有状态更新必须经过：

```text
Evidence → Verify → Propose → Gate → Apply → Reassess
```

## 2. State Delta 不是自动写入

Verifier 通过后生成的是：

```text
State Delta Proposal
```

不是直接修改 Project State。

## 3. 流程

```text
Run Completed
  ↓
Evidence Submitted
  ↓
Verification Passed / Partial
  ↓
State Delta Proposed
  ↓
Human or Policy Gate
  ↓
Apply / Reject
  ↓
Update Project State
  ↓
Record in Ledger
  ↓
Reassess
```

## 4. State Delta 模板

```yaml
state_delta:
  id: SD-001
  run_id: RUN-001
  intervention_id: IV-001
  verification_id: VR-001
  status: proposed
  proposed_at: 2026-05-16T10:00:00-07:00
  proposed_by: verifier
  primary_dimension: implementation
  secondary_dimensions:
    - quality
  before:
    implementation:
      maturity: unknown
      summary: "No intent intake command exists."
  after:
    implementation:
      maturity: drafted
      summary: "Intent intake command implemented for basic input."
  evidence_refs:
    - EV-001
  acceptance_summary:
    pass: 4
    fail: 0
    not_tested: 0
  remaining_gaps:
    - G-006
  emitted_events: []
  gate:
    required: true
    approved_by: null
    approved_at: null
  apply:
    applied_by: null
    applied_at: null
    previous_state_version: PS-0002
    next_state_version: null
  rollback:
    reversible: true
    rollback_delta_id: null
    rollback_steps:
      - "Restore project_state.yaml to PS-0002."
      - "Mark IV-001 as reopened."
```

## 5. Proposal / Apply 边界

`verify` 只能生成 State Delta Proposal。只有 `delta apply` 才能修改 Project State。任何工具实现不得把 verification pass 等同于 state updated。

## 6. Apply 条件

State Delta 只有满足以下条件才能 apply：

- Verification result 为 pass 或 pass_with_warnings。
- Evidence 映射完整。
- Scope check 通过。
- No silent deferral check 通过。
- 对应 automation policy 允许自动 apply，或人工确认。

## 7. Reject 条件

以下情况必须 reject：

- Evidence 缺失。
- 验收映射不完整。
- 修改超出 scope。
- 引入未批准架构变更。
- 产物自证循环。
- Verifier 与 Executor 是同一上下文。

## 8. Rollback

回滚不一定回滚代码，但必须回滚状态声明。

```bash
progress delta rollback SD-001
```

回滚后：

- Project State 恢复到 previous_state_version。
- State Delta 标记为 rolled_back。
- 生成 Change Event。
- 相关 Intervention 重新进入 reopened 或 stale。

## 9. State History

每次 apply 都写入：

```text
.progress/state/state_history.jsonl
```

字段：

```yaml
state_version: PS-0003
applied_delta: SD-001
applied_at: ...
applied_by: human | policy
summary: "Implementation state moved from unknown to drafted."
```

## 10. 重新评估

Apply 后必须运行 reassess：

```bash
progress assess --after-delta SD-001
```

因为一个 State Delta 可能产生新的 gap 或让旧 target 失效。
