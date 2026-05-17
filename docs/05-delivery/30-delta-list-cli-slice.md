# Delta List CLI Slice

本文定义 `IV-0020: Define next state delta CLI slice` 的实现切片。它延续已接受的只读 CLI 路径：

```bash
progress state show
progress gaps list
progress target list
progress intervention list
progress run list
progress evidence list
progress verify list
```

下一条路径只读进入 State Delta Proposal 对象，不做 delta apply、reject、rollback 或状态写入。

## 1. 切片结论

第八条 Python CLI 用户路径选择：

```bash
progress delta list
```

该命令读取 `.progress/deltas/*.yaml` 中的 State Delta Proposal 对象，并输出 proposal 摘要。

选择它的原因：

- State Delta 协议规定状态更新必须经过 Evidence、Verify、Propose、Gate、Apply、Reassess；在实现 apply 前，应先能审查已有 proposal。
- `progress verify list` 已证明 Verification review 只读路径成立，下一步应进入 State Delta Proposal 读取路径。
- 该命令仍然只读，不会 apply、reject、rollback、修改 Project State 或写入 state history。
- 它能为后续 `progress delta apply` 前的 proposal 可审查性打基础，但本切片不进入任何写操作。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
progress delta list
```

期望输出包含：

```text
State delta proposals:
- SDP-0019 [implementation] IV-0019 -> TS-0019 (applied; acceptance: 6 pass, 0 fail, 0 not_tested)
```

输出可以是纯文本；本切片不要求 JSON 输出、筛选、排序、`delta apply`、`delta reject` 或 `delta rollback`。

## 3. 输入、输出和状态影响

输入：

- `.progress/deltas/*.yaml`

输出：

- stdout 的 State Delta Proposal 摘要。
- stderr 的错误说明，用于 deltas 目录缺失、YAML 不可解析、缺少 `state_delta_proposal` 根对象或必要字段缺失。
- process exit code：
  - `0`：读取和输出成功。
  - `2`：输入目录缺失、YAML 解析失败或 State Delta Proposal 对象结构不满足最小读取要求。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不 apply / reject / rollback State Delta。
- 不更新 Project State。
- 不写入 state history。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/deltas/__init__.py
src/progress_engine/deltas/delta_list.py
tests/fixtures/minimal_progress_project/.progress/deltas/SDP-1001-sample-delta.yaml
tests/test_cli_delta_list.py
```

必要时可以小幅调整 `src/progress_engine/README.md`，但不得借机实现 `progress delta apply`、`progress delta reject` 或 `progress delta rollback`。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- YAML 读取继续使用 PyYAML。
- 默认从当前工作目录解析 `.progress/`。
- 只读取 `.progress/deltas/*.yaml` 中的 State Delta Proposal 对象。
- 每个 proposal 文件必须包含 `state_delta_proposal` 根 mapping。
- 每个 proposal 至少读取 `id`、`source_intervention`、`target_state_id`、`primary_dimension`、`status` 和 `acceptance_summary` 的 `pass`、`fail`、`not_tested`。
- 如果目录存在但没有 State Delta Proposal YAML，则输出 `- none`。
- 读取失败时错误信息不能伪装为 State Delta Proposal 列表。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-008-01 | `progress delta list` 能读取 `.progress/deltas/*.yaml` 并输出 State Delta Proposal 摘要。 |
| AC-CLI-008-02 | 命令能读取 `state_delta_proposal` 根 mapping 下的最小 proposal 字段和 acceptance summary。 |
| AC-CLI-008-03 | deltas 目录缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-008-04 | State Delta Proposal YAML 解析失败、缺少根 mapping 或必要字段缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-008-05 | pytest 覆盖成功路径、空目录路径、缺目录路径、malformed YAML 路径、缺根 mapping 路径和缺字段路径。 |
| AC-CLI-008-06 | `python3 scripts/check_repo.py` 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress delta list` 或等效模块入口的示例输出。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明 `.progress/` 未被命令修改。

## 8. Out of Scope

本切片明确不做：

- `progress delta apply`
- `progress delta reject`
- `progress delta rollback`
- Project State 写入
- state history 写入
- Verification artifact 生成
- Evidence 录入或编辑
- 自动选择或执行 Intervention
- JSON 输出、筛选、排序、分页和 TUI
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0021: Implement read-only delta list CLI slice
```

`IV-0021` 的目标不是“实现 delta management”，而是只把 `progress delta list` 变成可测试、可运行、只读的 State Delta Proposal 读取路径。
