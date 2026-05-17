# Next Read-only CLI Slice

本文定义 `IV-0008: Define next read-only state CLI slice` 的实现切片。它延续 `progress state show` 的策略：先扩展一个只读、可测试、不会修改 `.progress/` 的窄路径，而不是直接扩展成完整 CLI。

## 1. 切片结论

第二条 Python CLI 用户路径选择：

```bash
progress gaps list
```

该命令读取 `.progress/state/project_state.yaml` 中的 `open_state_gaps`，再读取 `.progress/gaps/*.yaml` 中对应 gap 对象，并输出当前 open gaps 的摘要。

选择它的原因：

- `progress state show` 已证明 Project State 可读；下一步应进入 State Gap，而不是跳到 delta apply 或自动执行。
- State Gap 是状态驱动闭环的第二个核心对象。
- 该命令仍然只读，不会创建、修改或删除 `.progress/` 文件。
- 它能复用 Project State loader，同时引入最小对象 loader，验证从单文件读取走向对象目录读取。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
progress gaps list
```

期望输出包含：

```text
Open gaps:
- SG-0001 [repo] repo bootstrap gap
- SG-0002 [product] v0.1 pilot validation gap
- SG-0003 [quality] progress object quality gate gap
- SG-0006 [implementation] next read-only CLI slice gap
```

具体标题可以来自 gap 的 `desired_state` 或文件名派生；本切片不要求复杂表格、筛选、排序或 JSON 输出。

## 3. 输入、输出和状态影响

输入：

- `.progress/state/project_state.yaml`
- `.progress/gaps/*.yaml`

输出：

- stdout 的 open gap 摘要。
- stderr 的错误说明，用于 Project State 缺失、gap 文件缺失、YAML 不可解析或必要字段缺失。
- process exit code：
  - `0`：读取和输出成功。
  - `2`：输入文件缺失、YAML 解析失败或 gap 对象结构不满足最小读取要求。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不生成 Evidence。
- 不生成 State Delta Proposal。
- 不更新 Project State maturity。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/gaps/__init__.py
src/progress_engine/gaps/gap_list.py
tests/fixtures/minimal_progress_project/.progress/gaps/SG-1001-sample-gap.yaml
tests/test_cli_gaps_list.py
```

必要时可以小幅调整 `tests/fixtures/minimal_progress_project/.progress/state/project_state.yaml` 和 `src/progress_engine/README.md`，但不得借机实现其他命令。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- YAML 读取继续使用 PyYAML。
- 默认从当前工作目录解析 `.progress/`。
- 只列出 Project State `open_state_gaps` 中声明的 gap。
- 每个 gap 至少读取 `id`、`dimension`、`status`、`desired_state`。
- 如果 open gap id 没有对应文件，命令必须返回 exit code `2`，避免状态账本产生静默漂移。
- 读取失败时错误信息不能伪装为 gap 列表。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-002-01 | `progress gaps list` 能读取 Project State 的 `open_state_gaps` 并输出对应 gap 摘要。 |
| AC-CLI-002-02 | 命令只列出 Project State 中声明的 open gaps，不扫描输出已 resolved gap。 |
| AC-CLI-002-03 | 缺少 gap 文件时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-002-04 | gap YAML 解析失败或必要字段缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-002-05 | pytest 覆盖成功路径、缺 gap 文件路径和 malformed gap 路径。 |
| AC-CLI-002-06 | `python3 scripts/check_repo.py` 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress gaps list` 或等效模块入口的示例输出。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明 `.progress/` 未被命令修改。

## 8. Out of Scope

本切片明确不做：

- `progress gaps show`
- `progress gaps create`
- `progress target suggest`
- `progress plan`
- `progress verify`
- `progress delta apply`
- 自动关闭 gap
- 根据代码或文档自动推断 gap
- Fresh Context Capsule 生成
- JSON 输出、筛选、排序、分页和 TUI
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0009: Implement read-only gaps list CLI slice
```

`IV-0009` 的目标不是“实现 gap management”，而是只把 `progress gaps list` 变成可测试、可运行、只读的最小对象目录读取路径。
