# State History CLI Slice

本文定义 `IV-0024: Define next state history CLI slice` 的实现切片。它延续已接受的只读 CLI 路径：

```bash
progress state show
progress gaps list
progress target list
progress intervention list
progress run list
progress evidence list
progress verify list
progress delta list
progress event list
```

下一条路径只读进入 State History，不做 state refresh、delta apply 或状态写入。

## 1. 切片结论

第十条 Python CLI 用户路径选择：

```bash
progress state history
```

该命令读取 `.progress/state/state_history.jsonl` 中的状态历史记录，并输出历史摘要。

选择它的原因：

- State Delta 协议要求每次 apply 都写入 `.progress/state/state_history.jsonl`；在继续写操作前，应先能审查状态变更历史。
- `progress event list` 已证明 Change Event 读取路径成立，下一步回到 State History 读取路径，补齐状态闭环的只读观察面。
- 该命令仍然只读，不会 refresh、reassess、apply delta、修改 Project State 或追加 state history。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
progress state history
```

期望输出包含：

```text
State history:
- PS-0022 <- SDP-0023 by human_user at 2026-05-18T01:02:00+08:00
```

输出可以是纯文本；本切片不要求 JSON 输出、筛选、分页、`state refresh` 或 state replay。

## 3. 输入、输出和状态影响

输入：

- `.progress/state/state_history.jsonl`

输出：

- stdout 的 State History 摘要。
- stderr 的错误说明，用于 history 文件缺失、JSONL 不可解析或必要字段缺失。
- process exit code：
  - `0`：读取和输出成功。
  - `2`：输入文件缺失、JSONL 解析失败或 history entry 结构不满足最小读取要求。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不 refresh / reassess Project State。
- 不 apply State Delta。
- 不追加 state history。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/state/state_history.py
tests/fixtures/minimal_progress_project/.progress/state/state_history.jsonl
tests/test_cli_state_history.py
```

必要时可以小幅调整 `src/progress_engine/README.md`，但不得借机实现 `progress state refresh`、state replay 或 Delta 命令写操作。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- JSONL 读取使用 Python 标准库 `json`。
- 默认从当前工作目录解析 `.progress/`。
- 每条 history entry 至少读取 `state_version`、`applied_delta`、`applied_at`、`applied_by` 和 `summary`。
- 如果文件存在但没有非空 JSONL entry，则输出 `- none`。
- 读取失败时错误信息不能伪装为 State History 列表。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-010-01 | `progress state history` 能读取 `.progress/state/state_history.jsonl` 并输出 State History 摘要。 |
| AC-CLI-010-02 | 命令能读取每条 entry 的 `state_version`、`applied_delta`、`applied_at`、`applied_by` 和 `summary`。 |
| AC-CLI-010-03 | state history 文件缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-010-04 | JSONL 解析失败或必要字段缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-010-05 | pytest 覆盖成功路径、空文件路径、缺文件路径、malformed JSONL 路径和缺字段路径。 |
| AC-CLI-010-06 | `python3 scripts/check_repo.py` 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress state history` 或等效模块入口的示例输出。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明 `.progress/` 未被命令修改。

## 8. Out of Scope

本切片明确不做：

- `progress state refresh`
- state replay
- state rollback
- State Delta apply / reject / rollback
- Project State 写入
- state history 追加或编辑
- 自动选择或执行 Intervention
- JSON 输出、筛选、排序、分页和 TUI
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0025: Implement read-only state history CLI slice
```

`IV-0025` 的目标不是“实现 state replay”，而是只把 `progress state history` 变成可测试、可运行、只读的 State History 读取路径。
