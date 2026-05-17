# 系统架构与模块边界

## 1. 架构目标

ProgressEngine 的架构目标：

- repo-native：项目事实源在仓库内。
- CLI-first：先用命令行完成闭环。
- prompt-only friendly：第一版不强依赖模型 API。
- state-driven：所有执行都服务项目状态变化。
- fresh-context：每个推进动作有独立上下文。
- evidence-backed：状态变化必须证据化。
- reversible：状态账本支持提案、应用、回滚。

## 2. 顶层模块

```text
ProgressEngine
  ├── State Engine
  ├── State Reconciler
  ├── Outcome Planner
  ├── Intervention Planner
  ├── Context Capsule Builder
  ├── Run Orchestrator
  ├── Evidence Verifier
  ├── Change Event Engine
  ├── State Ledger
  ├── Automation Policy Engine
  └── Adapter Layer
```

## 3. 模块职责

| 模块 | 职责 |
|---|---|
| State Engine | 管理 Project State、State Dimension、Maturity |
| State Reconciler | 调和文档、代码、git、ledger、runs，判断真实状态 |
| Outcome Planner | 根据 State Gap 选择下一步 Target State |
| Intervention Planner | 将 Target State 转成推进动作 |
| Context Capsule Builder | 为每个 Intervention 生成独立上下文 |
| Run Orchestrator | 管理 Run 生命周期，确保新会话执行 |
| Evidence Verifier | 验证状态变化证据，防假完成 |
| Change Event Engine | 捕获变化、失败、反馈、失效事件 |
| State Ledger | 存储状态、证据、决策、风险、Delta |
| Automation Policy Engine | 判断哪些动作可自动，哪些必须人工 gate |
| Adapter Layer | 对接 ChatGPT/Codex/Claude Code/本地命令/API |

## 4. 推荐目录结构

```text
.progress/
  project.yaml

  state/
    project_state.yaml
    state_history.jsonl
    state_gaps.yaml
    target_states.yaml

  artifacts/
    intent.md
    product_brief.md
    prd.md
    ux_design.md
    system_design.md
    technical_design.md
    quality_plan.md
    release_strategy.md

  decisions/
    ADR-0001.md
    ADR-0002.md

  interventions/
    IV-001.yaml
    IV-002.yaml

  pools/
    intent.yaml
    product.yaml
    ux.yaml
    system.yaml
    architecture.yaml
    implementation.yaml
    quality.yaml
    docs.yaml
    release.yaml
    feedback.yaml
    meta.yaml

  runs/
    RUN-YYYYMMDD-001/
      run.yaml
      context_capsule.md
      plan.md
      output.md
      evidence.yaml
      verification.md
      state_delta_proposal.yaml
      handoff.md

  events/
    change_events.jsonl
    invalidation_log.jsonl

  ledger/
    assumptions.yaml
    risks.yaml
    findings.yaml
    feedback.yaml
    decisions.yaml
    state_deltas.yaml

  policies/
    automation_policy.yaml
    maturity_rules.yaml
    verification_rules.yaml

  reviews/
    product_review_001.md
    architecture_review_001.md
    quality_review_001.md
```

## 5. 数据流

```text
Artifacts + Ledger + Git State
  ↓
State Reconciler
  ↓
Project State + State Gaps
  ↓
Outcome Planner
  ↓
Target State
  ↓
Intervention Planner
  ↓
Intervention Proposal
  ↓
Context Capsule Builder
  ↓
Run Orchestrator
  ↓
Evidence Verifier
  ↓
State Delta Proposal
  ↓
Apply / Rollback
  ↓
Updated Project State
```

## 6. Adapter Layer

第一版不强制直接调用 AI。

支持模式：

| 模式 | 说明 |
|---|---|
| prompt-only | 生成 Context Capsule，用户复制到 AI 工具 |
| manual-run | 用户人工执行，然后录入 Evidence |
| shell-adapter | 调用本地命令或外部 CLI |
| api-adapter | 后续直接调用模型 API |
| verify-only | 只验证已有结果 |

## 7. 架构边界

ProgressEngine 不直接等于：

- IDE 插件。
- AI 编程模型。
- 项目管理 SaaS。
- 任务看板。

它是：

```text
项目状态推进层
```

它可以在未来嵌入 IDE、调用模型或连接 GitHub，但第一性职责是维护项目状态的证据化推进。
