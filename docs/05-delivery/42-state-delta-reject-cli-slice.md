# State Delta Reject CLI Slice

本文定义 `IV-0044: Define delta reject CLI slice` 的实现切片。它承接 `progress delta apply`、`progress delta rollback` 和只读 `progress state refresh` 之后的缺口：State Delta Proposal 已经能被接受并应用、能回滚、能被 refresh 观察，但未通过 human gate、证据失败或不再适用的 proposal 还缺少受控 reject 路径。

## 1. 切片结论

下一条 reject-focused 用户路径选择：

```bash
progress delta reject SDP-ID --approved-by NAME --reason TEXT
```

该命令只处理尚未写入 Project State 的 proposal。它执行最小可测试 reject：

- 解析 `.progress/deltas/{SDP-ID}-*.yaml`。
- 只允许拒绝 `status: proposed` 或 `status: accepted` 的 State Delta Proposal。
- 校验 proposal 明确要求 human approval，且 reject gate 已由 human approver 批准。
- 校验 `--approved-by` 与 reject gate approver 一致。
- 校验 `--reason` 为非空文本。
- 将 proposal 标记为 `rejected`，写入 reject metadata。
- 不修改 Project State，不追加 state history，不生成 Evidence、Verification、Gap、Target 或 Intervention。

选择它的原因：

- v0.1 的 State Delta lifecycle 不能只有 apply / rollback；失败或不再适用的 proposal 也必须能被明确关闭。
- reject 是 proposal lifecycle 操作，不是 Project State 变更；它不能绕过 State Delta apply gate 修改 Project State。
- 直接实现完整 delta management、自动 rejection、自动 verification generation 或通用 workflow engine 会扩大范围；本切片只定义 bounded reject。
- 该切片继续使用 Python 3.11+、stdlib-first argparse、YAML / JSONL repo-native 账本，不引入 Web UI、模型 API 或外部服务。

## 2. 用户路径

用户先审查 State Delta Proposal，并在 proposal 的 reject gate 中记录 reject approval。随后运行：

```bash
progress delta reject SDP-0044 --approved-by human_user --reason "Acceptance evidence failed verifier review."
```

成功输出应包含：

```text
State delta rejected:
- delta: SDP-0044
- rejected by: human_user
- reason: Acceptance evidence failed verifier review.
- proposal: .progress/deltas/SDP-0044-example.yaml

Next:
- progress delta list
- progress assess
```

失败时命令返回 exit code `2`，并说明 proposal 缺失、YAML 不可解析、proposal 状态不允许 reject、reject gate 未批准、approver 不匹配、reason 为空或 metadata 格式错误。

## 3. 输入、输出和状态影响

输入：

- `.progress/deltas/{SDP-ID}-*.yaml`
- proposal 的 `status`
- proposal 的 `requires_human_approval`
- proposal 的 `reject.gate`
- CLI 参数 `--approved-by NAME`
- CLI 参数 `--reason TEXT`

输出：

- stdout 的 reject 摘要。
- stderr 的错误说明。
- 修改后的 State Delta Proposal YAML。

process exit code：

- `0`：reject 成功。
- `2`：proposal 缺失、YAML 不可解析、proposal 状态不允许 reject、reject gate 缺失或未批准、approver 不匹配、reason 为空、reject metadata 格式错误或写入前置检查失败。

状态影响：

- 将目标 proposal 的 `status` 改为 `rejected`。
- 写入 `reject.rejected_by`、`reject.rejected_at`、`reject.reason` 和 `reject.previous_status`。
- 保留原 proposal 的 Evidence、Verification、acceptance summary、gate 和 apply metadata。
- 不修改 `.progress/state/project_state.yaml`。
- 不追加 `.progress/state/state_history.jsonl`。
- 不创建或修改 Gap、Target、Intervention、Run、Evidence 或 Change Event。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/deltas/__init__.py
src/progress_engine/deltas/delta_reject.py
tests/test_cli_delta_reject.py
tests/fixtures/minimal_progress_project/.progress/deltas/SDP-1004-reject-ready-delta.yaml
```

必要时可以小幅调整 `src/progress_engine/README.md` 和根 `README.md` 的 CLI 命令清单。不得借机实现 automatic rejection、verification generation、state refresh changes、target suggestion、Web UI、模型 API 或外部 agent。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- 默认从当前工作目录解析 `.progress/`。
- proposal 文件必须使用 `{SDP-ID}-*.yaml` canonical 解析规则。
- `delta_id` 必须以 `SDP-` 开头。
- `--reason` 必须为非空文本。
- 只允许 reject `status: proposed` 或 `status: accepted` 的 proposal。
- 不允许 reject `applied`、`rolled_back`、`rejected` 或未知状态的 proposal。
- proposal 必须声明 `requires_human_approval: true`。
- proposal 必须包含 `reject.gate.decision: approved`。
- `--approved-by` 必须匹配 `reject.gate.approved_by`。
- reject 成功时不追加 state history；Project State 只能由 delta apply / rollback 改变。
- 任一写入前置检查失败时，不得部分修改 proposal 文件。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-017-01 | `progress delta reject SDP-ID --approved-by NAME --reason TEXT` 能解析 canonical State Delta Proposal。 |
| AC-CLI-017-02 | 命令只允许 reject `proposed` 或 `accepted` proposal，并拒绝 `applied`、`rolled_back`、`rejected` 或未知状态。 |
| AC-CLI-017-03 | 命令要求 reject gate 已批准、approver 匹配且 reason 非空。 |
| AC-CLI-017-04 | 成功 reject 时只修改 proposal lifecycle metadata，不修改 Project State 或 state history。 |
| AC-CLI-017-05 | pytest 覆盖成功路径、缺 proposal、状态不允许、gate 未批准、approver 不匹配、reason 为空和重复 reject。 |
| AC-CLI-017-06 | `python3 scripts/check_repo.py` 和全量 pytest 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_cli_delta_reject.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress delta reject` 在 fixture 项目中的示例输出。
- git diff 摘要，证明没有修改 Project State 写入路径、state history 写入路径、verification generation、模型 API 或 Web UI。
- 对 proposal reject metadata、Project State 未变和 state history 未变的断言结果。

## 8. Proposal Lifecycle 与 Project State Write Gate 边界

本切片把 reject 明确限定为 proposal lifecycle：

- proposal lifecycle：允许把一个未应用 proposal 标记为 rejected，并记录 rejected_by、rejected_at、reason 和 previous_status。
- Project State write gate：无写入；reject 不能修改 Project State 成熟度、summary、evidence、open gaps 或 next targets。
- State History：无写入；reject 没有产生新的 Project State version。

因此，reject 不替代 verifier，也不替代 apply / rollback。它只关闭一个不应进入 Project State 的 proposal。

## 9. Out of Scope

本切片明确不做：

- 自动 rejection
- 自动生成或修改 Evidence / Verification
- 修改 `.progress/state/project_state.yaml`
- 追加 `.progress/state/state_history.jsonl`
- 创建 Gap / Target / Intervention
- 任意 YAML merge / 通用 patch engine
- reject 已 applied 的 State Delta
- 跨仓库、多项目 workspace、模型 API、Web UI 或外部 agent 调用

## 10. 下一步 Intervention

本切片被 verifier gate 接受后，下一步应创建并执行：

```text
IV-0045: Implement delta reject CLI slice
```

`IV-0045` 的目标不是“实现完整 delta management”，而是只把未应用 proposal 的最小 human-gated reject 路径变成可运行、可测试、可追溯的 repo-native lifecycle 写操作。
