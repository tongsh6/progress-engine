# 从 0 启动角色流水线

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
