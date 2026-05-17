# Target List CLI Slice

本文定义 `IV-0010: Define next CLI state object slice` 的实现切片。它延续前两条已验证路径：

```bash
progress state show
progress gaps list
```

下一条路径只读进入 Target State 对象，不做 target suggest、approve 或自动规划。

## 1. 切片结论

第三条 Python CLI 用户路径选择：

```bash
progress target list
```

该命令读取 `.progress/state/project_state.yaml` 中的 `aim_of_next_state`，再读取 `.progress/targets/*.yaml` 中对应 Target State 对象，并输出当前 next target 摘要。

选择它的原因：

- 状态闭环顺序是 Project State -> State Gap -> Target State。
- `progress gaps list` 已证明对象目录读取路径成立，Target State 是下一个核心对象。
- 该命令仍然只读，不会 approve target、生成 intervention 或修改 Project State。
- 它能复用已有 Project State 读取方式，并新增最小 Target State loader。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
progress target list
```

期望输出包含：

```text
Next targets:
- TS-0010 [implementation] next target list CLI slice defined (review_ready)
```

输出可以是纯文本；本切片不要求 JSON 输出、筛选、排序、target suggest 或 approve。

## 3. 输入、输出和状态影响

输入：

- `.progress/state/project_state.yaml`
- `.progress/targets/*.yaml`

输出：

- stdout 的 next target 摘要。
- stderr 的错误说明，用于 Project State 缺失、target 文件缺失、YAML 不可解析或必要字段缺失。
- process exit code：
  - `0`：读取和输出成功。
  - `2`：输入文件缺失、YAML 解析失败或 target 对象结构不满足最小读取要求。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不 approve target。
- 不生成 Intervention。
- 不生成 Evidence 或 State Delta Proposal。
- 不更新 Project State maturity。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/targets/__init__.py
src/progress_engine/targets/target_list.py
tests/fixtures/minimal_progress_project/.progress/targets/TS-1001-sample-target.yaml
tests/test_cli_target_list.py
```

必要时可以小幅调整 `tests/fixtures/minimal_progress_project/.progress/state/project_state.yaml` 和 `src/progress_engine/README.md`，但不得借机实现 target suggest、approve 或 plan。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- YAML 读取继续使用 PyYAML。
- 默认从当前工作目录解析 `.progress/`。
- 只列出 Project State `aim_of_next_state` 中声明的 target。
- 每个 target 至少读取 `id`、`name`、`primary_dimension`、`status`。
- 如果 next target id 没有对应文件，命令必须返回 exit code `2`，避免状态账本产生静默漂移。
- 读取失败时错误信息不能伪装为 target 列表。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-003-01 | `progress target list` 能读取 Project State 的 `aim_of_next_state` 并输出对应 Target State 摘要。 |
| AC-CLI-003-02 | 命令只列出 Project State 中声明的 next targets，不扫描输出所有 targets。 |
| AC-CLI-003-03 | 缺少 target 文件时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-003-04 | target YAML 解析失败或必要字段缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-003-05 | pytest 覆盖成功路径、缺 target 文件路径和 malformed target 路径。 |
| AC-CLI-003-06 | `python3 scripts/check_repo.py` 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress target list` 或等效模块入口的示例输出。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明 `.progress/` 未被命令修改。

## 8. Out of Scope

本切片明确不做：

- `progress target suggest`
- `progress target approve`
- `progress target reject`
- `progress plan`
- Intervention 生成
- Target scoring 或排序
- 自动选择 next target
- State Delta apply
- Fresh Context Capsule 生成
- JSON 输出、筛选、排序、分页和 TUI
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0011: Implement read-only target list CLI slice
```

`IV-0011` 的目标不是“实现 target planning”，而是只把 `progress target list` 变成可测试、可运行、只读的 Target State 读取路径。
