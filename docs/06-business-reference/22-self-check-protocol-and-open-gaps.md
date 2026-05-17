# 自检协议与开放缺口

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
