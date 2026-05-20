# State Delta Lifecycle Pilot

本文定义 `IV-0046: Define State Delta lifecycle pilot validation slice` 的产品验证切片。它承接 `progress delta apply`、`progress state refresh`、`progress delta rollback` 和 `progress delta reject` 均已实现之后的缺口：这些能力各自可测试，但尚未作为一条 v0.1 lifecycle pilot 被统一验证。

## 1. 试点结论

下一条 pilot 验证路径选择：

```text
fixture project State Delta lifecycle pilot:
  apply an approved proposal
  refresh after the applied proposal
  rollback a reversible applied proposal
  reject a separate un-applied proposal
```

该 pilot 使用现有本地 fixture：

```text
tests/fixtures/minimal_progress_project/
```

它不调用模型 API、Web UI 或外部 agent，不修改真实项目 `.progress/`，只在 pytest `tmp_path` 中复制 fixture 并执行 CLI。

## 2. 选择理由

- `apply`、`rollback`、`reject` 和 `refresh` 已经分别实现；v0.1 需要产品级证据证明它们能组成可演示 lifecycle。
- 现有 bootstrap pilot 只覆盖 `init -> intake -> state show -> assess`，不覆盖 State Delta 写闭环。
- 使用 fixture 项目能保持验证稳定、快速、repo-native，不依赖外部环境。
- pilot 结果可以为后续更新 product summary 提供证据，移除“完整 State Delta 写闭环尚未验证”的旧判断。

## 3. 试点流程

在临时目录复制 fixture 后，执行以下分支：

### 3.1 Apply + Refresh 分支

```bash
progress delta apply SDP-1002 --approved-by human_user
progress state refresh --after-delta SDP-1002
```

期望观察：

- Project State implementation maturity 更新为 `drafted`。
- state history 追加 `PS-1002 <- SDP-1002`。
- `SDP-1002` status 变为 `applied`，并写入 apply metadata。
- `state refresh --after-delta SDP-1002` 能匹配 latest history。

### 3.2 Rollback 分支

在独立 fixture copy 中准备 rollback-ready state，然后执行：

```bash
progress delta rollback SDP-1003 --approved-by human_user
```

期望观察：

- Project State 恢复到 rollback restore 指定的 seed 状态。
- state history 追加 `ROLLBACK-SDP-1003`。
- `SDP-1003` status 变为 `rolled_back`，并写入 rollback metadata。

### 3.3 Reject 分支

在独立 fixture copy 中执行：

```bash
progress delta reject SDP-1004 --approved-by human_user --reason "Acceptance evidence failed verifier review."
```

期望观察：

- `SDP-1004` status 变为 `rejected`，并写入 rejected_by、rejected_at、reason 和 previous_status。
- Project State 不变。
- state history 不变。

## 4. 输入、输出和状态影响

输入：

- `tests/fixtures/minimal_progress_project/.progress/state/project_state.yaml`
- `tests/fixtures/minimal_progress_project/.progress/state/state_history.jsonl`
- `tests/fixtures/minimal_progress_project/.progress/deltas/SDP-1002-apply-ready-delta.yaml`
- `tests/fixtures/minimal_progress_project/.progress/deltas/SDP-1003-rollback-ready-delta.yaml`
- `tests/fixtures/minimal_progress_project/.progress/deltas/SDP-1004-reject-ready-delta.yaml`
- 现有 CLI 命令实现

输出：

- 新增 focused pytest，例如 `tests/test_state_delta_lifecycle_pilot.py`。
- pytest 断言结果。
- Evidence 记录命令结果和关键断言。

状态影响：

- 本定义切片不实现新代码。
- 下一轮实现切片只应新增或调整 pilot 测试，不改变 CLI runtime 行为，除非测试暴露真实缺陷。
- 真实项目状态仍只能通过 Evidence、Verification、State Delta Proposal 和 human-gated apply 更新。

## 5. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-PILOT-002-01 | pilot 文档明确代表性 State Delta lifecycle 验证场景。 |
| AC-PILOT-002-02 | pilot 步骤覆盖 apply、refresh、rollback 和 reject。 |
| AC-PILOT-002-03 | pilot 说明输入、输出、状态影响、out_of_scope 和 evidence_required。 |
| AC-PILOT-002-04 | pilot 要求 focused pytest 或等效本地命令验证。 |
| AC-PILOT-002-05 | pilot 不依赖模型 API、Web UI、外部 agent 或真实项目 `.progress/` 写入。 |

## 6. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_state_delta_lifecycle_pilot.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- apply + refresh 分支的关键断言摘要。
- rollback 分支的关键断言摘要。
- reject 分支的关键断言摘要。
- git diff 摘要，证明没有引入模型 API、Web UI 或外部 agent。

## 7. Out of Scope

本 pilot 明确不做：

- 自动生成 Evidence / Verification / State Delta Proposal
- 调用模型 API、Web UI 或外部 agent
- 修改真实项目 `.progress/` 作为 pilot 执行方式
- 发布流程、安装包或多项目 workspace
- 改变 `delta apply`、`delta rollback`、`delta reject` 或 `state refresh` 的命令语义

## 8. 下一步 Intervention

本切片被 verifier gate 接受后，下一步应创建并执行：

```text
IV-0047: Run State Delta lifecycle pilot validation
```

`IV-0047` 的目标不是扩展 CLI 功能，而是把完整 State Delta lifecycle 固化为本地可回归的产品验证证据。
