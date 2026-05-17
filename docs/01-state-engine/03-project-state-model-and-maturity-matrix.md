# 项目状态模型与成熟度矩阵

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
