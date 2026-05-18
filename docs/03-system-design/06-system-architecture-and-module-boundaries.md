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

## 8. v0.1 技术栈选择

`IV-0003` 将 v0.1 技术栈冻结为：

| 层面 | v0.1 选择 | 理由 |
|---|---|---|
| Runtime | Python 3.11+ | 本仓库已有 Python 自检脚本和 `src/progress_engine/` 预留目录；适合本地 CLI、文件系统操作和低依赖分发。 |
| CLI | Python stdlib `argparse` 起步，保留后续迁移到 Typer / Click 的空间 | v0.1 先证明状态闭环，不把 CLI 框架作为核心风险。 |
| 状态文件 | YAML + Markdown + JSONL | YAML 适合可审查对象，Markdown 适合人类协议和报告，JSONL 适合 append-only history / events。 |
| YAML 处理 | PyYAML 作为最小依赖；无 PyYAML 时检查脚本可降级跳过解析 | 与现有 `scripts/check_repo.py` 一致，降低引入复杂 schema runtime 的风险。 |
| 数据模型 | Python dataclass / typed dict 起步，schema 文件作为后续质量门禁 | v0.1 优先保持对象清晰和 repo-native 可读性，避免过早 ORM 或数据库抽象。 |
| 测试 | `pytest` 用于 CLI / state transition / verifier 测试 | Python CLI 生态成熟，适合 fixture-based 验证 YAML 和文件变更。 |
| 包管理 | `pyproject.toml` 已作为 Python package 配置引入 | 保持本地 CLI 和测试入口可运行。 |
| 模型 API | 不接入 | v0.1 采用 prompt-only / manual-run，避免把模型调用变成 MVP 前置条件。 |
| Web / SaaS | 不接入 | 已由 v0.1 产品边界排除。 |

该选择的正式决策记录见 `decisions/ADR-0001-v0.1-tech-stack.md`。

## 9. v0.1 模块边界

v0.1 实现应优先覆盖最小状态闭环，而不是一次性实现顶层模块的完整形态。

| v0.1 模块 | 最小职责 | 暂不承担 |
|---|---|---|
| State Store | 读取 / 写入 `.progress/state/project_state.yaml`、`state_history.jsonl`。 | 数据库、远程同步、多项目 workspace。 |
| Object Loader | 读取 Target State、Intervention、Evidence、State Delta Proposal、Change Event。 | 完整 schema migration、跨版本兼容层。 |
| State Reconciler | 基于显式 evidence refs 和 gap refs 输出当前状态摘要。 | 自动理解任意代码库或聊天历史。 |
| Intervention Planner | 从 Target State 和模板生成 Intervention 草案。 | 自动拆完整任务图。 |
| Capsule Builder | 生成 Fresh Context Capsule 的 Markdown 文件。 | 自动调用外部 AI agent。 |
| Evidence Recorder | 记录 artifact review、command output、test result 等 Evidence。 | 自动判断真实业务价值。 |
| Verifier | 检查 acceptance mapping、scope、silent deferral 和 State Delta claim。 | 替代人工产品 / 架构判断。 |
| Delta Manager | 生成、review、apply、reject State Delta Proposal。 | 绕过 human gate 自动改状态。 |
| Repo Check | 检查 required paths、YAML parse、Markdown links。 | 完整语义 schema 校验。 |

## 10. v0.1 目录边界

v0.1 实现阶段可使用以下目录边界：

```text
src/progress_engine/
  cli/              # argparse command handlers
  state/            # project state load/save/history
  objects/          # target/intervention/evidence/delta/event loaders
  planning/         # target to intervention helpers
  capsule/          # Fresh Context Capsule builder
  verification/     # artifact/evidence/scope checks
  delta/            # proposal/apply/reject/rollback helpers
  repo_check/       # docs/YAML/Markdown local checks

tests/
  fixtures/         # sample .progress objects
  test_state.py
  test_verification.py
  test_delta.py
  test_repo_check.py

schemas/
  target_state.schema.yaml
  intervention.schema.yaml
  evidence.schema.yaml
  state_delta.schema.yaml
```

这些目录是实现边界，不要求一次性创建所有模块；实际实现应继续按 Intervention 小切片逐步落地。

## 11. 备选方案与拒绝理由

| 方案 | 结论 | 理由 |
|---|---|---|
| Node.js / TypeScript CLI | 暂不采用为 v0.1 主路径 | 类型系统和 CLI 生态强，但当前仓库已有 Python 自检脚本；v0.1 的核心风险在状态协议，不在前端或 JS 生态。 |
| Rust CLI | 暂不采用 | 分发和性能优秀，但实现成本高于 v0.1 需要。 |
| Go CLI | 暂不采用 | 单文件分发好，但 YAML / Markdown / repo-native artifact 工作流不比 Python 更低摩擦。 |
| SQLite / embedded DB | 暂不采用 | 会削弱 repo-native 可审查性；v0.1 状态事实源应保持文件化。 |
| Full model API integration | 明确排除 | v0.1 产品边界是 prompt-only / manual-run 优先。 |

## 12. 已关闭前置条件与后续约束

以下前置条件已经关闭：

- `SDP-0003` 已被人工确认，architecture maturity 已推进到 accepted。
- `IV-0004` 已明确并实现最小 docs / YAML / Markdown / `.progress` 对象检查边界。
- `pyproject.toml`、测试 fixture 和 CLI 入口已在后续 implementation interventions 中按小切片创建。

后续约束：

- 如果人工重新否决 Python 主路径，应重新打开 `TS-0003`，并创建新的 architecture clarification intervention。
- 新 CLI 能力仍必须通过 Target State、Intervention、Evidence、Verification 和 State Delta Proposal 推进。
