# Event List CLI Slice

本文定义 `IV-0022: Define next change event CLI slice` 的实现切片。它延续已接受的只读 CLI 路径：

```bash
progress state show
progress gaps list
progress target list
progress intervention list
progress run list
progress evidence list
progress verify list
progress delta list
```

下一条路径只读进入 Change Event 对象，不做 event add、影响分析、失效传播或状态写入。

## 1. 切片结论

第九条 Python CLI 用户路径选择：

```bash
progress event list
```

该命令读取 `.progress/events/*.yaml` 中的 Change Event 对象，并输出事件摘要。

选择它的原因：

- Change Event 协议要求实现、验证、反馈和外部变化都要落账，才能触发后续影响分析。
- `progress delta list` 已证明 State Delta Proposal 读取路径成立，下一步应验证 Change Event 对象读取路径。
- 该命令仍然只读，不会新增事件、传播失效、标记 stale 或修改 Project State。
- 它能为后续 `progress event add` 和 invalidation propagation 打基础，但本切片不进入写操作。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
progress event list
```

期望输出包含：

```text
Change events:
- EVT-0002 [medium] documentation_and_state_material_consistency (3 dimensions; human_review=true)
```

输出可以是纯文本；本切片不要求 JSON 输出、筛选、排序、`event add`、`event show` 或自动失效传播。

## 3. 输入、输出和状态影响

输入：

- `.progress/events/*.yaml`

输出：

- stdout 的 Change Event 摘要。
- stderr 的错误说明，用于 events 目录缺失、YAML 不可解析、缺少 `change_event` 根对象或必要字段缺失。
- process exit code：
  - `0`：读取和输出成功。
  - `2`：输入目录缺失、YAML 解析失败或 Change Event 对象结构不满足最小读取要求。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不新增 Change Event。
- 不传播 invalidation。
- 不标记 Intervention stale。
- 不更新 Project State maturity。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/events/__init__.py
src/progress_engine/events/event_list.py
tests/fixtures/minimal_progress_project/.progress/events/EVT-1001-sample-event.yaml
tests/test_cli_event_list.py
```

必要时可以小幅调整 `src/progress_engine/README.md`，但不得借机实现 `progress event add`、`progress event show` 或 invalidation propagation。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- YAML 读取继续使用 PyYAML。
- 默认从当前工作目录解析 `.progress/`。
- 只读取 `.progress/events/*.yaml` 中的 Change Event 对象。
- 每个 event 文件必须包含 `change_event` 根 mapping。
- 每个 event 至少读取 `id`、`type`、`severity`、`summary`、`affected_dimensions` 和 `requires_human_review`。
- 如果目录存在但没有 Change Event YAML，则输出 `- none`。
- 读取失败时错误信息不能伪装为 Change Event 列表。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-009-01 | `progress event list` 能读取 `.progress/events/*.yaml` 并输出 Change Event 摘要。 |
| AC-CLI-009-02 | 命令能读取 `change_event` 根 mapping 下的最小 event 字段。 |
| AC-CLI-009-03 | events 目录缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-009-04 | Change Event YAML 解析失败、缺少根 mapping 或必要字段缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-009-05 | pytest 覆盖成功路径、空目录路径、缺目录路径、malformed YAML 路径、缺根 mapping 路径和缺字段路径。 |
| AC-CLI-009-06 | `python3 scripts/check_repo.py` 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress event list` 或等效模块入口的示例输出。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明 `.progress/` 未被命令修改。

## 8. Out of Scope

本切片明确不做：

- `progress event add`
- `progress event show`
- Change Event 录入或编辑
- invalidation propagation
- 标记 stale / blocked
- 生成 Gap / Target / Intervention
- Project State 写入
- JSONL event log 写入
- JSON 输出、筛选、排序、分页和 TUI
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0023: Implement read-only event list CLI slice
```

`IV-0023` 的目标不是“实现 event engine”，而是只把 `progress event list` 变成可测试、可运行、只读的 Change Event 对象读取路径。
