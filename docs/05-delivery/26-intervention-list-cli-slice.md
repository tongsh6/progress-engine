# Intervention List CLI Slice

本文定义 `IV-0012: Define next CLI intervention object slice` 的实现切片。它延续已接受的只读 CLI 路径：

```bash
progress state show
progress gaps list
progress target list
```

下一条路径只读进入 Intervention 对象，不做 plan generation、run orchestration 或自动执行。

## 1. 切片结论

第四条 Python CLI 用户路径选择：

```bash
progress intervention list
```

该命令读取 `.progress/interventions/*.yaml` 中的 Intervention 对象，并输出当前 proposed / evidence_submitted / active 类状态的推进动作摘要。

选择它的原因：

- 状态闭环顺序是 Project State -> State Gap -> Target State -> Intervention。
- `progress target list` 已证明 Target State 目录读取路径成立，Intervention 是下一个核心对象。
- 该命令仍然只读，不会生成新的 Intervention、启动 Run、提交 Evidence 或修改 Project State。
- 它能引入最小 Intervention loader，为后续 `progress plan` 或 `progress run` 之前的对象读取打基础。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
progress intervention list
```

期望输出包含：

```text
Interventions:
- IV-0012 [implementation] Define next CLI intervention object slice (evidence_submitted)
```

输出可以是纯文本；本切片不要求 JSON 输出、筛选、排序、plan generation 或 run start。

## 3. 输入、输出和状态影响

输入：

- `.progress/interventions/*.yaml`

输出：

- stdout 的 Intervention 摘要。
- stderr 的错误说明，用于 interventions 目录缺失、YAML 不可解析或必要字段缺失。
- process exit code：
  - `0`：读取和输出成功。
  - `2`：输入目录缺失、YAML 解析失败或 Intervention 对象结构不满足最小读取要求。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不生成 Intervention。
- 不启动 Run。
- 不生成 Evidence 或 State Delta Proposal。
- 不更新 Project State maturity。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/interventions/__init__.py
src/progress_engine/interventions/intervention_list.py
tests/fixtures/minimal_progress_project/.progress/interventions/IV-1001-sample-intervention.yaml
tests/test_cli_intervention_list.py
```

必要时可以小幅调整 `src/progress_engine/README.md`，但不得借机实现 `progress plan`、`progress run` 或 Evidence / Delta 命令。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- YAML 读取继续使用 PyYAML。
- 默认从当前工作目录解析 `.progress/`。
- 只读取 `.progress/interventions/*.yaml` 中的 Intervention 对象。
- 每个 Intervention 至少读取 `id`、`name`、`primary_dimension`、`target_state_id`、`status`。
- 默认输出 status 不为 `completed` 的 Intervention；如果没有，则输出 `- none`。
- 读取失败时错误信息不能伪装为 Intervention 列表。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-004-01 | `progress intervention list` 能读取 `.progress/interventions/*.yaml` 并输出未完成 Intervention 摘要。 |
| AC-CLI-004-02 | 命令默认不输出 `completed` Intervention。 |
| AC-CLI-004-03 | interventions 目录缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-004-04 | Intervention YAML 解析失败或必要字段缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-004-05 | pytest 覆盖成功路径、缺目录路径、malformed YAML 路径和缺字段路径。 |
| AC-CLI-004-06 | `python3 scripts/check_repo.py` 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress intervention list` 或等效模块入口的示例输出。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明 `.progress/` 未被命令修改。

## 8. Out of Scope

本切片明确不做：

- `progress plan`
- `progress intervention create`
- `progress run start`
- Run lifecycle 管理
- Evidence 录入
- Verification 或 State Delta Proposal 生成
- State Delta apply
- 自动选择或执行 Intervention
- JSON 输出、筛选、排序、分页和 TUI
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0013: Implement read-only intervention list CLI slice
```

`IV-0013` 的目标不是“实现 planning”，而是只把 `progress intervention list` 变成可测试、可运行、只读的 Intervention 对象读取路径。
