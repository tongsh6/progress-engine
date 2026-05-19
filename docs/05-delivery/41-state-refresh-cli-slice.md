# State Refresh CLI Slice

本文定义 `IV-0042: Define state refresh CLI slice` 的实现切片。它承接 `progress delta apply` 和 `progress delta rollback` 之后的缺口：状态账本已经能受控前进和回退，但还缺少一个专门的、只读的状态再观察入口来核对当前 Project State 与 state history、open gaps、next targets 是否对齐。

## 1. 切片结论

下一条 state refresh-focused 用户路径选择：

```bash
progress state refresh [--after-delta SDP-ID]
```

该命令在 v0.1 中是只读 reconciliation 命令。它不刷新写入 `.progress/state/project_state.yaml`，不创建 Gap、Target、Intervention、Evidence 或 State Delta Proposal，也不调用模型。它只读取现有账本并输出当前状态观察：

- 当前 Project State 的 project、phase 和 dimension maturity。
- 最新 state history entry。
- 可选 `--after-delta SDP-ID` 与 state history 中 applied delta 的匹配结果。
- 当前 `open_state_gaps` 对应的 Gap 摘要。
- 当前 `aim_of_next_state` 对应的 Target 摘要。
- 下一步建议命令，例如 `progress gaps list`、`progress target list`、`progress intervention list`。

选择它的原因：

- apply / rollback 已经是受 human gate 约束的写路径；refresh 不应绕过 gate 改写 Project State。
- `progress assess` 已提供总体摘要，但 refresh 需要面向 state history 之后的再观察，尤其是确认最新 delta 是否已经体现在当前 open gaps / next targets 中。
- 直接实现 reject、自动 gap generation、state recomputation 或完整 delta management 会扩大 v0.1 范围；本切片只定义只读观察路径。
- 该切片继续使用 Python 3.11+、stdlib-first argparse、YAML / JSONL repo-native 账本，不引入 Web UI、模型 API 或外部服务。

## 2. 用户路径

用户在执行 `delta apply` 或 `delta rollback` 后运行：

```bash
progress state refresh --after-delta SDP-0041
```

成功输出应包含：

```text
State refresh:
- project: progress-engine
- phase: repo_bootstrap
- latest state: PS-0040
- latest delta: SDP-0041
- requested delta: SDP-0041 (matched)

Maturity:
- implementation: drafted
- quality: reviewed

Open gaps:
- SG-0032 [implementation] ...

Next targets:
- TS-0042 [implementation] next state refresh slice defined

Next:
- progress gaps list
- progress target list
- progress intervention list
```

如果没有传入 `--after-delta`，命令仍输出最新 state history 和当前 Project State 观察。若传入的 delta 不存在于 state history，或不是最新 applied delta，应返回 exit code `2` 并给出清晰错误，避免用户误以为状态已经被指定 delta 推进。

## 3. 输入、输出和状态影响

输入：

- `.progress/state/project_state.yaml`
- `.progress/state/state_history.jsonl`
- `.progress/gaps/{SG-ID}-*.yaml`
- `.progress/targets/{TS-ID}-*.yaml`
- 可选 CLI 参数 `--after-delta SDP-ID`

输出：

- stdout 的 state refresh 摘要。
- stderr 的错误说明。

process exit code：

- `0`：refresh 观察成功。
- `2`：Project State 缺失、YAML 不可解析、state history 缺失或不可解析、`--after-delta` 格式错误、指定 delta 未出现在 history、指定 delta 与最新 history 不匹配、open gap / next target 引用无法解析。

状态影响：

- 不修改 `.progress/state/project_state.yaml`。
- 不追加 `.progress/state/state_history.jsonl`。
- 不修改任何 State Delta Proposal。
- 不创建或修改 Gap、Target、Intervention、Run、Evidence 或 Change Event。
- 不把 CLI 输出视为新的 Project State；状态变化仍只能通过 Evidence、Verification、State Delta Proposal 和 human-gated apply / rollback 写入。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/state/__init__.py
src/progress_engine/state/state_refresh.py
src/progress_engine/state/project_state.py
src/progress_engine/state/state_history.py
src/progress_engine/state/references.py
tests/test_cli_state_refresh.py
tests/fixtures/minimal_progress_project/.progress/state/state_history.jsonl
```

必要时可以小幅调整 `src/progress_engine/README.md` 和根 `README.md` 的 CLI 命令清单。不得借机实现 `progress delta reject`、自动 Evidence / Verification / State Delta generation、target suggestion、Web UI、模型 API 或外部 agent。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- 默认从当前工作目录解析 `.progress/`。
- `progress state refresh` 是只读命令。
- `--after-delta` 必须以 `SDP-` 开头。
- state history 必须按 JSONL 读取，不允许通过字符串拼接解析。
- 最新 history entry 至少读取 `state_version`、`applied_delta`、`applied_at`、`applied_by` 和 `summary`。
- 如果提供 `--after-delta`，它必须匹配最新 history entry 的 `applied_delta`。
- open gaps 和 next targets 必须使用 `{id}-*.yaml` canonical 引用解析规则。
- 输出可以复用 `assess` 的 maturity / gap / target 摘要风格，但必须包含 latest state 和 latest delta。
- 任一读取或解析失败时，不得创建或修改任何文件。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-016-01 | `progress state refresh` 能读取当前 Project State、最新 state history、open gaps 和 next targets 并输出 refresh 摘要。 |
| AC-CLI-016-02 | `progress state refresh --after-delta SDP-ID` 能确认指定 delta 是否匹配最新 state history。 |
| AC-CLI-016-03 | 命令在指定 delta 缺失、格式错误或不是最新 applied delta 时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-016-04 | 命令复用 canonical Gap / Target 引用解析规则，引用缺失或多匹配时失败。 |
| AC-CLI-016-05 | pytest 覆盖无参数成功路径、`--after-delta` 成功路径、delta 不匹配、history 缺失和引用缺失。 |
| AC-CLI-016-06 | `python3 scripts/check_repo.py` 和全量 pytest 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_cli_state_refresh.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress state refresh --after-delta SDP-ID` 在 fixture 项目中的示例输出。
- git diff 摘要，证明没有实现 reject、automatic generation、模型 API 或 Web UI。
- 对 Project State、state history 和 Gap / Target 引用读取的断言结果。

## 8. Read / Derive 与 Write Gate 边界

本切片把 refresh 明确限定为 read / derive：

- read：读取 Project State、state history、Gap 和 Target 对象。
- derive：从现有账本计算 latest state、latest delta、open gap 摘要和 next target 摘要。
- write：无写入；任何需要改变 Project State 的结果都必须另行产生 Evidence、Verification 和 State Delta Proposal，并经过 human gate apply。

因此，refresh 不替代 `delta apply`，不替代 `delta rollback`，也不替代未来可能存在的 verifier。

## 9. Out of Scope

本切片明确不做：

- `progress delta reject`
- 自动生成 Gap / Target / Intervention
- 自动生成 Evidence、Verification 或 State Delta Proposal
- 自动 human approval
- 修改 `.progress/state/project_state.yaml`
- 追加 `.progress/state/state_history.jsonl`
- 任意 YAML merge / 通用 patch engine
- 跨仓库、多项目 workspace、模型 API、Web UI 或外部 agent 调用

## 10. 下一步 Intervention

本切片被 verifier gate 接受后，下一步应创建并执行：

```text
IV-0043: Implement state refresh CLI slice
```

`IV-0043` 的目标不是“重新计算项目状态”，而是只把 apply / rollback 后的最小只读 state refresh 观察路径变成可运行、可测试、可追溯的 CLI 命令。
