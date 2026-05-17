# v0.1 MVP 范围与路线图

本文是 `IV-0002: Freeze v0.1 MVP boundary` 的产品边界产物。它的目的不是拆实现任务，也不是选择技术栈，而是把 ProgressEngine v0.1 从“已有策划书定义”推进到“实现前可审查、可确认、可作为技术栈选择和实现计划依据”的产品状态。

## 1. v0.1 目标状态

v0.1 的目标状态是：

```text
一个 repo-native、prompt-only / manual-run 优先的 ProgressEngine 状态推进闭环可以在本地项目中被完整演示：

Project State
  → State Gap
  → Target State
  → Intervention
  → Fresh Context Capsule
  → Evidence
  → Verification
  → State Delta Proposal
  → Human Gate
```

v0.1 不以“自动完成项目”为目标，也不以“生成更多任务”为目标。v0.1 只证明一件事：项目状态可以被结构化记录、被目标状态驱动推进，并通过证据和 State Delta Proposal 防止假完成。

## 2. v0.1 目标用户

v0.1 面向单人或小团队中的项目推进负责人，尤其是：

- 独立开发者，正在用 AI 工具推进一个从 0 到可用的项目。
- 小团队技术负责人，需要把产品、架构、质量和实现推进状态保持在同一个 repo 中。
- 使用 Codex、ChatGPT、Claude Code 或类似 AI 编码工具的人，需要避免长上下文漂移和“写了就算完成”。
- 想把项目推进经验变成可复用状态账本和验证协议的人。

v0.1 不面向企业级多用户协作、跨项目组合管理或生产 SaaS 运营团队。

## 3. v0.1 核心使用场景

### 3.1 从模糊意图启动项目状态

用户提供一个模糊项目意图后，ProgressEngine 帮助形成第一版可审查的 Project State，并识别当前最重要的 State Gap。

### 3.2 为下一步推进选择目标状态

用户或 AI 根据当前 Project State、State Gap 和成熟度矩阵选择一个 Target State，而不是从任务池中任意挑任务。

### 3.3 生成一个可执行的 Intervention

系统把 Target State 转成一个范围清楚、证据要求明确、带上下文预算的 Intervention。

### 3.4 隔离上下文执行

执行者只读取 Fresh Context Capsule 中列出的必要材料，避免继承长期会话噪声。

### 3.5 收集证据并生成 State Delta Proposal

执行完成后，ProgressEngine 记录 Evidence、执行非代码或代码验证，并只生成 State Delta Proposal。Project State 是否更新由 Human Gate 或明确策略决定。

## 4. v0.1 Must Have

v0.1 必须具备以下产品能力，才算形成最小状态推进闭环。

### 4.1 Repo-native 项目状态账本

- 在项目仓库内使用 `.progress/` 保存状态材料。
- 至少支持 `state/`、`gaps/`、`targets/`、`interventions/`、`runs/`、`evidence/`、`deltas/`、`events/`。
- 项目状态以文件系统中的 YAML / Markdown 为主要事实来源。

### 4.2 最小对象模型

v0.1 必须定义并使用以下最小对象：

- Project State：当前项目在 intent、product、architecture、implementation、quality、delivery、knowledge 等维度上的成熟度和证据。
- State Gap：当前状态与可推进目标状态之间的缺口。
- Target State：下一步希望达到的状态，而不是任务标题。
- Intervention：为了推进 Target State 而执行的一次有限动作。
- Fresh Context Capsule：执行 Intervention 所需的最小上下文包。
- Evidence：证明产物发生变化、验收标准被检查的证据。
- State Delta Proposal：建议如何更新 Project State 的提案。
- Change Event：记录影响状态声明、产物有效性或后续推进计划的变化。

### 4.3 手动或半自动状态推进流程

v0.1 可以是 manual-run 或 prompt-only 模式，但必须跑通：

```text
assess current state
identify state gap
select target state
plan intervention
prepare fresh context
execute outside or inside AI session
collect evidence
verify evidence
propose state delta
wait for human gate
```

该流程可以由文档、模板和人工命令共同完成，不要求完整 CLI 自动化。

### 4.4 Fresh Context Capsule 协议

- 每个 Intervention 必须有可生成或可手工整理的 Fresh Context Capsule。
- Capsule 必须声明目标、输入文件、输出文件、验收标准、范围外事项和上下文预算。
- Capsule 不得要求执行者读取完整历史对话。

### 4.5 Evidence Verifier 最小规则

v0.1 的 Evidence Verifier 至少检查：

- Evidence 是否映射到 Target State 的 acceptance criteria。
- 是否存在“文档已更新所以完成”的自证循环。
- 是否出现 silent deferral。
- 是否越过 out_of_scope。
- 是否修改 Project State 却没有 State Delta Proposal。

### 4.6 State Delta Proposal 优先

- v0.1 只能在验证后生成 State Delta Proposal。
- 默认不能由 Executor 直接修改 Project State 成熟度。
- 只有 Human Gate 或明确自动化策略允许时，才能 apply State Delta。

### 4.7 最小质量门禁

v0.1 必须至少具备：

- 核心文件存在检查。
- YAML 可解析检查。
- Markdown 本地链接检查。
- 文档产物 checklist。
- Evidence 与 acceptance criteria 映射检查。

### 4.8 Prompt-only / manual-run 优先

v0.1 的第一版可运行形态可以通过提示词、模板、文档和手动命令完成，不要求完整模型 API 接入或自动 agent 编排。

## 5. v0.1 Should Have

以下能力对 v0.1 有价值，但不能扩大 Must Have 边界：

- 面向 CLI 的命令草案和输入输出示例。
- Mermaid 生命周期图和状态维度图。
- Git diff 或文件变更摘要作为 Evidence 辅助材料。
- 基础 Markdown / HTML 报告。
- 对 stale target / stale intervention 的简单人工标记。
- 一到两个示例项目状态材料，用于验证 `.progress/` 结构是否可读。

## 6. v0.1 Won't Have

v0.1 明确不包含：

- Web UI。
- SaaS。
- 多用户协作。
- 完整模型 API 接入。
- 自动调用外部 AI agent。
- 自动发布生产环境。
- 完整 CLI 全功能。
- 复杂调度器。
- 支付、权限、多租户。
- 跨项目 workspace 管理。
- 实时 agent 编排。
- 全自动高风险产品或架构决策。
- 生产级插件市场或外部 adapter 生态。

## 7. v0.1 明确非目标

v0.1 不承诺：

- 自动把任意项目意图变成完整产品。
- 自动替代产品负责人、技术负责人或 QA 负责人。
- 证明所有状态判断都是客观正确的。
- 让任务数量、任务完成率或任务图规模成为成功指标。
- 为未来所有版本提前定死架构。
- 支持团队权限、审计合规、计费和生产部署。

## 8. v0.1 成功标准

v0.1 成功必须同时满足：

1. 能在一个 repo 中初始化或维护 `.progress/` 状态账本。
2. 能记录第一版 Project State，并为每个状态维度附上证据引用。
3. 能识别至少一个 State Gap，并说明为什么它是当前优先级。
4. 能生成或维护一个 Target State，且 Target State 有 acceptance criteria。
5. 能生成或维护一个 Intervention，且包含 in_scope、out_of_scope、evidence_required 和 human gate 策略。
6. 能生成或整理 Fresh Context Capsule，限制执行上下文。
7. 能记录 Evidence，并将 Evidence 映射到验收项。
8. 能执行非代码产物或代码产物的最小验证。
9. 能生成 State Delta Proposal，而不是直接污染 Project State。
10. 能明确列出 remaining gaps，并将它们转为后续 State Gap、Target State 或 Intervention。
11. 能通过最小仓库检查：核心文件存在、YAML 可解析、Markdown 本地链接有效。

## 9. v0.1 不成功的判定标准

出现以下任一情况，v0.1 不应被判定为成功：

- 只能生成任务列表，不能说明项目状态如何变化。
- Project State 被直接修改为完成态，但没有 Evidence 和 State Delta Proposal。
- MVP 范围依赖完整 Web UI、SaaS、外部 agent 或模型 API 才能成立。
- Fresh Context Capsule 只是复制完整历史对话，没有最小上下文边界。
- Evidence 只写“文档已更新”或“功能已完成”，没有验收映射。
- Won't Have 和非目标不清，导致技术栈选择被过早扩大。
- remaining gaps 只用自然语言说“后续优化”，没有进入结构化状态材料。
- 最小仓库检查无法通过，且失败原因没有进入 Change Event 或 remaining gap。

## 10. v0.1 第一批可实现能力

v0.1 的第一批实现能力应按状态闭环排序，而不是按任务数量排序：

1. 读取和显示 Project State。
2. 记录和列出 State Gap。
3. 维护 Target State。
4. 从 Target State 形成 Intervention 草案。
5. 生成或校验 Fresh Context Capsule。
6. 记录 Evidence。
7. 基于 checklist 验证 Evidence。
8. 生成 State Delta Proposal。
9. 在 Human Gate 后应用或拒绝 State Delta。
10. 运行最小 docs / YAML / Markdown link 检查。

这些能力可以先通过 prompt-only、manual-run 和轻量脚本组合实现；是否做成正式 CLI 子命令，留给 `IV-0003` 和后续技术栈决策。

## 11. v0.1 后续实现前置条件

进入 v0.1 实现前，至少需要：

- `TS-0002` 被人工确认或接受。
- `SDP-0002` 被人工审查，并决定是否 apply 到 Project State。
- `IV-0003` 明确技术栈、目录结构、schema 处理方式和最小 CLI 边界。
- `IV-0004` 强化 docs / YAML / Markdown link 检查，避免状态材料格式漂移。
- 确认哪些 `.progress/` 对象只需要模板，哪些需要可执行 schema。

## 12. v0.1 与后续版本的边界

### v0.1: State Loop MVP

目标是跑通 repo-native 状态推进闭环。它可以是手动或半自动，不要求完整自动化。

### v0.2: Bootstrap Role Pipeline

强化从 0 启动，包括 Product Lead、Product Critic、Tech Lead、QA Lead 和 State Synthesizer 等角色流水线。

### v0.3: Change Event + Reassessment

强化变更事件、影响分析、stale / reopened 标记和 intervention invalidation。

### v0.4: Guarded Spiral

支持多轮受控推进，但每轮仍坚持 One Intervention, One Fresh Context, Evidence, State Delta。

### v1.0: Adapter Integration

连接外部 AI 执行工具、模型 API 或 shell adapter，但不能改变 v0.1 中确立的状态门禁原则。

## 13. 本次仍未解决的产品问题

以下问题不阻断 v0.1 边界冻结，但必须作为后续状态材料处理：

| Gap | 状态缺口 | 影响 | 结构化去向 |
|---|---|---|---|
| `SG-0002` | v0.1 的真实试点项目尚未选定。 | v0.1 可以 accepted，但不能 validated。 | 进入后续 product / validation target。 |
| `SG-0003` | `.progress` 对象 schema 与仓库检查仍偏弱。 | 可能导致 Evidence、Target State 和 State Delta 格式漂移。 | 由 `IV-0004` 推进 quality state。 |
| `EVT-0002` | 现有 target 文件命名和索引材料存在不一致。 | 可能影响后续自动发现和人工审查。 | 作为 Change Event 记录，后续由 docs / YAML check 收敛。 |

## 14. 未解决问题如何进入后续状态推进

- `SG-0002` 应生成后续 Target State：`v0.1 pilot validation scenario selected`，并由新的 product clarification / validation intervention 推进。
- `SG-0003` 应由 `IV-0004: Strengthen docs and YAML check` 推进，不应并入 IV-0002。
- `EVT-0002` 应在下一轮质量或治理推进中复核，决定是否统一 target 文件命名、补充 INDEX 和强化检查脚本。
- 如果人工审查认为本文仍不足以冻结 MVP 边界，应拒绝 `SDP-0002`，并生成新的 product clarification intervention，而不是直接进入 `IV-0003`。

## 15. 下一步推荐状态推进

如果 `TS-0002` 和 `SDP-0002` 经人工确认，下一步优先推进：

- `IV-0003: Select v0.1 technical stack`，把已冻结的产品边界转化为技术栈、模块边界和实现计划依据。
- `IV-0004: Strengthen docs and YAML check`，强化最小仓库检查，降低状态材料漂移风险。
