# ProgressEngine 完整项目策划书 v3

> 核心口径：持续推进项目状态，而不是持续完成任务。

## 目录

- [ProgressEngine 项目策划书 v3](#ProgressEngine-项目策划书-v3)
- [执行摘要](#执行摘要)
- [愿景定位与问题定义](#愿景定位与问题定义)
- [核心方法论：持续推进项目状态](#核心方法论：持续推进项目状态)
- [项目状态模型与成熟度矩阵](#项目状态模型与成熟度矩阵)
- [目标状态选择策略](#目标状态选择策略)
- [从 0 启动角色流水线](#从-0-启动角色流水线)
- [系统架构与模块边界](#系统架构与模块边界)
- [核心对象与数据模型](#核心对象与数据模型)
- [Intervention 推进动作与执行协议](#Intervention-推进动作与执行协议)
- [Fresh Context 上下文隔离协议](#Fresh-Context-上下文隔离协议)
- [Evidence Verifier 证据验证协议](#Evidence-Verifier-证据验证协议)
- [非代码产物验证协议](#非代码产物验证协议)
- [Change Event 影响分析与失效传播](#Change-Event-影响分析与失效传播)
- [State Delta 提案、应用与回滚协议](#State-Delta-提案、应用与回滚协议)
- [CLI 与交互设计](#CLI-与交互设计)
- [工作流与典型场景](#工作流与典型场景)
- [MVP 范围与路线图](#MVP-范围与路线图)
- [质量体系与风险管理](#质量体系与风险管理)
- [Guarded Spiral 自动化边界](#Guarded-Spiral-自动化边界)
- [实施计划与推进动作清单](#实施计划与推进动作清单)
- [运营方式、商业化与后续演进](#运营方式、商业化与后续演进)
- [术语表](#术语表)
- [自检协议与开放缺口](#自检协议与开放缺口)
- [v3 版本修正清单](#v3-版本修正清单)
- [v3 自检与修正报告](#v3-自检与修正报告)

---

## README

本包是 ProgressEngine 的第三版完整项目策划书。相较 v2，本版做了更严格的一致性、自检和闭环补强：

1. **把核心目标从“生成任务池 / 编译任务图”改为“持续推进项目状态”。**
2. **把任务降级为推进动作的一种执行形态。**任务不是目标，项目状态变化才是目标。
3. **补齐关键闭环协议。**包括项目状态成熟度矩阵、目标状态选择策略、从 0 启动角色流水线、非代码产物验证协议、Change Event 影响分析、Fresh Context 执行协议、State Delta 提案/应用/回滚协议、Guarded Spiral 自动化边界。
4. **明确 MVP 第一阶段以 prompt-only / repo-native / CLI-first 为主。** 不把模型调用和复杂自动化作为第一阶段核心风险。

建议阅读顺序：

```text
dist/ProgressEngine_Project_Plan_full.md
  ↓
docs/00-overview/02-core-methodology-state-driven-progress.md
  ↓
docs/01-state-engine/03-project-state-model-and-maturity-matrix.md
  ↓
docs/02-bootstrap-workflows/05-zero-to-project-role-pipeline.md
  ↓
docs/03-system-design/14-cli-and-interaction-design.md
  ↓
docs/05-delivery/16-mvp-scope-and-roadmap.md
```

本版核心定义：

> ProgressEngine 是一个状态驱动的 AI 软件工程系统，目标不是生成任务池，而是持续推进项目状态。它通过状态建模、目标状态规划、推进动作拆解、上下文隔离执行和证据验证，把模糊项目意图逐步推进为可用产品、工程资产和决策结果。


## v3 自检修正重点

v3 在 v2 基础上额外修正：

1. 明确 `progress update` 的冗余问题，统一为 `delta apply` 后自动写入状态，并通过 `progress state refresh` 做重新评估。
2. 补齐成熟度矩阵中的 `seed` 及异常状态说明，避免枚举和矩阵不一致。
3. 强化 `StateDelta` 的 proposal / approval / apply / rollback 元数据。
4. 强化 `ChangeEvent` 的影响分析字段，包括 artifact effect、invalidated claims、generated gaps / targets / interventions。
5. 明确 `verify` 只生成 State Delta Proposal，不直接更新 Project State。
6. 明确 `delta apply` 才能修改状态账本，且必须可回滚或显式声明不可回滚。
7. 增加自检协议，说明哪些内容可以机器检查、哪些必须人工审查。

---

## 执行摘要

## 1. 项目名称

**ProgressEngine**

## 2. 一句话定义

ProgressEngine 是一个**持续推进项目状态**的 AI 软件工程系统。它不是任务管理器，也不是 AI 编程器，而是通过状态建模、目标状态规划、推进动作拆解、隔离执行和证据验证，把模糊项目意图逐步推进为可用产品、工程资产和决策结果。

## 3. 项目背景

单人或小团队用 AI 做软件项目时，常见问题不是“AI 不能写代码”，而是：

- 项目初期没有方向，只能靠逐渐摸索。
- 产品、项目、技术、质量职责都压在一个人身上。
- AI 会话很快上下文膨胀，注意力漂移。
- AI 容易“假完成”：自称完成，但没有证据，没有验收映射，没有后续计划。
- 项目推进过程中的产品变化、架构发现、质量缺口、任务拆分没有被系统性记录。
- 项目状态散落在聊天、代码、文档、记忆和临时 TODO 中，难以复盘和持续推进。

ProgressEngine 的目标是建立一个 repo-native、状态驱动、AI-native 的项目推进系统，让一个人也能像一个小型软件组织一样，从 0 开始持续推进项目。

## 4. 核心转变

本项目的关键认知修正是：

```text
任务不是目标。
任务池不是目标。
任务图不是目标。
真正目标是持续推进项目状态。
```

因此系统主循环不是：

```text
生成任务 → 执行任务 → 完成任务
```

而是：

```text
评估当前项目状态
  ↓
识别状态缺口
  ↓
选择下一步目标状态
  ↓
规划最小有效推进动作
  ↓
隔离上下文执行
  ↓
证据验证
  ↓
应用状态变化
  ↓
重新评估项目状态
```

## 5. 核心产物

ProgressEngine 第一阶段应产出：

- `.progress/` 项目运行目录协议。
- 项目状态模型与成熟度矩阵。
- 从 0 启动角色流水线。
- 目标状态选择策略。
- 推进动作 Intervention 协议。
- Fresh Context 上下文隔离协议。
- Evidence Verifier 证据验证协议。
- Change Event 影响分析与失效传播协议。
- State Delta 提案、应用、回滚协议。
- CLI-first 的本地工具。
- Prompt-only 的 AI 执行入口。

## 6. MVP 成功标准

第一版 MVP 不追求全自动编码，不追求 Web 平台，不追求复杂 agent 编排。它的成功标准是：

```text
输入一个模糊项目意图
  ↓
生成第一版可审查 Project State
  ↓
识别当前最重要的 State Gap
  ↓
推荐一个 Target State
  ↓
生成一个可执行 Intervention
  ↓
生成 Fresh Context Capsule
  ↓
用户或外部 AI 执行
  ↓
收集 Evidence
  ↓
独立 Verify
  ↓
生成 State Delta Proposal
  ↓
应用到项目状态账本
```

只要这条闭环成立，ProgressEngine 就能开始服务真实项目推进。

---

## 愿景定位与问题定义

## 1. 愿景

ProgressEngine 的愿景是：

> 让一个人能够在 AI 协助下，以产品经理、项目经理、技术负责人、质量负责人和开发者的复合视角，从模糊意图开始，持续推进一个软件项目走向可用、可验证、可交付的状态。

它面向的不是“更快写代码”，而是“更可靠地推进项目”。

## 2. 用户画像

### 2.1 主要用户

- 独立开发者。
- 小团队技术负责人。
- 使用 AI 编码工具推进多个项目的人。
- 想把隐性项目推进经验体系化的人。
- 既关心工程质量，也关心产品验证的人。

### 2.2 用户当前行为

当前用户通常会这样推进项目：

```text
有一个想法
  ↓
开一个 AI 对话
  ↓
让 AI 生成一些代码或文档
  ↓
逐渐搭建项目
  ↓
发现问题后修修补补
  ↓
手写台账
  ↓
手动阅读台账挑任务
  ↓
继续执行
```

这条路径的问题是：前半段非常混乱，后半段才逐渐形成秩序。

ProgressEngine 要做的是让项目从第一天就拥有可推进的状态结构，而不是混乱若干轮之后才开始台账化。

## 3. 核心问题

### 3.1 项目初期无方向

用户有意图，但不知道如何系统地把意图变成项目状态、产品范围、设计、架构、质量计划和推进动作。

### 3.2 AI 缺少项目治理边界

AI 可以写代码，但缺少项目级上下文治理。它容易忽略非目标、跳过验收、扩大范围或自作主张改变架构。

### 3.3 上下文膨胀导致注意力漂移

长会话会积累过多上下文，导致模型对当前任务的关注度下降，质量不可控。

### 3.4 假完成

AI 常见输出：

```text
功能已完成。
后续可以继续优化。
这个可以放到下一阶段。
```

但没有证据，没有状态变化记录，没有新任务，没有验证结果。

### 3.5 非代码工作缺少验证

PRD、架构设计、UX 流程、质量计划等非代码产物容易“写了就算完成”，但实际上可能缺少关键字段、反方审查和可执行性。

### 3.6 项目是螺旋式推进，不是瀑布式推进

项目会不断出现：

- 产品澄清。
- 架构修正。
- 任务重拆。
- 质量查漏。
- 用户反馈。
- 实现中发现设计缺陷。

系统必须支持前进、后退、修正、重规划，而不是一次性生成计划后机械执行。

## 4. 解决方案概述

ProgressEngine 用以下机制解决问题：

| 问题 | 机制 |
|---|---|
| 项目初期无方向 | 从 0 启动角色流水线 |
| AI 注意力漂移 | One Intervention, One Fresh Context |
| 假完成 | Evidence Verifier + State Delta |
| 任务制造机倾向 | State-first 调度 |
| 非代码产物自证循环 | Artifact Review Checklist |
| 螺旋式变化 | Change Event + Impact Analysis + Invalidation |
| 状态账本污染 | Proposal / Apply / Rollback |
| 自动化风险 | Guarded Spiral Automation Policy |

## 5. 非目标

第一阶段不做：

- 不做大而全 SaaS。
- 不做多用户协作系统。
- 不做复杂 Web Dashboard。
- 不直接替代 ChatGPT、Codex、Claude Code 等 AI 工具。
- 不承诺完全自动完成高风险产品和架构决策。
- 不把任务数量、任务池规模作为成功指标。

## 6. 成功判断

ProgressEngine 成功不是因为它生成了很多任务，而是因为用户能清楚回答：

```text
当前项目真实状态是什么？
当前最大状态缺口是什么？
下一步目标状态是什么？
为什么优先推进这个状态？
用什么动作推进？
完成后有什么证据？
状态是否真的改变？
如果失败，回流到哪个环节？
```

---

## 核心方法论：持续推进项目状态

## 1. 总纲

ProgressEngine 的总纲是：

> 持续推进项目状态，而不是持续完成任务。

项目推进的本质是：

```text
在不确定性中，持续把意图转化为可验证的产品能力、工程资产和决策证据。
```

## 2. 核心公式

```text
Project State
  → State Gap
  → Target State
  → Intervention
  → Fresh Run
  → Evidence
  → State Delta
  → Updated Project State
```

解释：

| 概念 | 含义 |
|---|---|
| Project State | 当前项目真实状态 |
| State Gap | 当前状态与期望状态之间的缺口 |
| Target State | 下一步希望项目达到的状态 |
| Intervention | 推动状态变化的动作 |
| Fresh Run | 一次隔离上下文执行 |
| Evidence | 证明状态变化的证据 |
| State Delta | 本轮执行导致的状态变化声明 |
| Updated Project State | 被证据更新后的项目状态 |

## 3. 核心原则

### 3.1 State First

系统每轮首先判断项目状态，而不是挑任务。

```text
先问：项目下一步应该变成什么状态？
再问：需要采取什么动作？
最后才问：这个动作是否需要变成任务或 Run？
```

### 3.2 Task Second

任务是推进动作的可执行形态，不是系统核心。

```text
Task = Executable Intervention
```

如果一个任务不能说明它推动哪个项目状态维度，就不应该执行。

### 3.3 Evidence Required

任何状态变化必须有证据。

```text
没有证据，状态不变。
```

### 3.4 Fresh Context

每个推进动作必须使用新的上下文空间。

```text
One Intervention, One Fresh Context.
```

上一轮完整对话不能进入下一轮。下一轮只能读取已落账的项目事实源。

### 3.5 Executor Cannot Self-Close

执行者不能关闭自己的任务或状态变化。Verifier 必须独立验证。

### 3.6 No Silent Deferral

任何“后续再做”都必须变成结构化状态缺口、Change Event 或新的 Intervention。

### 3.7 Spiral, Not Waterfall

项目不是线性推进，而是：

```text
前进 → 发现问题 → 回退修正 → 重规划 → 再前进
```

系统必须显式支持 reopened、stale、superseded、rollback 等状态。

## 4. 主循环

```text
Assess Project State
  ↓
Score State Gaps
  ↓
Select Target State
  ↓
Generate Intervention Proposal
  ↓
Gate / Approve
  ↓
Build Fresh Context Capsule
  ↓
Execute Run
  ↓
Collect Evidence
  ↓
Verify in Fresh Context
  ↓
Propose State Delta
  ↓
Apply / Reject / Rollback
  ↓
Emit Change Events
  ↓
Reassess Project State
```

## 5. 和普通项目管理的区别

| 普通项目管理 | ProgressEngine |
|---|---|
| 以任务列表为中心 | 以项目状态为中心 |
| 完成任务即进展 | 证据化状态变化才算进展 |
| 阶段计划相对静态 | 持续根据事件重规划 |
| 上下文依赖人脑记忆 | 上下文来自事实源和 Capsule |
| AI 执行后自称完成 | Verifier 独立验证 |
| 变更可能散落在聊天 | Change Event 统一捕获 |

## 6. 和 AI 编程工具的区别

AI 编程工具解决的是：

```text
如何完成一个局部代码任务？
```

ProgressEngine 解决的是：

```text
当前项目最需要推进什么状态？
如何把这个状态变化转化为可执行动作？
如何证明状态真的改变？
如何把结果沉淀到下一轮？
```

ProgressEngine 可以调用 AI 编程工具，但它不等同于 AI 编程工具。

---

## 项目状态模型与成熟度矩阵

## 1. Project State 结构

ProgressEngine 使用 `Project State` 表示项目当前真实状态。项目状态不是单一状态，而是由多个维度组成。

```text
Project State
  ├── Intent State
  ├── Product State
  ├── UX / Design State
  ├── System Design State
  ├── Architecture State
  ├── Implementation State
  ├── Quality State
  ├── Delivery State
  └── Knowledge / Governance State
```

## 2. 状态维度定义

| 维度 | 说明 |
|---|---|
| Intent | 项目意图、目标、约束是否清楚 |
| Product | 用户、场景、范围、价值是否清楚 |
| UX / Design | 用户流程、交互、信息结构、界面体验是否清楚 |
| System Design | 系统边界、数据流、模块关系是否清楚 |
| Architecture | 技术栈、架构决策、关键风险是否清楚 |
| Implementation | 已实现能力、运行状态、代码结构 |
| Quality | 测试、验收、风险覆盖、质量门禁 |
| Delivery | 部署、回滚、监控、发布准备 |
| Knowledge / Governance | 决策、假设、风险、反馈、变更是否沉淀 |

## 3. 成熟度枚举

为了避免状态评估完全主观，使用统一成熟度枚举：

```text
unknown      未知或未评估
weak         有模糊信息，但不足以指导下一步
seed         有初始结构或草案起点
drafted      有完整初稿，但未审查
reviewed     已经过角色审查或 checklist 审查
accepted     已被人工或策略门禁接受，可指导下游工作
validated    已被实现、测试、用户反馈或实验验证
stale        因新变化失效，需要复核
reopened     之前接受过，但因事件重新打开
superseded   已被新版本替代
blocked      因依赖、缺口或风险无法继续推进
```

## 4. 成熟度矩阵

成熟度矩阵用于判断每个状态维度是否已经足以指导下游推进。`seed` 表示已有起点但还不足以称为完整初稿；`stale / reopened / superseded / blocked` 是异常或治理状态，不是线性成熟度阶段。

| 维度 | unknown / weak | seed | drafted | reviewed | accepted | validated |
|---|---|---|---|---|---|---|
| Intent | 只有想法或口头描述 | 有一段原始意图记录 | 有 intent.yaml，包含目标和约束 | 经过意图澄清问题审查 | 人工确认项目方向 | 经过真实推进仍然成立 |
| Product | 用户和场景不清 | 有候选用户或问题假设 | 有 PRD / Product Brief 初稿 | 经过 Product Critic 审查 | MVP 范围、非目标、成功标准确认 | 用户反馈或实验支持价值假设 |
| UX / Design | 无流程或界面想法 | 有粗略流程或界面草图 | 有用户流程/命令交互/页面草图 | 经过 UX checklist 审查 | 可指导实现 | 被可用性测试或真实使用验证 |
| System Design | 系统边界模糊 | 有候选模块或边界线索 | 有模块、数据流、接口草案 | 经过系统设计审查 | 模块边界可指导拆解 | 实现证明边界可用 |
| Architecture | 技术路线不清 | 有候选技术栈 | 有技术方案和备选方案 | 经过 Tech Critic 审查 | ADR 接受，关键风险有处理计划 | Spike 或实现证明方案可行 |
| Implementation | 无可运行能力 | 有仓库或脚手架起点 | 有脚手架或局部实现 | 经过代码 review 或运行检查 | 核心能力可运行 | 自动化测试/演示/用户使用证明可用 |
| Quality | 没有测试策略 | 有质量关注点列表 | 有质量计划和测试矩阵 | 经过 QA review | 核心门禁确认 | 测试、回归、缺陷数据支持质量信心 |
| Delivery | 不可部署 | 有部署目标或候选环境 | 有部署方案草案 | 经过 release checklist 审查 | 可部署、可回滚、可观察 | 真实发布或内测运行成功 |
| Knowledge | 决策散落 | 有零散记录 | 有假设、风险、决策记录 | 经过 reconcile 审查 | 账本与项目现实一致 | 经过多轮迭代仍可追溯 |

### 4.1 异常与治理状态

这些状态不代表成熟度上升，而代表项目需要治理动作：

| 状态 | 含义 | 必须动作 |
|---|---|---|
| stale | 由于新事件或新版本，原状态声明可能失效 | 运行 reassess，生成 Gap 或 Reopen 事件 |
| reopened | 曾经 accepted / reviewed 的 artifact 被重新打开 | 重新 review，可能生成新的 Target State |
| superseded | 被新版本完全替代 | 更新引用，标记依赖项 stale |
| blocked | 因依赖、风险或信息缺失无法推进 | 生成解除阻塞的 Intervention |

## 5. Progress Status 与 Maturity 分离

成熟度表示“可信程度”，进展状态表示“当前操作状态”。两者不应混用。

```yaml
state_dimension:
  maturity: drafted
  progress: in_progress
```

`progress` 枚举：

```text
not_started
in_progress
partial
complete
blocked
waiting_for_review
```

示例：

```yaml
product:
  maturity: reviewed
  progress: partial
  summary: "MVP scope reviewed, but success metrics still weak."
```

## 6. State Assessment 输出

每次 `progress assess` 应输出：

```yaml
assessment:
  project_id: progressengine
  assessed_at: 2026-05-16
  dimensions:
    product:
      maturity: reviewed
      progress: partial
      evidence:
        - artifacts/prd.md
        - reviews/product_critic_001.md
      gaps:
        - G-004
    quality:
      maturity: weak
      progress: not_started
      evidence: []
      gaps:
        - G-008
```

## 7. 判定规则

状态不能因为“存在文档”就自动升级。升级必须同时满足：

```text
artifact exists
+ required fields present
+ review checklist passed
+ evidence recorded
+ no blocking gap
```

对于 validated 状态，还需要：

```text
implementation evidence / test evidence / user feedback / experiment result
```

---

## 目标状态选择策略

## 1. 为什么需要目标状态选择策略

如果系统只根据已有任务池选择任务，就会退化成任务工具。ProgressEngine 每轮必须先判断：

```text
当前最有价值的项目状态变化是什么？
```

这需要一个可解释的目标状态选择策略。

## 2. 从 State Gap 到 Target State

流程：

```text
Project State Assessment
  ↓
State Gaps
  ↓
Gap Scoring
  ↓
Target State Candidate
  ↓
Target State Selection
  ↓
Intervention Planning
```

## 3. State Gap 数据结构

```yaml
gap:
  id: G-001
  dimension: product
  current_state: "Product scope is drafted but not reviewed."
  desired_state: "MVP scope accepted with explicit non-goals and success metrics."
  severity: high
  evidence:
    - artifacts/prd.md
  impact:
    - "Implementation tasks may encode wrong scope."
    - "Quality acceptance criteria cannot be finalized."
```

## 4. 评分模型

每个目标状态候选使用 0-5 分评分：

| 因子 | 说明 |
|---|---|
| risk_reduction | 是否降低关键风险 |
| downstream_unlock | 是否解锁后续工作 |
| user_value_proximity | 是否更接近用户价值 |
| quality_confidence_gain | 是否提升质量信心 |
| prevents_wrong_work | 是否避免在错误方向上继续实现 |
| implementation_capability_gain | 是否增加可运行能力 |
| knowledge_clarity_gain | 是否提升项目可追溯性 |
| effort | 预计成本，越高越扣分 |
| reversibility | 是否容易回退，越容易越加分 |
| automation_suitability | 是否适合自动或半自动执行 |

推荐公式：

```text
score =
  risk_reduction
+ downstream_unlock
+ user_value_proximity
+ quality_confidence_gain
+ prevents_wrong_work
+ implementation_capability_gain
+ knowledge_clarity_gain
+ reversibility
+ automation_suitability
- effort
```

## 5. 选择策略

### 5.1 Explore 模式

适合项目早期。

优先级：

```text
降低最大不确定性 > 增加代码量
```

常见目标状态：

- Intent accepted。
- Product scope reviewed。
- Architecture options reviewed。
- Quality plan drafted。

### 5.2 Converge 模式

适合从概念收敛到 MVP。

优先级：

```text
明确范围 > 明确架构 > 明确验收 > 再实现
```

### 5.3 Build 模式

适合主要方向已定后。

优先级：

```text
增加可运行能力 > 补文档
```

但如果实现中发现设计缺口，必须回退到对应状态维度。

### 5.4 Harden 模式

适合发布前。

优先级：

```text
质量证据 > 新功能
```

### 5.5 Release 模式

适合交付阶段。

优先级：

```text
部署、回滚、监控、已知问题、反馈入口
```

## 6. Target State 模板

```yaml
target_state:
  id: TS-001
  dimension: product
  from:
    maturity: drafted
    summary: "PRD exists but scope is not reviewed."
  to:
    maturity: accepted
    summary: "MVP scope accepted with explicit non-goals and success metrics."
  why_now:
    - "Implementation tasks depend on stable scope."
    - "Avoid building features outside MVP."
  score:
    risk_reduction: 4
    downstream_unlock: 5
    user_value_proximity: 4
    quality_confidence_gain: 3
    prevents_wrong_work: 5
    effort: 2
  required_interventions:
    - IV-001
  gate_required: true
```

## 7. 输出要求

`progress target` 不应只输出一个答案，而应输出：

```text
Top 3 Target State Candidates
  - 推荐目标状态
  - 为什么现在做
  - 不做的风险
  - 需要的人类确认
  - 对应推进动作建议
```

## 8. 禁止规则

- 不允许直接从状态缺口跳到代码实现。
- 不允许忽略高风险状态缺口继续刷实现任务。
- 不允许选择无法验证的目标状态。
- 不允许选择没有 State Delta 定义的目标状态。

---

## 从 0 启动角色流水线

## 1. 目的

用户最早的问题是：

```text
我有一个意图，如何在产品经理、项目经理、技术负责人、质量负责人等角色的帮助下，从 0 开始推进项目？
```

ProgressEngine 的启动流程必须解决这个问题。

## 2. 启动原则

从 0 启动不是瀑布式定稿，而是创建第一版可运行的项目认知结构。

```text
Initial Project State = seed version, not final truth.
```

后续每次执行都会根据新发现重评估和修正。

## 3. 启动流水线

```text
Intent Intake
  ↓
Product Lead Pass
  ↓
Product Critic Pass
  ↓
UX / Interaction Pass
  ↓
Project Manager Pass
  ↓
Tech Lead Pass
  ↓
Architecture Critic Pass
  ↓
QA Lead Pass
  ↓
State Synthesizer Pass
  ↓
Initial Target State Proposal
```

每个 pass 都是独立上下文，不继承完整聊天历史，只读取前一个 pass 产出的 artifact。

## 4. 各角色职责

| Pass | 输入 | 输出 | 推进的状态 |
|---|---|---|---|
| Intent Intake | 用户原始意图 | intent.yaml | Intent |
| Product Lead | intent.yaml | product_brief.md, prd.md | Product |
| Product Critic | product_brief, prd | product_review.md, gaps | Product / Knowledge |
| UX / Interaction | PRD | ux_design.md | UX / Design |
| Project Manager | PRD, gaps | roadmap.md, state_targets.yaml | Knowledge / Planning |
| Tech Lead | PRD, UX, constraints | technical_design.md, ADR draft | Architecture / System |
| Architecture Critic | technical_design | arch_review.md, risks | Architecture / Knowledge |
| QA Lead | PRD, Tech Design | quality_plan.md, test_matrix.md | Quality |
| State Synthesizer | all artifacts | project_state.yaml | 全局状态 |

## 5. Intent Intake

目标：把模糊想法变成结构化意图。

输出：

```yaml
intent:
  raw: "..."
  project_name: null
  desired_outcome: null
  target_user: null
  constraints: []
  non_goals: []
  known_risks: []
  target_stage: "local_mvp"
  time_budget: null
  confidence: low
```

必须澄清：

- 你想解决什么问题？
- 给谁解决？
- 第一阶段希望达到什么状态？
- 明确不做什么？
- 有哪些资源和技术约束？

## 6. Product Lead Pass

目标：生成第一版产品判断。

输出必须包含：

- 目标用户。
- 核心场景。
- 当前替代方案。
- MVP 范围。
- Must / Should / Won’t。
- 成功标准。
- 高风险假设。

## 7. Product Critic Pass

目标：防止产品文档自证循环。

检查：

- 用户是否过宽？
- 问题是否真实？
- MVP 是否过大？
- 非目标是否足够明确？
- 成功标准是否可验证？
- 是否存在“为了完整而做”的功能？

输出：

```text
product_review.md
state_gaps.yaml
change_events.jsonl
```

## 8. UX / Interaction Pass

即使是 CLI 工具，也需要 UX 设计。

输出：

- 核心使用路径。
- 命令交互流程。
- 成功状态输出。
- 失败状态输出。
- 用户确认点。
- 空状态与错误提示。

## 9. Project Manager Pass

目标：不是排死计划，而是规划可推进状态序列。

输出：

```text
roadmap.md
state_targets.yaml
risk_log.yaml
```

核心问题：

```text
项目先达到什么状态，才能安全进入下一状态？
```

## 10. Tech Lead Pass

目标：生成初始技术方案。

输出必须包含：

- 技术栈选择。
- 模块边界。
- 数据模型草案。
- 文件系统协议。
- CLI 架构。
- Adapter 边界。
- ADR 草案。
- 技术风险。

## 11. Architecture Critic Pass

检查：

- 是否过度设计？
- 是否低估状态账本复杂度？
- 是否把任务误当目标？
- 是否存在上下文污染风险？
- 是否有无法回滚的决策？

## 12. QA Lead Pass

目标：定义质量策略，而不是事后补测试。

输出：

- 状态成熟度判定检查。
- Evidence 要求。
- 非代码产物 review checklist。
- CLI 测试策略。
- Fresh Context 测试策略。
- State Delta 回滚测试。

## 13. State Synthesizer Pass

目标：合成第一版项目状态。

输出：

```yaml
project_state:
  dimensions:
    intent:
      maturity: accepted
    product:
      maturity: reviewed
    ux:
      maturity: drafted
    architecture:
      maturity: drafted
    quality:
      maturity: drafted
    implementation:
      maturity: unknown
```

## 14. 启动完成门禁

进入执行前，必须满足：

```text
Intent 至少 accepted
Product 至少 reviewed
Architecture 至少 drafted
Quality 至少 drafted
至少有 1 个明确 Target State
至少有 1 个可执行 Intervention
```

否则不能进入 `progress plan` 与后续 Run 流程。

---

## 系统架构与模块边界

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

---

## 核心对象与数据模型

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

---

## Intervention 推进动作与执行协议

## 1. 定义

Intervention 是为推动项目状态变化而设计的推进动作。

```text
Intervention = State Gap → Target State 的行动方案
```

Task 不是一等核心。Task 是可执行粒度的 Intervention。

## 2. Intervention 类型

| 类型 | 说明 |
|---|---|
| intent_clarification | 澄清项目意图 |
| product_design | 产品定义、PRD、用户故事 |
| ux_design | 用户流程、交互、界面、CLI 输出体验 |
| system_design | 系统边界、数据流、模块关系 |
| architecture_decision | 架构方案、ADR、技术取舍 |
| planning | 路线图、状态目标、推进计划 |
| implementation | 代码实现 |
| quality_gap | 测试、验收、质量门禁补齐 |
| documentation | 文档和知识沉淀 |
| release | 部署、回滚、监控、发布准备 |
| feedback_analysis | 用户反馈分析 |
| meta | 重拆、重评估、重规划、协议修正 |
| repair | 修复验证失败结果 |

## 3. Intervention Contract

每个 Intervention 必须包含：

```yaml
id: IV-001
type: implementation
dimension: implementation
target_state: TS-001
title: "Implement intent intake command"
goal: "..."
why_now: []
in_scope: []
out_of_scope: []
inputs: []
outputs: []
acceptance: []
evidence_required: []
context_budget: {}
automation: {}
done_policy: {}
fallback_policy: {}
```

## 4. 必须回答的问题

每个 Intervention 必须能回答：

```text
它推动哪个状态维度？
当前状态是什么？
目标状态是什么？
为什么现在做？
完成后如何证明状态改变？
如果做不完，会产生什么 gap 或 event？
```

## 5. Ready 条件

一个 Intervention 只有满足以下条件才可执行：

```text
target_state 已定义
scope 明确
out_of_scope 明确
输入 artifact 存在
验收标准可检查
evidence_required 明确
context_budget 未超限
automation policy 允许当前执行模式
```

## 6. 执行边界

Intervention 不允许：

- 擅自修改目标状态。
- 引入未批准架构变更。
- 扩大 scope。
- 将未完成事项口头延期。
- 用“基本完成”替代 Evidence。
- 在同一上下文继续执行下一个 Intervention。

## 7. 失败处理

如果执行失败，必须产生以下之一：

| 结果 | 说明 |
|---|---|
| Repair Intervention | 小范围修复 |
| Clarification Gap | 需要产品/设计/架构澄清 |
| Change Event | 发现影响上游事实的事件 |
| Blocker | 当前推进动作被阻断 |
| Split Request | 任务过大，需要拆分 |

## 8. No Silent Deferral

错误示例：

```text
这个功能可以放到下一阶段。
```

正确输出：

```yaml
deferred_intervention:
  id: IV-019
  title: "Add token budget visualization"
  reason: "Not required for MVP target state TS-004."
  target_state: TS-012
  trigger: "After Context Capsule generator is validated."
  acceptance:
    - "CLI displays estimated context size."
```

## 9. Intervention 与旧任务池的关系

仍然可以按工作流维护池：

```text
product pool
ux pool
architecture pool
implementation pool
quality pool
release pool
meta pool
```

但池只是组织方式，不是目标。

调度器选择的是：

```text
下一步最有价值的状态变化
```

而不是：

```text
任务池中的下一个任务
```

---

## Fresh Context 上下文隔离协议

## 1. 背景

AI 任务质量下降的核心原因之一是上下文膨胀和注意力漂移。ProgressEngine 必须强制上下文隔离。

## 2. 核心规则

```text
One Intervention, One Fresh Context.
```

每个 Intervention 必须在新的上下文空间中执行。

## 3. 禁止继承完整聊天历史

下一轮 Run 不允许读取上一轮完整聊天。只能读取：

- Project State。
- 已接受 artifact。
- Ledger。
- 已应用 State Delta。
- 当前 Intervention。
- 相关文件。
- 必要 Evidence。

未落账的信息视为不存在。

## 4. Execution Session 与 Verification Session 分离

```text
Execution Session: 执行推进动作
Verification Session: 独立验证结果
```

执行者不能验证自己的完成状态。

## 5. Context Capsule

Context Capsule 是单个 Intervention 的上下文胶囊。

内容包括：

```text
项目快照
当前目标状态
当前 Intervention
相关 artifact 摘要
相关文件列表
非目标
验收标准
证据要求
执行规则
失败处理规则
```

## 6. Capsule 示例

```markdown
# Context Capsule: IV-007

## Project Snapshot
- Project: ProgressEngine
- Current Mode: Explore / Converge
- Current State: Product reviewed, Quality drafted, Implementation unknown

## Target State
TS-003: MVP success metrics accepted.

## Intervention
IV-007: Define measurable MVP success metrics.

## In Scope
- Define measurable success metrics.
- Map metrics to release gate.

## Out of Scope
- Do not change MVP feature scope.
- Do not introduce new modules.

## Evidence Required
- Updated PRD section.
- Product checklist pass.
- State Delta proposal.

## Rules
- Do not claim completion without acceptance mapping.
- Do not defer silently.
- Output remaining gaps explicitly.
```

## 7. Context Budget

每个 Intervention 必须声明上下文预算：

```yaml
context_budget:
  max_artifacts: 8
  max_files: 12
  max_acceptance_items: 7
  max_expected_diff_files: 8
  allow_full_repo_scan: false
```

如果超预算，系统必须执行：

```text
split intervention
```

而不是强行执行。

## 8. 执行模式

| 模式 | 说明 |
|---|---|
| prompt-only | 生成 Capsule，用户复制给 AI |
| manual-run | 用户人工执行，再录入 Evidence |
| shell-adapter | 调用本地命令或 AI CLI |
| api-adapter | 直接调用模型 API |
| verify-only | 只做验证 |

MVP 第一版优先支持：

```text
prompt-only + manual-run + verify-only
```

## 9. Session TTL

```text
Session TTL = 1 Intervention
```

一个会话完成一个 Intervention 后必须关闭。后续只能通过 State Delta、Evidence 和 Ledger 交接。

## 10. Split 触发条件

必须拆分的情况：

- 需要修改多个无关模块。
- 验收标准超过 7 条。
- 相关文件超过预算。
- 同时包含产品决策和代码实现。
- 同时包含架构变更和实现。
- Evidence 无法在单轮验证。

## 11. 上下文污染检测

Verifier 应检查：

- 输出是否引用了 Capsule 之外的未授权假设。
- 是否扩大 scope。
- 是否引入未落账决策。
- 是否把未完成事项口头延期。

---

## Evidence Verifier 证据验证协议

## 1. 目标

防止 AI 假完成，确保每次项目状态变化都有证据。

## 2. 基本规则

```text
Executor can implement.
Verifier decides whether state advanced.
```

执行者最多可以输出：

```text
implemented / evidence submitted
```

不能直接输出：

```text
done / state advanced
```

## 3. Evidence 类型

| 类型 | 示例 |
|---|---|
| code_diff | 修改的代码文件 |
| test_result | 测试命令和结果 |
| artifact_review | 文档 checklist 通过 |
| command_output | CLI 输出 |
| demo_result | 可运行演示 |
| user_feedback | 用户反馈或访谈记录 |
| decision_record | ADR 或决策记录 |
| risk_update | 风险状态变化 |
| release_check | 发布检查结果 |

## 4. 验证流程

```text
Collect Evidence
  ↓
Map Evidence to Acceptance Criteria
  ↓
Check Scope
  ↓
Check No Silent Deferral
  ↓
Check State Delta Claim
  ↓
Pass / Partial / Fail
```

## 5. 验收映射

每条 acceptance criterion 必须有结果：

```yaml
acceptance_mapping:
  - criterion: "CLI can generate context capsule."
    status: pass
    evidence: "tests/context_capsule_test.ts::generates_capsule"
  - criterion: "Missing artifact returns clear error."
    status: fail
    evidence: null
    required_action: "Create repair intervention."
```

状态：

```text
pass
fail
not_tested
not_applicable
blocked
```

## 6. 验证输出

```yaml
verification:
  id: VR-001
  run_id: RUN-001
  result: partial
  summary: "Implementation works for normal path, but missing artifact error is not tested."
  acceptance_mapping: []
  scope_check:
    result: pass
  evidence_check:
    result: partial
  silent_deferral_check:
    result: pass
  recommended_action:
    type: repair_intervention
    title: "Add missing artifact error test."
```

## 7. 不能接受的完成表述

以下表述不能作为完成证据：

```text
基本完成。
主要功能已经实现。
后续可以优化。
理论上应该可以。
我已经更新了相关内容。
```

必须替换为：

```text
哪个状态维度发生了什么变化？
哪条验收标准通过？
证据在哪里？
哪些未通过？
是否产生新的 gap？
```

## 8. Scope Check

Verifier 必须检查：

- 是否修改了 out_of_scope 文件。
- 是否引入新依赖。
- 是否改变架构。
- 是否绕过质量门禁。
- 是否更改项目状态但没有 State Delta。

## 9. 结果处理

| 结果 | 后续 |
|---|---|
| pass | 生成 State Delta Proposal |
| partial | 生成 Repair / Gap / Event |
| fail | 回滚或阻断 |
| blocked | 生成 blocker 和上游 clarification |

## 10. 独立上下文验证

Verification Session 必须使用新的上下文，只包含：

- Intervention Contract。
- Evidence。
- Diff / artifact changes。
- 验证规则。

不能继承执行者长篇解释。

---

## 非代码产物验证协议

## 1. 背景

代码可以通过测试、diff、运行命令验证。但产品、设计、架构、质量计划等非代码产物容易出现自证循环：

```text
我写了一个文档，所以状态推进了。
```

ProgressEngine 必须避免这种情况。

## 2. 非代码 Evidence 公式

```text
Non-code Evidence = Artifact + Checklist + Reviewer Result + Remaining Gaps
```

只有 artifact 不算充分证据。

## 3. Product / PRD 验证清单

PRD 至少包含：

- 目标用户。
- 核心问题。
- 使用场景。
- 当前替代方案。
- MVP 目标。
- Must / Should / Won’t。
- 非目标。
- 成功指标。
- 用户故事。
- 验收标准。
- 关键假设。
- 风险和依赖。

PRD reviewed 必须满足：

```text
字段完整
+ Product Critic 审查
+ 范围没有明显膨胀
+ 非目标明确
+ 成功指标可验证
```

PRD accepted 需要人工确认或策略 gate。

## 4. UX / Interaction 验证清单

UX 产物至少包含：

- 核心用户路径。
- 关键交互步骤。
- 成功状态。
- 失败状态。
- 空状态。
- 错误提示。
- 确认点。
- 对应 PRD 场景。

对于 CLI 产品，还要包含：

- 命令输入输出示例。
- 错误消息。
- 人工确认提示。
- 交互退出方式。

## 5. Technical Design 验证清单

技术设计至少包含：

- 技术栈选择及理由。
- 备选方案比较。
- 模块边界。
- 数据模型。
- 核心流程。
- 文件系统协议。
- 外部依赖。
- 错误处理。
- 安全/隐私考虑。
- 技术风险。
- ADR 索引。
- 明确不做什么。

reviewed 需要 Tech Critic 通过。

accepted 需要关键 ADR 接受。

validated 需要 Spike、测试或实现证明。

## 6. Quality Plan 验证清单

质量计划至少包含：

- 状态成熟度判定规则。
- 每类 Intervention 的 evidence 要求。
- 代码测试策略。
- 非代码 artifact review 策略。
- Fresh Context 检查。
- State Delta 检查。
- 回归测试。
- 发布门禁。

## 7. Release Strategy 验证清单

发布策略至少包含：

- 部署目标。
- 环境变量。
- 回滚方式。
- 日志与监控。
- 已知问题。
- 反馈入口。
- 发布阻断条件。

## 8. Reviewer Result

非代码验证输出：

```yaml
artifact_review:
  artifact: artifacts/prd.md
  reviewer_role: product_critic
  result: pass_with_notes
  checklist:
    target_user: pass
    non_goals: pass
    success_metrics: fail
  remaining_gaps:
    - G-003
  suggested_target_states:
    - TS-003
```

## 9. 状态升级规则

```text
artifact exists       → seed / drafted
checklist passed      → reviewed
human gate accepted   → accepted
real-world evidence   → validated
new conflicting event → stale / reopened
```

---

## Change Event 影响分析与失效传播

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

---

## State Delta 提案、应用与回滚协议

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

---

## CLI 与交互设计

## 1. CLI 目标

CLI 是 ProgressEngine MVP 的主要入口。它不应首先成为 AI 执行器，而应成为项目状态推进工具。

## 2. 命令总览

```bash
progress init
progress intake
progress assess
progress gaps
progress target
progress plan
progress capsule
progress run
progress evidence
progress verify
progress delta
progress event
progress state
progress spiral
```

## 3. 命令语义

### 3.1 `progress init`

初始化 `.progress/` 目录。

```bash
progress init --project progressengine
```

生成：

```text
.progress/project.yaml
.progress/state/project_state.yaml
.progress/policies/*
.progress/artifacts/*
```

### 3.2 `progress intake`

捕获初始意图。

```bash
progress intake --from intent.md
```

输出：

```text
.progress/artifacts/intent.md
.progress/state/project_state.yaml
```

### 3.3 `progress assess`

评估当前项目真实状态。

```bash
progress assess
```

输出：

```text
Project State Summary
State Maturity by Dimension
Detected Gaps
Stale Claims
Recommended Next Target Candidates
```

### 3.4 `progress gaps`

列出状态缺口。

```bash
progress gaps list
progress gaps show G-001
```

### 3.5 `progress target`

推荐目标状态。

```bash
progress target suggest
progress target approve TS-001
```

注意：`target` 不执行动作，只处理目标状态。

### 3.6 `progress plan`

把目标状态转成推进动作。

```bash
progress plan --target TS-001
```

输出：

```text
Intervention Proposal IV-001
```

### 3.7 `progress capsule`

生成 Fresh Context Capsule。

```bash
progress capsule --intervention IV-001
```

输出：

```text
.progress/runs/RUN-001/context_capsule.md
```

### 3.8 `progress run`

管理 Run 生命周期。

```bash
progress run start --intervention IV-001 --mode prompt-only
progress run close RUN-001
```

MVP 第一版中，`run start` 可以只生成上下文包，不直接调用模型。

### 3.9 `progress evidence`

录入证据。

```bash
progress evidence add --run RUN-001 --file evidence.yaml
progress evidence list --run RUN-001
```

### 3.10 `progress verify`

独立验证结果。

```bash
progress verify --run RUN-001
```

输出：

```text
verification.md
state_delta_proposal.yaml
```

### 3.11 `progress delta`

管理 State Delta。

```bash
progress delta review SD-001
progress delta apply SD-001
progress delta reject SD-001
progress delta rollback SD-001
```

### 3.12 `progress event`

管理 Change Event。

```bash
progress event add --type implementation_finding
progress event list
progress event show EVT-001
```

### 3.13 `progress state`

查看、刷新和回放项目状态。`delta apply` 负责写入状态；`state refresh` 负责重新评估派生缺口和状态摘要。

```bash
progress state show
progress state history
progress state refresh --after-delta SD-001
```

### 3.14 `progress spiral`

执行受控螺旋推进。

```bash
progress spiral --mode guarded --max-runs 3
```

每轮必须 fresh context。

## 4. 标准推进命令序列

```bash
progress assess
progress target suggest
progress target approve TS-001
progress plan --target TS-001
progress capsule --intervention IV-001
progress run start --intervention IV-001 --mode prompt-only
# 用户或 AI 执行
progress evidence add --run RUN-001 --file evidence.yaml
progress verify --run RUN-001
progress delta review SD-001
progress delta apply SD-001
progress state refresh --after-delta SD-001
progress assess
```

## 5. CLI 输出原则

- 输出当前状态，而不是只输出命令结果。
- 每个命令都说明下一步建议。
- 明确区分 proposal 和 applied。
- 不用“完成”描述未验证结果。
- 失败时给出 repair / gap / event 建议。

## 6. 交互示例

```text
$ progress assess

Project: progressengine
State version: PS-0005

Dimensions:
- Intent: accepted / complete
- Product: reviewed / partial
- UX: drafted / partial
- Architecture: drafted / in_progress
- Implementation: unknown / not_started
- Quality: drafted / partial

Top Gaps:
1. G-003 Product success metrics are weak.
2. G-005 Architecture adapter boundary unclear.
3. G-007 Quality evidence rules incomplete.

Recommended Target:
TS-003 Accept measurable MVP success metrics.
```

---

## 工作流与典型场景

## 1. 场景一：从 0 创建项目

```text
用户输入意图
  ↓
progress init
  ↓
progress intake
  ↓
角色流水线生成第一版 artifacts
  ↓
progress assess
  ↓
progress target suggest
  ↓
生成第一个 Target State
```

示例：

```bash
progress init --project my-tool
progress intake --from intent.md
progress assess
progress target suggest
```

输出不是任务池，而是：

```text
当前项目状态
主要状态缺口
推荐目标状态
建议推进动作
```

## 2. 场景二：产品状态不清，阻止继续编码

状态：

```text
Implementation ready tasks exist, but Product State is weak.
```

系统行为：

```text
不继续执行代码任务
  ↓
推荐产品澄清 Target State
  ↓
生成 product_clarification Intervention
```

## 3. 场景三：执行中发现架构缺口

执行 `IV-008 Implement context capsule generator` 时发现：

```text
artifact priority rules missing
```

系统行为：

```text
生成 EVT-002 implementation_finding
  ↓
technical_design reopened
  ↓
IV-008 blocked
  ↓
生成 TS-010 artifact priority rules accepted
  ↓
生成 IV-020 define artifact priority rules
```

这是正常的螺旋推进，不是失败。

## 4. 场景四：AI 假完成被拦截

Executor 输出：

```text
功能已经基本完成，后续可以补异常路径。
```

Verifier 检测：

```text
missing acceptance mapping
silent deferral detected
error path untested
```

结果：

```text
verification: fail
state_delta: not proposed
new intervention: IV-021 add error-path tests
```

## 5. 场景五：非代码产物验证

用户更新 PRD。

系统不直接升级 Product State，而是：

```text
PRD artifact exists
  ↓
Product Checklist
  ↓
Product Critic Review
  ↓
State Delta Proposal
  ↓
Apply
```

如果成功指标仍然不清楚，则 Product State 保持 reviewed / partial，不升级到 accepted。

## 6. 场景六：上下文超预算

Intervention 需要读取 30 个文件和 15 条验收标准。

系统输出：

```text
Context budget exceeded.
This intervention must be split.
```

生成：

```text
META intervention: split IV-030
```

## 7. 场景七：发布前状态评估

发布前运行：

```bash
progress assess --mode release
```

系统检查：

- Implementation 是否 validated。
- Quality 是否 accepted/validated。
- Delivery 是否 reviewed/accepted。
- Known gaps 是否存在 release blocker。
- Rollback 是否定义。
- Feedback channel 是否存在。

## 8. 场景八：持续螺旋推进

```bash
progress spiral --mode guarded --max-runs 3
```

每轮：

```text
assess
select target state
plan intervention
build fresh capsule
execute / prompt-only
verify
propose state delta
apply if allowed
reassess
```

如果任何一轮产生 high severity event，spiral 停止，等待人工 gate。

---

## MVP 范围与路线图

## 1. MVP 定义

ProgressEngine MVP 的目标不是自动完成整个软件项目，而是证明：

```text
一个模糊项目意图可以被转化为可审查项目状态，
并通过目标状态、推进动作、隔离上下文、证据验证和 State Delta，
完成至少一轮真实的项目状态推进。
```

## 2. Must Have

### 2.1 Project State

- `.progress/` 初始化。
- Project State schema。
- 状态维度与成熟度矩阵。
- State Gap 记录。

### 2.2 从 0 启动

- intent intake。
- 角色流水线 prompt 模板。
- 初始 artifacts 生成。
- 初始 Project State 合成。

### 2.3 Target State

- gaps list。
- target suggest。
- target scoring。
- target approve。

### 2.4 Intervention

- Intervention schema。
- plan target to intervention。
- readiness check。

### 2.5 Fresh Context

- context capsule 生成。
- context budget 检查。
- prompt-only run start。

### 2.6 Evidence / Verification

- evidence add。
- acceptance mapping。
- verifier checklist。
- State Delta proposal。

### 2.7 State Delta

- delta apply。
- delta reject。
- delta rollback。
- state history。

### 2.8 Change Event

- event add/list/show。
- basic impact analysis。
- mark artifact stale/reopened。

## 3. Should Have

- Mermaid 图生成。
- 基础 TUI。
- Git diff 检查。
- 自动检测 stale interventions。
- shell-adapter 调用测试命令。
- markdown/html report。

## 4. Won’t Have

第一阶段不做：

- Web SaaS。
- 多用户权限。
- 实时 agent 编排。
- 自动调用所有模型。
- 自动发布生产环境。
- 全自动高风险架构决策。
- 复杂项目组合管理。

## 5. 版本路线图

### v0.1 — State Loop MVP

目标：跑通状态推进闭环。

功能：

```text
init / intake / assess / gaps / target / plan / capsule / evidence / verify / delta apply
```

成功标准：

```text
能从一个意图生成第一版 project state，并完成一轮 State Delta 应用。
```

### v0.2 — Bootstrap Role Pipeline

目标：强化从 0 启动。

功能：

- Product Lead Pass。
- Product Critic Pass。
- Tech Lead Pass。
- QA Lead Pass。
- State Synthesizer。

成功标准：

```text
能为新项目生成可审查 artifacts 和初始 target states。
```

### v0.3 — Change Event + Reassessment

目标：支持螺旋式回退。

功能：

- Change Event 捕获。
- 影响分析。
- stale/reopened 标记。
- intervention invalidation。

### v0.4 — Guarded Spiral

目标：连续推进，但每轮 fresh context。

功能：

```bash
progress spiral --mode guarded --max-runs N
```

### v1.0 — Adapter Integration

目标：连接外部 AI 执行工具。

支持：

- shell adapter。
- API adapter。
- GitHub/Codex/Claude Code 等执行接口。

## 6. MVP 验收标准

MVP 通过标准：

```text
1. 可以初始化新项目。
2. 可以记录原始意图。
3. 可以生成并评估 Project State。
4. 可以识别 State Gap。
5. 可以推荐 Target State。
6. 可以生成 Intervention。
7. 可以为 Intervention 生成 Context Capsule。
8. 可以收集 Evidence。
9. 可以独立 Verify。
10. 可以生成并应用 State Delta。
11. 可以在下一轮 assess 中看到状态变化。
```

## 7. 第一批推进动作

建议从这些动作开始实现：

```text
IV-001 Define project_state schema
IV-002 Implement progress init
IV-003 Implement intent intake
IV-004 Implement state assessment from static files
IV-005 Implement gap list
IV-006 Implement target scoring
IV-007 Implement intervention schema
IV-008 Implement context capsule generator
IV-009 Implement evidence schema
IV-010 Implement verifier checklist
IV-011 Implement state delta apply/rollback
```

---

## 质量体系与风险管理

## 1. 质量目标

ProgressEngine 的质量目标不是“没有 bug”，而是：

```text
项目状态变化可信、可追溯、可回滚。
```

## 2. 质量门禁

### 2.1 State Assessment Gate

检查：

- 状态维度完整。
- 成熟度枚举合法。
- Evidence refs 存在。
- Gap refs 存在。

### 2.2 Target Selection Gate

检查：

- Target State 有明确 from/to。
- 评分模型完整。
- why_now 合理。
- 对应 gap 存在。

### 2.3 Intervention Readiness Gate

检查：

- target_state 存在。
- in_scope/out_of_scope 明确。
- inputs 存在。
- acceptance 可验证。
- evidence_required 明确。
- context budget 未超限。

### 2.4 Fresh Context Gate

检查：

- Context Capsule 是新生成。
- 未携带上一轮完整 transcript。
- 包含必要事实源。
- 未包含无关上下文。

### 2.5 Evidence Gate

检查：

- Evidence 映射 acceptance。
- 文件/命令/审查结果存在。
- 非代码 artifact 有 checklist。

### 2.6 Delta Apply Gate

检查：

- Verifier 通过。
- Policy 允许。
- 可回滚。
- 状态历史可写入。

## 3. 测试策略

| 模块 | 测试类型 |
|---|---|
| Schema | fixture validation |
| CLI | command output tests |
| State Engine | state transition tests |
| Target Planner | scoring tests |
| Capsule Builder | context generation tests |
| Verifier | acceptance mapping tests |
| Delta Apply | rollback tests |
| Event Engine | invalidation tests |

## 4. 高风险点

| 风险 | 影响 | 缓解 |
|---|---|---|
| 退化成任务管理器 | 偏离愿景 | State-first 硬规则 |
| 非代码产物假完成 | 状态虚假推进 | Artifact checklist + Critic |
| 自动化过度 | 误推进状态 | Guarded policy |
| 上下文污染 | AI 质量下降 | Fresh Context |
| 状态账本污染 | 后续判断错误 | Proposal / Apply / Rollback |
| Change Event 未传播 | 旧任务继续执行 | Invalidation log |
| 过度设计 | MVP 延迟 | CLI-first, prompt-only |

## 5. 质量指标

建议跟踪：

```text
false completion rate
state delta rejection rate
reopened artifact count
stale intervention count
average runs per accepted state delta
manual gate frequency
context budget exceed count
verification failure categories
```

## 6. 发布阻断条件

以下情况不能发布：

- State Delta apply/rollback 未验证。
- Fresh Context 不能稳定生成。
- Evidence schema 不完整。
- 非代码 artifact 无法 review。
- Change Event 不能标记 stale/reopened。
- CLI 不能跑通完整状态推进闭环。

---

## Guarded Spiral 自动化边界

## 1. 背景

ProgressEngine 可以自动推进，但不能无边界自动推进。自动化必须服务状态推进，同时避免错误状态被写入。

## 2. 自动化模式

| 模式 | 说明 |
|---|---|
| manual | 只生成建议和上下文，由人执行 |
| prompt-only | 生成 prompt，用户复制给 AI |
| guarded | 自动执行低风险步骤，关键点人工 gate |
| adapter | 调用外部 AI/CLI 工具执行 |
| autonomous | 后续高级模式，MVP 不做 |

## 3. Guarded Spiral 流程

```text
assess
  ↓
suggest target
  ↓
policy check
  ↓
plan intervention
  ↓
build capsule
  ↓
execute if allowed
  ↓
verify
  ↓
propose delta
  ↓
apply only if allowed
  ↓
reassess
```

## 4. 自动允许项

```yaml
auto_allowed:
  - state_assessment
  - gap_listing
  - target_scoring
  - context_capsule_generation
  - schema_validation
  - documentation_check
  - evidence_structure_check
  - stale_reference_detection
```

## 5. 需要人工 gate 的项

```yaml
human_gate_required:
  - product_scope_change
  - target_state_approval
  - architecture_decision
  - dependency_introduction
  - destructive_file_change
  - release_action
  - state_delta_apply
  - rollback
  - user_visible_behavior_change
```

## 6. 自动停止条件

Guarded Spiral 必须在以下情况下停止：

- 产生 high severity Change Event。
- 需要人工 gate。
- Context budget 超限。
- 连续两次 verification fail。
- 出现 silent deferral。
- State Delta 被 reject。
- Git working tree 有未解释变更。

## 7. 命令

```bash
progress spiral --mode guarded --max-runs 3
```

选项：

```bash
--allow-docs-only
--allow-low-risk-code
--no-delta-auto-apply
--stop-on-event high
```

## 8. 自动化不是长会话

Guarded Spiral 不能使用一个长 AI 会话连续完成多个动作。

必须是：

```text
Run 1 fresh context
  ↓
verify / delta / reassess
  ↓
Run 2 fresh context
  ↓
verify / delta / reassess
```

## 9. 安全边界

即使未来支持模型 API，以下操作默认禁止自动执行：

- 删除大量文件。
- 修改生产配置。
- 发布生产环境。
- 改变核心架构。
- 改变 MVP 范围。
- 写入不可回滚 State Delta。

---

## 实施计划与推进动作清单

## 1. 实施策略

ProgressEngine 自身也应该用 ProgressEngine 方法推进。也就是说，不从“实现所有功能”开始，而是先推进状态。

## 2. 初始目标状态序列

```text
TS-001 Project concept accepted
TS-002 Project state schema drafted
TS-003 CLI init can create .progress structure
TS-004 State assessment can read static project state
TS-005 Gap and target suggestion can run
TS-006 Intervention can generate context capsule
TS-007 Evidence and verification can produce state delta proposal
TS-008 State delta can apply and rollback
TS-009 One full state advancement loop validated
```

## 3. 第一阶段推进动作

| ID | 目标状态 | 类型 | 标题 |
|---|---|---|---|
| IV-001 | TS-001 | product | Finalize ProgressEngine project kernel |
| IV-002 | TS-002 | system | Define project_state schema |
| IV-003 | TS-003 | implementation | Implement progress init |
| IV-004 | TS-004 | implementation | Implement state assessment reader |
| IV-005 | TS-005 | implementation | Implement gap listing and target scoring |
| IV-006 | TS-006 | implementation | Implement context capsule generator |
| IV-007 | TS-007 | quality | Implement evidence verifier checklist |
| IV-008 | TS-008 | implementation | Implement state delta apply/rollback |
| IV-009 | TS-009 | meta | Run end-to-end state advancement fixture |

## 4. 建议技术栈

第一版可以使用：

```text
语言：TypeScript 或 Python
运行方式：本地 CLI
数据格式：YAML + Markdown + JSONL
测试：单元测试 + fixture tests
发布：npm package 或 pip package，二选一
```

选择标准：

- 如果你希望 CLI 快速开发和跨平台分发，TypeScript + Node 更合适。
- 如果你希望 YAML/文件处理和原型速度，Python 更简单。

建议第一版按你已有项目栈决定，不为了工具而换栈。

## 5. 里程碑

### M1：State Loop Skeleton

目标：完成 Project State 基础闭环。

交付：

- `.progress/` 初始化。
- project_state schema。
- assess 命令。

### M2：Target and Intervention

目标：从 gap 到 target，再到 intervention。

交付：

- gap list。
- target suggest。
- intervention plan。

### M3：Fresh Context and Evidence

目标：生成上下文，收集证据。

交付：

- context capsule。
- evidence schema。
- verifier 输出。

### M4：State Delta and Reassessment

目标：状态变化可应用、可回滚。

交付：

- verify 生成 State Delta Proposal；delta review/apply/rollback。
- state history。
- reassess。

### M5：Bootstrap Role Pipeline

目标：从 0 启动新项目。

交付：

- intent intake。
- role pass prompts。
- initial artifacts。
- initial state synthesis。

### M6：Change Event and Spiral

目标：支持螺旋式回退和自动推进。

交付：

- event engine。
- invalidation。
- guarded spiral。

## 6. 第一版不要做的事

- 不要先做漂亮 UI。
- 不要先做多模型调度。
- 不要先做完整自动化。
- 不要让任务池成为主产物。
- 不要把复杂项目管理功能提前塞进 MVP。

## 7. 验收用例

### 用例：从意图到第一轮状态推进

输入：

```text
我想做一个帮助个人开发者用 AI 推进软件项目的本地 CLI 工具。
```

期望输出：

```text
intent artifact
project_state
state gaps
target state
intervention
context capsule
evidence
verification
state delta
updated project state
```

成功判断：

```text
Project State 从 unknown/weak 推进到至少 seed/drafted，且有 Evidence。
```

---

## 运营方式、商业化与后续演进

## 1. 采用路径

建议采用路径：

```text
自用验证
  ↓
开源 CLI / 模板
  ↓
VS Code / IDE 集成
  ↓
团队版 / 托管版
  ↓
AI 工程治理平台
```

## 2. 自用阶段

目标：验证 ProgressEngine 是否真的解决你的问题。

成功标准：

- 你能用它启动一个新项目。
- 不再靠混乱摸索才进入台账阶段。
- 每轮 AI 执行都有 fresh context。
- 假完成能被发现。
- 项目状态能被持续推进。

## 3. 开源阶段

可开源内容：

- `.progress/` 协议。
- CLI。
- 模板。
- role pass prompts。
- schema。
- examples。

开源价值：

- 吸引独立开发者和 AI 编程用户。
- 收集真实项目反馈。
- 验证状态驱动方法论。

## 4. 商业化方向

### 4.1 Pro CLI

- 高级 report。
- 多项目 workspace。
- adapter 集成。
- GitHub / Linear / Jira sync。

### 4.2 Team Edition

- 多人状态账本。
- 角色审批。
- 项目状态仪表盘。
- 审计日志。

### 4.3 Hosted Platform

- Web Dashboard。
- Agent execution orchestration。
- 项目状态智能分析。
- 多仓库治理。

## 5. 目标用户扩展

从：

```text
独立开发者
```

扩展到：

```text
小团队技术负责人
AI coding team lead
研发效能负责人
技术咨询团队
内部工具团队
```

## 6. 长期演进

长期可以形成：

```text
AI-native Engineering Management System
```

但必须坚持：

```text
状态推进优先于任务管理
证据优先于口头完成
上下文隔离优先于长会话自动化
螺旋推进优先于瀑布计划
```

## 7. 护城河

真正的护城河不是 CLI，而是：

- 状态驱动方法论。
- 非代码产物验证协议。
- Fresh Context 执行协议。
- Evidence-backed State Delta。
- Change Event 失效传播。
- 真实项目使用数据形成的状态推进策略。

---

## 术语表

## ProgressEngine

持续推进项目状态的 AI 软件工程系统。

## Project State

当前项目真实状态，由多个维度组成。

## State Dimension

项目状态的一个维度，例如 Product、Architecture、Quality。

## Maturity

状态维度的可信成熟度，例如 drafted、reviewed、accepted、validated。

## State Gap

当前项目状态与期望状态之间的缺口。

## Target State

下一步希望项目达到的状态。

## Intervention

为了推动状态变化而设计的推进动作。Task 是其可执行形态之一。

## Run

一次隔离上下文执行。

## Fresh Context

为单个 Intervention 重新生成的独立上下文空间。

## Context Capsule

用于执行一个 Intervention 的最小充分上下文包。

## Evidence

证明状态变化的证据。

## Evidence Verifier

独立验证 Evidence 是否支持状态变化的模块或角色。

## State Delta

状态变化提案。只有通过验证和 gate 后才能 apply。

## Change Event

项目推进中产生的变化事件，例如实现发现、验证失败、用户反馈、架构冲突。

## Artifact

项目事实源文件，例如 PRD、技术设计、质量计划。

## Ledger

项目长期账本，包括状态、决策、风险、证据、反馈。

## Guarded Spiral

带人工 gate 和自动化边界的连续推进模式。

## No Silent Deferral

禁止口头延期；任何延期必须转成结构化 gap、event 或 intervention。

---

## 自检协议与开放缺口

## 1. 目的

ProgressEngine 的项目策划书不能只靠一次性生成。每次版本输出后，应进行多轮自检，目标是降低明显错误、遗漏、歧义和闭环缺陷。这里的“自检通过”不代表绝对无缺陷，而代表在当前检查协议下没有发现阻断级问题。

## 2. 自检边界

不能诚实承诺：

```text
100% 没有错误、遗漏、歧义和缺陷。
```

可以承诺：

```text
按既定检查项重复检查，直到没有发现新的阻断级或高优先级问题，并把剩余不确定性显式记录。
```

## 3. 自检 Pass

### Pass 1：愿景一致性

检查是否仍以“持续推进项目状态”为主轴，而不是退化成任务池、任务图或 agent 编排系统。

通过条件：

- Project State 是第一核心对象。
- Intervention 是推进动作，不是终极目标。
- Run 是执行单元，不是产品目标。
- 任务池 / 任务图仅作为中间表示出现。

### Pass 2：对象模型一致性

检查核心对象是否前后一致：

```text
ProjectState
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

通过条件：

- ID 前缀一致。
- 模板和正文一致。
- StateDelta 不绕过 Verification。
- ChangeEvent 能触发 reassess。

### Pass 3：主循环闭环

标准闭环：

```text
Assess
  ↓
Gap
  ↓
Target
  ↓
Plan Intervention
  ↓
Build Fresh Context
  ↓
Run
  ↓
Evidence
  ↓
Verify
  ↓
State Delta Proposal
  ↓
Apply / Reject / Rollback
  ↓
Reassess
```

通过条件：每个步骤都有命令、对象、输出和失败路径。

### Pass 4：上下文隔离

检查是否存在长会话连续执行多个推进动作的隐患。

通过条件：

- One Intervention, One Fresh Context。
- Execution Session 与 Verification Session 分离。
- 下一轮只能读取 Ledger / Artifact / State Delta，不读取完整 transcript。

### Pass 5：防假完成

检查是否允许 AI 自称完成。

通过条件：

- Executor 不能 self-close。
- Evidence 必须映射 acceptance。
- Verifier 必须独立。
- Silent deferral 必须变成显式 Intervention / Gap / Event。

### Pass 6：非代码产物验证

检查 PRD、UX、Architecture、Quality Plan 是否避免“写了文档所以完成”。

通过条件：

```text
Artifact + Checklist + Reviewer Result + Remaining Gaps
```

缺一不可。

### Pass 7：螺旋推进

检查是否支持前进、后退、重新评估和重新推进。

通过条件：

- ChangeEvent 可标记 artifact stale / reopened / superseded。
- 可生成新 Gap、Target、Intervention。
- 可让旧 Intervention stale / blocked / needs_review。

## 4. 当前 v3 自检结论

按上述 Pass 检查，v3 未发现阻断级愿景偏移。已修正的高优先级问题：

1. `progress update` 语义冗余，已改为 `progress state refresh`，状态写入由 `delta apply` 完成。
2. 成熟度枚举和矩阵不完全对齐，已补充 `seed` 和异常状态说明。
3. State Delta 模板缺少 proposal/apply/rollback 元数据，已补齐。
4. Change Event 模板偏弱，已补充 artifact effect、invalidates、propagation 字段。
5. 验证与状态写入边界不够硬，已明确 `verify` 只生成 proposal，`delta apply` 才能写状态。

## 5. 剩余不确定性

这些不是当前策划书的阻断项，但进入实现前仍应继续收敛：

- 各状态维度的判定规则仍需要在真实项目中校准。
- Target State 评分权重需要通过实践调整。
- 非代码 reviewer 可以先由 AI 扮演，但长期需要更严格的 checklist 和人工 gate。
- prompt-only 模式下，Fresh Context 依赖用户手动遵守复制边界；工具只能生成胶囊，不能完全强制外部聊天工具隔离。
- Guarded Spiral 的自动化边界需要在实现中以 policy 测试覆盖。

## 6. 后续实现前检查门槛

进入代码实现前，至少应完成：

- 所有 YAML 模板可被解析。
- CLI 命令语义与对象状态转移一致。
- 至少一个端到端 fixture：`intent → assess → target → intervention → capsule → evidence → verify → delta apply → reassess`。
- 至少一个反例 fixture：verification failed 后生成 Gap / Repair Intervention，而不是关闭状态。

---

## v3 版本修正清单

本版在 v2 基础上做了以下补强：

| 类别 | 修正 |
|---|---|
| CLI 闭环 | `progress update` 改为 `progress state refresh`，避免与 `delta apply` 重叠 |
| 成熟度模型 | 成熟度矩阵补充 `seed`，并单独说明 `stale / reopened / superseded / blocked` |
| State Delta | 补充 `verification_id`、`proposed_at`、`gate`、`apply`、`rollback_delta_id` |
| Change Event | 补充 artifact effect、invalidated evidence、propagation 字段 |
| Intervention | 补充 `expected_state_delta` 与 `verification_policy` |
| 验证边界 | 明确 `verify` 只生成 proposal，`delta apply` 才能修改 Project State |
| 自检机制 | 新增 `docs/22_自检协议与开放缺口.md` 与 `v3_自检与修正报告.md` |

本版仍不声称 100% 无缺陷，只声明按当前检查协议未发现阻断级问题。

---

## v3 自检与修正报告

## 1. 自检结论

v3 已按以下维度重复检查：

1. 愿景是否偏离。
2. Project State 是否仍是核心对象。
3. CLI 命令是否闭环。
4. 模板与正文是否一致。
5. State Delta 是否防止状态污染。
6. Change Event 是否支持螺旋推进。
7. Fresh Context 是否支持上下文切断。
8. Evidence Verifier 是否防止假完成。
9. 非代码产物是否避免自证循环。
10. Guarded Spiral 是否有自动化边界。

结论：没有发现阻断级缺陷；发现并修复了若干高/中优先级不一致。

## 2. 已修复问题

| 问题 | 修复 |
|---|---|
| `progress update` 与 `delta apply` 语义重叠 | 改为 `progress state refresh`，状态写入只由 `delta apply` 发生 |
| 成熟度枚举有 `seed`，矩阵无 `seed` | 成熟度矩阵增加 `seed` 列 |
| stale/reopened/superseded/blocked 未解释清楚 | 增加异常与治理状态说明 |
| State Delta 缺少 proposal/apply/rollback 元数据 | 增加 verification_id、proposed_at、gate、apply、rollback_delta_id |
| Change Event 模板缺少传播信息 | 增加 artifact effect、invalidates evidence、propagation |
| `verify` 与状态更新边界不够硬 | 明确 verify 只生成 proposal，delta apply 才写状态 |
| Intervention 模板对预期 State Delta 表达不足 | 增加 expected_state_delta 与 verification_policy |
| 状态转移缺少 stale / needs_review / reopened | Intervention 状态转移补充治理状态 |

## 3. 未承诺项

本报告不承诺 100% 无缺陷。它承诺的是：按当前检查协议，未发现新的阻断级问题；剩余不确定性已记录在 `docs/22_自检协议与开放缺口.md`。

---

