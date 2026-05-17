# 实施计划与推进动作清单

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
