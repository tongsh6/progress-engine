# Evidence Verifier 证据验证协议

## 1. 目标

防止 AI 假完成，确保每次项目状态变化都有证据。

## 2. 基本规则

```text
Executor can implement.
Verifier decides whether state advanced.
```

执行者最多可以输出：

```text
implemented / evidence submitted
```

不能直接输出：

```text
done / state advanced
```

## 3. Evidence 类型

| 类型 | 示例 |
|---|---|
| code_diff | 修改的代码文件 |
| test_result | 测试命令和结果 |
| artifact_review | 文档 checklist 通过 |
| command_output | CLI 输出 |
| demo_result | 可运行演示 |
| user_feedback | 用户反馈或访谈记录 |
| decision_record | ADR 或决策记录 |
| risk_update | 风险状态变化 |
| release_check | 发布检查结果 |

## 4. 验证流程

```text
Collect Evidence
  ↓
Map Evidence to Acceptance Criteria
  ↓
Check Scope
  ↓
Check No Silent Deferral
  ↓
Check State Delta Claim
  ↓
Pass / Partial / Fail
```

## 5. 验收映射

每条 acceptance criterion 必须有结果：

```yaml
acceptance_mapping:
  - criterion: "CLI can generate context capsule."
    status: pass
    evidence: "tests/context_capsule_test.ts::generates_capsule"
  - criterion: "Missing artifact returns clear error."
    status: fail
    evidence: null
    required_action: "Create repair intervention."
```

状态：

```text
pass
fail
not_tested
not_applicable
blocked
```

## 6. 验证输出

```yaml
verification:
  id: VR-001
  run_id: RUN-001
  result: partial
  summary: "Implementation works for normal path, but missing artifact error is not tested."
  acceptance_mapping: []
  scope_check:
    result: pass
  evidence_check:
    result: partial
  silent_deferral_check:
    result: pass
  recommended_action:
    type: repair_intervention
    title: "Add missing artifact error test."
```

## 7. 不能接受的完成表述

以下表述不能作为完成证据：

```text
基本完成。
主要功能已经实现。
后续可以优化。
理论上应该可以。
我已经更新了相关内容。
```

必须替换为：

```text
哪个状态维度发生了什么变化？
哪条验收标准通过？
证据在哪里？
哪些未通过？
是否产生新的 gap？
```

## 8. Scope Check

Verifier 必须检查：

- 是否修改了 out_of_scope 文件。
- 是否引入新依赖。
- 是否改变架构。
- 是否绕过质量门禁。
- 是否更改项目状态但没有 State Delta。

## 9. 结果处理

| 结果 | 后续 |
|---|---|
| pass | 生成 State Delta Proposal |
| partial | 生成 Repair / Gap / Event |
| fail | 回滚或阻断 |
| blocked | 生成 blocker 和上游 clarification |

## 10. 独立上下文验证

Verification Session 必须使用新的上下文，只包含：

- Intervention Contract。
- Evidence。
- Diff / artifact changes。
- 验证规则。

不能继承执行者长篇解释。
