# Change Event 影响分析与失效传播

## 1. 目的

项目是螺旋式推进。实现、验证、反馈和外部变化都会让已有状态失效。Change Event 用来捕获这些变化，并触发影响分析、失效传播和重新推进。

## 2. Change Event 类型

| 类型 | 来源 | 可能影响 |
|---|---|---|
| new_intent | 用户新增意图 | Intent / Product / Planning |
| scope_change | MVP 范围变化 | Product / UX / Quality / Implementation |
| implementation_finding | 实现中发现设计缺口 | System / Architecture / Planning |
| verification_failure | 验证失败 | Quality / Implementation / State Delta |
| quality_gap | QA 发现缺口 | Quality / Implementation |
| architecture_conflict | 架构冲突 | Architecture / System / ADR |
| task_too_large | 上下文或范围超限 | Planning / Meta |
| user_feedback | 用户反馈 | Product / UX / Roadmap |
| release_blocker | 发布阻断 | Delivery / Quality |
| external_change | 依赖、API、环境变化 | Architecture / Implementation |
| human_override | 人工方向调整 | 多维度 |

## 3. 事件结构

```yaml
change_event:
  id: EVT-001
  type: implementation_finding
  severity: high
  source:
    run_id: RUN-001
    intervention_id: IV-001
  summary: "Context Capsule generation requires artifact priority rules."
  affected_dimensions:
    - system_design
    - quality
  affected_artifacts:
    - id: technical_design
      current_version: v2
      effect: reopen
  invalidates:
    interventions:
      - IV-009
    state_claims:
      - SD-004
    target_states:
      - TS-005
  emitted_gaps:
    - G-012
  emitted_targets:
    - TS-009
  emitted_interventions:
    - IV-014
  requires_human_review: true
```

## 4. 影响分析流程

```text
Capture Event
  ↓
Classify Event
  ↓
Identify Affected Dimensions
  ↓
Identify Affected Artifacts
  ↓
Identify Invalidated State Claims
  ↓
Mark Affected Interventions stale / blocked
  ↓
Emit New Gaps
  ↓
Propose New Target States
  ↓
Plan New Interventions
```

## 5. 失效传播规则

### 5.1 Artifact reopened

当实现发现架构文档不足时：

```yaml
artifact_effect: reopen
```

意味着：

- artifact 状态从 accepted/reviewed 变为 reopened。
- 依赖该 artifact 的目标状态需要复核。
- 相关 Intervention 进入 stale 或 needs_review。

### 5.2 Artifact superseded

当新版本完全替代旧版本时：

```yaml
artifact_effect: supersede
```

意味着：

- 旧 artifact 不再作为事实源。
- 旧任务引用需要重算。

### 5.3 State claim invalidated

如果某个 State Delta 的证据被推翻：

```yaml
invalidates:
  state_claims: [SD-004]
```

必须：

- 标记对应 Project State 维度为 stale。
- 生成 reassessment Intervention。

## 6. 示例：实现中发现系统设计缺口

当前 Intervention：

```text
IV-008 Implement Context Capsule Builder
```

发现：

```text
artifact 优先级未定义，导致 capsule 内容不可控。
```

系统应生成：

```text
EVT-002 implementation_finding
G-014 system design gap
TS-010 artifact priority rule accepted
IV-020 define artifact priority rules
```

同时：

```text
IV-008 blocked
technical_design reopened
相关 quality tests stale
```

## 7. 禁止行为

- 不允许在实现中临时发明规则并继续。
- 不允许忽略影响继续执行下游任务。
- 不允许口头说明“后面再补”。
- 不允许 Change Event 不落账。
