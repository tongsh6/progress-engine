# Fresh Context 上下文隔离协议

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
