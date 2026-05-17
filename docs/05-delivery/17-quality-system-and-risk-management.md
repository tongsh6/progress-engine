# 质量体系与风险管理

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
