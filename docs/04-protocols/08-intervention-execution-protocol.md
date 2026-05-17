# Intervention 推进动作与执行协议

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
