# 核心方法论：持续推进项目状态

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
