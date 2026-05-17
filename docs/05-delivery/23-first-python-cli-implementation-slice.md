# First Python CLI Implementation Slice

本文定义 `IV-0006: Define first Python CLI implementation slice` 的实现切片。它只冻结下一步代码工作的边界，不实现代码，也不把完整 CLI 提前塞进 v0.1。

## 1. 切片结论

第一条 Python CLI 用户路径选择：

```bash
progress state show
```

该命令只读取当前仓库的 `.progress/state/project_state.yaml`，并输出项目状态摘要。

选择它的原因：

- 它是状态驱动闭环的入口，先证明 Project State 能被 CLI 稳定读取。
- 它不写入 `.progress/`，不会绕过 State Delta Proposal 或 human gate。
- 它能验证 Python package、argparse、YAML 读取、错误处理和 fixture test 的最小工程路径。
- 它不需要模型 API、外部 agent、数据库、Web UI 或复杂调度器。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
progress state show
```

期望输出包含：

```text
Project: progress-engine
Phase: repo_bootstrap
Dimensions:
- intent: accepted
- product: accepted
- design: drafted
- architecture: accepted
- implementation: not_started
- quality: reviewed
- delivery: weak
- knowledge: reviewed
Open gaps:
- SG-0001
- SG-0002
- SG-0003
- SG-0004
Next target:
- TS-0006
```

输出可以是纯文本；本切片不要求 JSON 输出、彩色终端、交互式选择或分页。

## 3. 输入、输出和状态影响

输入：

- `.progress/state/project_state.yaml`

输出：

- stdout 的项目状态摘要。
- stderr 的错误说明，用于缺文件、YAML 不可解析或必要字段缺失。
- process exit code：
  - `0`：读取和输出成功。
  - `2`：输入文件缺失、YAML 解析失败或 Project State 结构不满足最小读取要求。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不生成 Evidence。
- 不生成 State Delta Proposal。
- 不更新 Project State maturity。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下新代码边界：

```text
pyproject.toml
src/progress_engine/__init__.py
src/progress_engine/__main__.py
src/progress_engine/cli.py
src/progress_engine/state/__init__.py
src/progress_engine/state/project_state.py
tests/fixtures/minimal_progress_project/.progress/state/project_state.yaml
tests/test_cli_state_show.py
```

可以保留或更新 `src/progress_engine/README.md`，但不得借机实现其他命令。

## 5. 最小行为规则

- CLI 使用 Python 3.11+ 和 `argparse`。
- YAML 读取使用 PyYAML。
- 默认从当前工作目录解析 `.progress/state/project_state.yaml`。
- 允许测试中通过 helper 或参数传入 fixture 根目录，但用户路径不要求先设计完整 workspace 参数系统。
- 输出只依赖 Project State 中已经存在的字段：`project`、`state_dimensions`、`open_state_gaps`、`aim_of_next_state`。
- 读取失败时必须返回非零 exit code，且错误信息不能伪装为状态摘要。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-001-01 | `progress state show` 能读取 `.progress/state/project_state.yaml` 并打印 project id、phase、dimension maturity、open gaps 和 next target。 |
| AC-CLI-001-02 | 命令不修改 `.progress/` 中任何文件。 |
| AC-CLI-001-03 | 缺少 Project State 文件时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-001-04 | YAML 解析失败或必要字段缺失时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-001-05 | pytest 覆盖成功路径、缺文件路径和 malformed state 路径。 |
| AC-CLI-001-06 | `python3 scripts/check_repo.py` 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress state show` 或等效模块入口的示例输出。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明 `.progress/state/project_state.yaml` 未被命令修改。

## 8. Out of Scope

本切片明确不做：

- `progress init`
- `progress assess`
- `progress gaps`
- `progress target`
- `progress plan`
- `progress capsule`
- `progress evidence`
- `progress verify`
- `progress delta apply`
- State Delta 生成、应用或回滚
- Fresh Context Capsule 生成
- 完整 schema 校验
- Web UI / SaaS
- 模型 API 或外部 agent 调用
- 多项目 workspace 管理
- 复杂终端 UI、颜色主题、配置文件系统

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0007: Implement first Python CLI state show slice
```

`IV-0007` 的目标不是“实现 ProgressEngine CLI”，而是只把 `progress state show` 变成可测试、可运行、只读的最小 Python CLI。
