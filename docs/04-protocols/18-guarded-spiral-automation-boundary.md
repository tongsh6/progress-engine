# Guarded Spiral 自动化边界

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
