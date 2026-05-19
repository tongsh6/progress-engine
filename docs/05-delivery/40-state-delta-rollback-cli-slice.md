# State Delta Rollback CLI Slice

本文定义 `IV-0040: Define delta rollback CLI slice` 的实现切片。它承接 `progress delta apply` 之后的缺口：状态账本已经能在 human gate 后前进，但还不能把一次已 apply 的 State Delta 通过受控命令回退。

## 1. 切片结论

下一条 rollback-focused 用户路径选择：

```bash
progress delta rollback SDP-ID --approved-by NAME
```

该命令只处理已经 `applied`、具备 apply metadata、并声明 `rollback.reversible: true` 的 State Delta Proposal。它执行最小可测试回退：

- 校验目标 proposal 已 apply，且 `apply.previous_state_version`、`apply.next_state_version` 和 state history 一致。
- 校验 rollback gate 已由 human approver 批准，`--approved-by` 与 gate metadata 一致。
- 从 state history 中定位 `previous_state_version` 对应的状态快照来源或 rollback-safe patch。
- 按明确 allow-list 恢复 `.progress/state/project_state.yaml`。
- 追加新的 state history 记录，说明哪个 applied delta 被 rollback。
- 将原 proposal 标记为 `rolled_back`，写入 rollback metadata。

选择它的原因：

- v0.1 质量边界要求 State Delta apply 后具备可回滚路径，否则状态写入仍然不可放心使用。
- 直接实现 reject、state refresh、通用 patch engine 或完整 delta management 会扩大范围；本切片只定义 rollback 的最小命令边界。
- rollback 必须和 apply 一样受 human gate 约束，不能由 executor 或 verifier 自动改写 Project State。
- 该切片继续使用 Python 3.11+、stdlib-first argparse、YAML / JSONL repo-native 账本，不引入 Web UI、模型 API 或外部服务。

## 2. 用户路径

用户先审查已经 apply 的 State Delta Proposal，并在 proposal 中记录 rollback gate approval。随后运行：

```bash
progress delta rollback SDP-0039 --approved-by human_user
```

成功输出应包含：

```text
State delta rolled back:
- delta: SDP-0039
- rolled back state: PS-0038
- restored state: PS-0037
- new state: PS-0039
- project_state: .progress/state/project_state.yaml
- state_history: .progress/state/state_history.jsonl

Next:
- progress state show
- progress assess
```

失败时命令返回 exit code `2`，并说明 proposal 状态、rollback gate、apply metadata、state history、reversibility 或 allow-list restore 字段中的具体问题。

## 3. 输入、输出和状态影响

输入：

- `.progress/deltas/{SDP-ID}-*.yaml`
- proposal 的 `apply.previous_state_version` 和 `apply.next_state_version`
- proposal 的 `rollback` metadata
- `.progress/state/project_state.yaml`
- `.progress/state/state_history.jsonl`

输出：

- stdout 的 rollback 摘要。
- stderr 的错误说明。
- 恢复后的 `.progress/state/project_state.yaml`。
- 追加一行 state history JSONL。
- 修改后的 State Delta Proposal rollback metadata。

process exit code：

- `0`：rollback 成功。
- `2`：proposal 缺失、YAML 不可解析、proposal 未 applied、rollback 不可逆、human gate 未批准、approver 不匹配、apply metadata 缺失、state history 不一致、restore patch 超出 allow-list 或写入前置检查失败。

状态影响：

- 只允许恢复 Project State 的 allow-list 字段：`open_state_gaps`、`aim_of_next_state`、dimension `summary`、dimension `maturity` 和 dimension `evidence`。
- 必须追加新的 `PS-*` state history 记录；不得删除已有 history。
- 必须保留原 apply history，并在 rollback history 中引用被回退的 delta 和被回退的 state version。
- 必须把 proposal 标记为 `rolled_back`，记录 `rolled_back_by`、`rolled_back_at`、`rolled_back_state_version`、`restored_state_version` 和 `rollback_history_version`。
- 不允许命令自己生成新 Evidence、Verification、State Delta Proposal、Gap、Target 或 Intervention。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/deltas/__init__.py
src/progress_engine/deltas/delta_rollback.py
src/progress_engine/state/project_state.py
src/progress_engine/state/state_history.py
tests/test_cli_delta_rollback.py
tests/fixtures/minimal_progress_project/.progress/deltas/SDP-1003-rollback-ready-delta.yaml
tests/fixtures/minimal_progress_project/.progress/evidence/EV-1003-rollback-ready.yaml
```

必要时可以小幅调整 `src/progress_engine/README.md` 和根 `README.md` 的 CLI 命令清单。不得借机实现 `progress delta reject`、`progress state refresh`、verification generation、target suggestion、Web UI、模型 API 或外部 agent。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- 默认从当前工作目录解析 `.progress/`。
- proposal 文件必须使用 `{SDP-ID}-*.yaml` canonical 解析规则。
- proposal `status` 必须为 `applied`，不能 rollback `proposed`、`accepted`、`rejected` 或已经 `rolled_back` 的 proposal。
- `rollback.reversible` 必须为 `true`。
- rollback gate 必须显式记录为 approved，且命令参数 `--approved-by` 必须匹配 gate approver。
- `apply.previous_state_version` 和 `apply.next_state_version` 必须存在，并且 `apply.next_state_version` 必须能在 state history 中匹配当前 applied delta。
- proposal 必须提供 `rollback.project_state_restore`，其结构与 apply 的 `project_state_update` allow-list 相同。
- rollback 不删除 state history；它只追加新 history 记录。
- Project State 恢复必须基于结构化 allow-list patch，不能执行任意 YAML merge。
- 任一写入前置检查失败时，不得部分修改 `.progress/state/project_state.yaml`、state history 或 proposal 文件。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-015-01 | `progress delta rollback SDP-ID --approved-by NAME` 能解析 canonical applied State Delta Proposal。 |
| AC-CLI-015-02 | 命令拒绝未 applied、不可逆、缺 apply metadata、缺 rollback gate 或 approver 不匹配的 proposal。 |
| AC-CLI-015-03 | 成功 rollback 时只按 allow-list 恢复 Project State，并追加新的 state history 记录。 |
| AC-CLI-015-04 | 成功 rollback 时将 proposal 标记为 `rolled_back`，写入 rollback metadata，并保留原 apply metadata。 |
| AC-CLI-015-05 | pytest 覆盖成功路径、未 applied、不可逆、gate 未批准、history 不一致、patch 越界和重复 rollback。 |
| AC-CLI-015-06 | `python3 scripts/check_repo.py` 和全量 pytest 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_cli_delta_rollback.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress delta rollback` 在 fixture 项目中的示例输出。
- git diff 摘要，证明没有实现 reject、state refresh、verification generation、模型 API 或 Web UI。
- 对 Project State、state history 和 proposal rollback metadata 的断言结果。

## 8. Reject 与 State Refresh 边界

本切片不实现 reject 命令。未批准、证据缺失或验收失败的 proposal 只能继续停留在原状态，不能由 rollback 命令标记为 rejected。

本切片不实现 state refresh。rollback 后的 Project State 是否需要重新评估，必须由后续独立 Target State 和 Intervention 定义，不能在本命令中自动生成 Gap、Target 或 Evidence。

## 9. Out of Scope

本切片明确不做：

- `progress delta reject`
- `progress state refresh`
- Verification 或 State Delta Proposal 自动生成
- Evidence 录入或编辑
- 任意 YAML merge / 通用 patch engine
- 自动创建 Gap / Target / Intervention
- 自动 human approval
- 跨仓库、多项目 workspace、模型 API、Web UI 或外部 agent 调用

## 10. 下一步 Intervention

本切片被 verifier gate 接受后，下一步应创建并执行：

```text
IV-0041: Implement delta rollback CLI slice
```

`IV-0041` 的目标不是“实现完整 delta management”，而是只把 gate 后的最小 State Delta rollback 路径变成可运行、可测试、可追溯的 repo-native 写操作。
