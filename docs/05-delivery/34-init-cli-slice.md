# Init CLI Slice

本文定义 `IV-0028: Define next state-changing CLI slice` 的实现切片。它是第一条会写入仓库的 Python CLI 路径，因此范围必须比只读路径更窄，并且默认拒绝覆盖已有 `.progress/`。

## 1. 切片结论

第一条 state-changing CLI 用户路径选择：

```bash
progress init --project PROJECT_ID
```

该命令只在当前目录不存在 `.progress/` 时，创建最小 ProgressEngine 状态账本骨架。

选择它的原因：

- `progress init` 是系统设计中最早的写操作，比 `delta apply`、`state refresh` 和 `event add` 风险更低。
- 初始化空账本不绕过 Evidence / Verification / Delta gate；它只建立项目开始使用 ProgressEngine 所需的最小状态容器。
- 已有只读 CLI 可以立即读取新生成的 `.progress/state/project_state.yaml`，形成可验证闭环。
- 拒绝覆盖已有 `.progress/` 可以避免误伤真实状态账本。

## 2. 用户路径

目标用户在一个尚未初始化的仓库根目录运行：

```bash
progress init --project sample-project
```

期望输出包含：

```text
Initialized ProgressEngine project: sample-project
Created:
- .progress/README.md
- .progress/state/project_state.yaml
- .progress/state/state_history.jsonl
Next:
- progress state show
```

如果当前目录已经存在 `.progress/`，命令必须返回 exit code `2` 并输出清晰错误，不覆盖任何文件。

## 3. 输入、输出和状态影响

输入：

- CLI 参数 `--project PROJECT_ID`
- 当前工作目录

输出：

- `.progress/README.md`
- `.progress/state/project_state.yaml`
- `.progress/state/state_history.jsonl`
- 后续只读对象目录：
  - `.progress/gaps/`
  - `.progress/targets/`
  - `.progress/interventions/`
  - `.progress/runs/`
  - `.progress/evidence/`
  - `.progress/deltas/`
  - `.progress/events/`
  - `.progress/context_capsules/`
  - `.progress/ledger/`

process exit code：

- `0`：初始化成功。
- `2`：`.progress/` 已存在、项目 id 非法或写入失败。

状态影响：

- 只创建新的 `.progress/` 最小骨架。
- 不修改已有 `.progress/`。
- 不生成 Evidence。
- 不生成或 apply State Delta Proposal。
- 不运行 state refresh、assessment、target suggestion 或外部 agent。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/init/__init__.py
src/progress_engine/init/init_project.py
tests/test_cli_init.py
src/progress_engine/README.md
```

必要时可以小幅调整 `docs/05-delivery/34-init-cli-slice.md`，但不得借机实现 `delta apply`、`state refresh`、`intake`、模板渲染引擎或完整项目脚手架。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- YAML 写入可使用 PyYAML，输出格式必须能被现有 `progress state show` 读取。
- 默认从当前工作目录创建 `.progress/`。
- `--project` 必填，必须是非空字符串，只允许字母、数字、点、下划线和短横线。
- `.progress/` 已存在时必须拒绝执行。
- 初始化成功后，`progress state show` 在同一目录必须能读取 Project State。
- `state_history.jsonl` 初始为空文件。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-011-01 | `progress init --project sample-project` 在空目录创建最小 `.progress/` 骨架。 |
| AC-CLI-011-02 | 生成的 `.progress/state/project_state.yaml` 可被 `progress state show` 读取。 |
| AC-CLI-011-03 | `.progress/` 已存在时返回 exit code `2` 并且不覆盖既有文件。 |
| AC-CLI-011-04 | 缺少或非法 `--project` 时返回非零退出码并输出清晰错误。 |
| AC-CLI-011-05 | pytest 覆盖成功路径、已有 `.progress/` 路径和非法 project id 路径。 |
| AC-CLI-011-06 | `python3 scripts/check_repo.py` 和全量 pytest 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_cli_init.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- 初始化后运行 `progress state show` 的示例输出。
- git diff 摘要，证明没有实现 delta apply、state refresh 或自动修复。

## 8. Out of Scope

本切片明确不做：

- `progress intake`
- `progress assess`
- `progress state refresh`
- `progress delta apply`、reject 或 rollback
- 自动生成 Gap / Target / Intervention
- 复制完整模板目录或复杂模板渲染
- 覆盖或迁移已有 `.progress/`
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0029: Implement init CLI slice
```

`IV-0029` 的目标不是“实现完整 bootstrap pipeline”，而是只把 `progress init --project PROJECT_ID` 变成可测试、可运行、拒绝覆盖的最小写入路径。
