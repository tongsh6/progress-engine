# Evidence List CLI Slice

本文定义 `IV-0016: Define next evidence object CLI slice` 的实现切片。它延续已接受的只读 CLI 路径：

```bash
progress state show
progress gaps list
progress target list
progress intervention list
progress run list
```

下一条路径只读进入 Evidence 对象，不做 evidence add、verification、State Delta Proposal 生成或状态写入。

## 1. 切片结论

第六条 Python CLI 用户路径选择：

```bash
progress evidence list
```

该命令读取 `.progress/evidence/*.yaml` 中的 Evidence 对象，并输出 Evidence 摘要。

选择它的原因：

- 状态闭环顺序已经覆盖 Project State、State Gap、Target State、Intervention 和 Run；Evidence 是 Run 之后的下一核心对象。
- `progress run list` 已证明 Run 对象目录读取路径成立，下一步应验证 Evidence 对象读取路径。
- 该命令仍然只读，不会录入 Evidence、执行 Verification、提出 State Delta 或修改 Project State。
- 它能为后续 `progress verify` 前的 Evidence 可审查性打基础，但本切片不进入验证或写操作。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
progress evidence list
```

期望输出包含：

```text
Evidence:
- EV-0016 [artifact_review] RUN-20260517-IV-0016 / IV-0016 (pass_requires_human_gate)
```

输出可以是纯文本；本切片不要求 JSON 输出、筛选、排序、evidence add、verify 或 delta proposal。

## 3. 输入、输出和状态影响

输入：

- `.progress/evidence/*.yaml`

输出：

- stdout 的 Evidence 摘要。
- stderr 的错误说明，用于 evidence 目录缺失、YAML 不可解析、缺少 `evidence` 根对象或必要字段缺失。
- process exit code：
  - `0`：读取和输出成功。
  - `2`：输入目录缺失、YAML 解析失败或 Evidence 对象结构不满足最小读取要求。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不录入 Evidence。
- 不运行 Verification。
- 不生成 State Delta Proposal。
- 不更新 Project State maturity。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/evidence/__init__.py
src/progress_engine/evidence/evidence_list.py
tests/fixtures/minimal_progress_project/.progress/evidence/EV-1001-sample-evidence.yaml
tests/test_cli_evidence_list.py
```

必要时可以小幅调整 `src/progress_engine/README.md`，但不得借机实现 `progress evidence add`、`progress verify` 或 Delta 命令。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- YAML 读取继续使用 PyYAML。
- 默认从当前工作目录解析 `.progress/`。
- 只读取 `.progress/evidence/*.yaml` 中的 Evidence 对象。
- 每个 Evidence 文件必须包含 `evidence` 根 mapping。
- 每个 Evidence 至少读取 `id`、`run_id`、`intervention_id`、`evidence_type` 和 `reviewer.result`。
- 如果目录存在但没有 Evidence YAML，则输出 `- none`。
- 读取失败时错误信息不能伪装为 Evidence 列表。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-006-01 | `progress evidence list` 能读取 `.progress/evidence/*.yaml` 并输出 Evidence 摘要。 |
| AC-CLI-006-02 | 命令能读取 `evidence` 根 mapping 下的 Evidence 字段。 |
| AC-CLI-006-03 | evidence 目录缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-006-04 | Evidence YAML 解析失败、缺少根 mapping 或必要字段缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-006-05 | pytest 覆盖成功路径、空目录路径、缺目录路径、malformed YAML 路径和缺字段路径。 |
| AC-CLI-006-06 | `python3 scripts/check_repo.py` 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress evidence list` 或等效模块入口的示例输出。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明 `.progress/` 未被命令修改。

## 8. Out of Scope

本切片明确不做：

- `progress evidence add`
- `progress evidence show`
- `progress evidence list --run`
- Evidence 录入或编辑
- Verification 或 State Delta Proposal 生成
- State Delta apply
- 自动选择或执行 Intervention
- JSON 输出、筛选、排序、分页和 TUI
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0017: Implement read-only evidence list CLI slice
```

`IV-0017` 的目标不是“实现 evidence management”，而是只把 `progress evidence list` 变成可测试、可运行、只读的 Evidence 对象读取路径。
