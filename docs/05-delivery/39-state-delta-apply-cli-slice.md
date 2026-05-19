# State Delta Apply CLI Slice

本文定义 `IV-0038: Define next full state-loop write slice` 的实现切片。它承接 v0.1 试点后的缺口：当前 CLI 已能初始化、录入 intent、读取 Project State 和列出 State Delta Proposal，但尚未提供受控的 State Delta 写入路径。

## 1. 切片结论

下一条 State Delta 写闭环用户路径选择：

```bash
progress delta apply SDP-ID --approved-by NAME
```

该命令只处理已经存在、已经过 human gate 批准的 State Delta Proposal，并执行最小状态账本写入：

- 校验 proposal、verification、evidence 和 gate 字段满足 apply 前置条件。
- 按 allow-list 更新 `.progress/state/project_state.yaml`。
- 追加 `.progress/state/state_history.jsonl`。
- 将 proposal 标记为 `applied`，记录 apply metadata。

选择它的原因：

- v0.1 成功标准要求 State Delta Proposal 不能停留在只读列表，必须能在 gate 后进入状态历史。
- 直接实现完整 verify、apply、reject、rollback、refresh 会扩大范围；本切片只定义 apply 的最小可测试路径。
- `progress delta apply` 是 State Delta 写闭环的核心写操作，但必须被 human gate 约束，不能由 verifier 或 executor 自动污染 Project State。
- 该切片延续 Python 3.11+、stdlib-first argparse、YAML / JSONL repo-native 账本，不引入 Web UI、模型 API 或外部服务。

## 2. 用户路径

用户先审查 State Delta Proposal，并在 proposal 中记录 human gate approval。随后运行：

```bash
progress delta apply SDP-0039 --approved-by human_user
```

成功输出应包含：

```text
State delta applied:
- delta: SDP-0039
- previous state: PS-0037
- next state: PS-0038
- project_state: .progress/state/project_state.yaml
- state_history: .progress/state/state_history.jsonl

Next:
- progress state show
- progress assess
```

失败时命令返回 exit code `2`，并说明缺失的 gate、evidence、verification、patch 字段或引用漂移。

## 3. 输入、输出和状态影响

输入：

- `.progress/deltas/{SDP-ID}-*.yaml`
- proposal 中引用的 Evidence 对象
- `.progress/state/project_state.yaml`
- `.progress/state/state_history.jsonl`

输出：

- stdout 的 apply 摘要。
- stderr 的错误说明。
- 修改后的 `.progress/state/project_state.yaml`。
- 追加一行 state history JSONL。
- 修改后的 State Delta Proposal apply metadata。

process exit code：

- `0`：apply 成功。
- `2`：proposal 缺失、YAML 不可解析、gate 未批准、evidence / verification 引用缺失、proposal 含 fail / not_tested acceptance、patch 不在 allow-list、state history 不可写或状态版本冲突。

状态影响：

- 只允许根据 proposal 中显式、结构化的 `project_state_update` 更新 Project State。
- 只允许更新 `open_state_gaps`、`aim_of_next_state`、dimension `summary`、dimension `maturity` 和 dimension `evidence`。
- 只允许把当前 proposal 标记为 `applied` 并写入 `apply` metadata。
- 必须写入新的 `PS-*` state history 记录。
- 不允许命令自己生成新 Evidence、Verification、State Delta Proposal、Gap、Target 或 Intervention。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/deltas/__init__.py
src/progress_engine/deltas/delta_apply.py
src/progress_engine/state/project_state.py
src/progress_engine/state/state_history.py
tests/test_cli_delta_apply.py
tests/fixtures/minimal_progress_project/.progress/deltas/SDP-1002-apply-ready-delta.yaml
tests/fixtures/minimal_progress_project/.progress/evidence/EV-1002-apply-ready.yaml
```

必要时可以小幅调整 `src/progress_engine/README.md` 中的 CLI 命令清单。不得借机实现 `progress delta reject`、`progress delta rollback`、`progress state refresh`、verification generation、target suggestion、Web UI、模型 API 或外部 agent。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- 默认从当前工作目录解析 `.progress/`。
- proposal 文件必须使用 `{SDP-ID}-*.yaml` canonical 解析规则。
- proposal `status` 必须为 `proposed` 或 `accepted`，不能重复 apply 已 applied / rejected / rolled_back proposal。
- `requires_human_approval` 必须为 `true`，且 `gate.decision` 必须为 `approved`。
- 命令参数 `--approved-by` 必须与 gate metadata 一起写入 apply metadata；该参数不是自动审批。
- `acceptance_summary.fail` 和 `acceptance_summary.not_tested` 必须为 `0`。
- `evidence_refs` 中的本地路径必须存在。
- `project_state_update` 必须是 allow-list patch，不能执行任意 YAML merge。
- 写入前必须读取当前 state history 最后一条 `state_version`，生成下一个 `PS-*`。
- 任一写入前置检查失败时，不得部分修改 `.progress/state/project_state.yaml`、state history 或 proposal 文件。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-014-01 | `progress delta apply SDP-ID --approved-by NAME` 能解析 canonical State Delta Proposal。 |
| AC-CLI-014-02 | 命令拒绝未 human gate approved、缺 evidence refs、acceptance 有 fail / not_tested 或 patch 超出 allow-list 的 proposal。 |
| AC-CLI-014-03 | 成功 apply 时只按 `project_state_update` allow-list 修改 Project State，并追加 state history。 |
| AC-CLI-014-04 | 成功 apply 时将 proposal 标记为 `applied`，写入 applied_by、applied_at、previous_state_version、next_state_version 和 project_state_file。 |
| AC-CLI-014-05 | pytest 覆盖成功路径、未批准 gate、缺 evidence、acceptance 未全 pass、patch 越界和重复 apply。 |
| AC-CLI-014-06 | `python3 scripts/check_repo.py` 和全量 pytest 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_cli_delta_apply.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress delta apply` 在 fixture 项目中的示例输出。
- git diff 摘要，证明没有实现 reject、rollback、state refresh、verification generation、模型 API 或 Web UI。
- 对 Project State、state history 和 proposal apply metadata 的断言结果。

## 8. Rollback 与 Rejection 边界

本切片必须为后续 rollback 保留数据，但不实现 rollback 命令：

- apply 前必须记录 `previous_state_version`。
- State Delta Proposal 必须保留 `rollback.reversible` 和 `rollback.rollback_steps`。
- state history 必须能说明哪个 delta 生成了哪个 `PS-*`。

本切片不实现 reject 命令。未批准、证据缺失或验收未全 pass 的 proposal 只能被 `progress delta apply` 拒绝执行，不能被该命令标记为 rejected。

## 9. Out of Scope

本切片明确不做：

- `progress delta reject`
- `progress delta rollback`
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
IV-0039: Implement delta apply CLI slice
```

`IV-0039` 的目标不是“实现完整 delta management”，而是只把 gate 后的最小 State Delta apply 路径变成可运行、可测试、可回滚准备的 repo-native 写操作。
