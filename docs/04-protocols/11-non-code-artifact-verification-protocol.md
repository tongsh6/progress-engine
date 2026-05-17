# 非代码产物验证协议

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
