# Verify List CLI Slice

本文定义 `IV-0018: Define next verification CLI slice` 的实现切片。它延续已接受的只读 CLI 路径：

```bash
progress state show
progress gaps list
progress target list
progress intervention list
progress run list
progress evidence list
```

下一条路径只读进入 Verification 审查队列，不运行验证器、不生成 State Delta Proposal、不修改 Project State。

## 1. 切片结论

第七条 Python CLI 用户路径选择：

```bash
progress verify list
```

该命令读取 `.progress/evidence/*.yaml` 中已有 Evidence 的 reviewer result 和 acceptance mapping 摘要，并输出 Verification review 队列。

选择它的原因：

- Evidence Verifier 协议要求 verifier 检查 acceptance mapping、scope、silent deferral 和 state delta claim；在实现写操作前，应先能审查已有 Evidence 的验证状态。
- `progress evidence list` 已证明 Evidence 对象目录读取路径成立，下一步应进入 Verification 审查视图，而不是直接实现 `progress verify --run` 写操作。
- 该命令仍然只读，不会判定新结果、生成 verification artifact、提出 State Delta 或修改 Project State。
- 它能为后续 `progress verify --run RUN-001` 打基础，但本切片不进入 verification 生成或 delta apply。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
progress verify list
```

期望输出包含：

```text
Verification reviews:
- EV-0017 RUN-20260517-IV-0017 / IV-0017 (pass_requires_human_gate; acceptance: 6 pass, 0 fail, 0 not_tested)
```

输出可以是纯文本；本切片不要求 JSON 输出、筛选、排序、`progress verify --run`、verification artifact 生成或 delta proposal。

## 3. 输入、输出和状态影响

输入：

- `.progress/evidence/*.yaml`

输出：

- stdout 的 Verification review 摘要。
- stderr 的错误说明，用于 evidence 目录缺失、YAML 不可解析、缺少 `evidence` 根对象、必要字段缺失或 acceptance mapping 结构不满足最小读取要求。
- process exit code：
  - `0`：读取和输出成功。
  - `2`：输入目录缺失、YAML 解析失败或 Evidence / acceptance mapping 结构不满足最小读取要求。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不运行 Verification。
- 不生成 verification artifact。
- 不生成 State Delta Proposal。
- 不更新 Project State maturity。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/verification/__init__.py
src/progress_engine/verification/verify_list.py
tests/fixtures/minimal_progress_project/.progress/evidence/EV-1001-sample-evidence.yaml
tests/test_cli_verify_list.py
```

必要时可以小幅调整 `src/progress_engine/README.md`，但不得借机实现 `progress verify --run`、State Delta Proposal 生成或 Delta 命令。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- YAML 读取继续经由现有 Evidence loader，不新增第二套 Evidence YAML 解析。
- 默认从当前工作目录解析 `.progress/`。
- 只读取 `.progress/evidence/*.yaml` 中的 Evidence 对象。
- 每个 Evidence 至少读取 `id`、`run_id`、`intervention_id`、`reviewer.result` 和 `claims[].acceptance_mapping[].status`。
- 如果目录存在但没有 Evidence YAML，则输出 `- none`。
- 读取失败时错误信息不能伪装为 Verification review 列表。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-007-01 | `progress verify list` 能读取 `.progress/evidence/*.yaml` 并输出 Verification review 摘要。 |
| AC-CLI-007-02 | 命令能复用 Evidence loader，并读取 `reviewer.result` 和 acceptance mapping status 计数。 |
| AC-CLI-007-03 | evidence 目录缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-007-04 | Evidence YAML 解析失败、缺少根 mapping、必要字段缺失或 acceptance mapping status 缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-007-05 | pytest 覆盖成功路径、空目录路径、缺目录路径、malformed YAML 路径、缺字段路径和缺 acceptance status 路径。 |
| AC-CLI-007-06 | `python3 scripts/check_repo.py` 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress verify list` 或等效模块入口的示例输出。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明 `.progress/` 未被命令修改。

## 8. Out of Scope

本切片明确不做：

- `progress verify --run`
- verification artifact 生成
- State Delta Proposal 生成
- State Delta apply / reject / rollback
- Evidence 录入或编辑
- 自动选择或执行 Intervention
- JSON 输出、筛选、排序、分页和 TUI
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0019: Implement read-only verify list CLI slice
```

`IV-0019` 的目标不是“实现 verifier”，而是只把 `progress verify list` 变成可测试、可运行、只读的 Verification review 路径。
