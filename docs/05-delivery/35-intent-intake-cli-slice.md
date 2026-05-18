# Intent Intake CLI Slice

本文定义 `IV-0030: Define intent intake CLI slice` 的实现切片。它延续 `progress init --project PROJECT_ID` 的受控写操作策略：只做一个可验证的最小写入，不执行自动评估或目标推荐。

## 1. 切片结论

下一条 bootstrap CLI 用户路径选择：

```bash
progress intake --from FILE
```

该命令在已初始化的 `.progress/` 中：

- 读取用户提供的 intent Markdown 文件。
- 写入 `.progress/artifacts/intent.md`。
- 更新 `.progress/state/project_state.yaml` 的 `intent` 维度为 `seed`。

选择它的原因：

- `progress init` 只能创建空账本；下一步应捕获用户初始意图，而不是直接自动评估。
- intent intake 是 bootstrap pipeline 的最小后续写操作。
- 该命令可以确定性执行，不需要模型 API。
- 它不生成 Gap、Target、Intervention 或 State Delta，避免绕过后续验证边界。

## 2. 用户路径

目标用户在已运行过 `progress init --project sample-project` 的仓库根目录运行：

```bash
progress intake --from intent.md
```

期望输出包含：

```text
Captured intent: .progress/artifacts/intent.md
Updated Project State intent maturity: seed
Next:
- progress state show
```

如果 `.progress/state/project_state.yaml` 不存在，命令返回 exit code `2` 并输出清晰错误。

## 3. 输入、输出和状态影响

输入：

- CLI 参数 `--from FILE`
- `.progress/state/project_state.yaml`

输出：

- `.progress/artifacts/intent.md`
- 更新后的 `.progress/state/project_state.yaml`

process exit code：

- `0`：intent 捕获成功。
- `2`：Project State 缺失、输入文件缺失、输入文件为空、YAML 解析失败或写入失败。

状态影响：

- 写入或覆盖 `.progress/artifacts/intent.md`。
- 将 `state_dimensions.intent.maturity` 设置为 `seed`。
- 将 `state_dimensions.intent.summary` 设置为指向初始 intent artifact 的确定性摘要。
- 将 `.progress/artifacts/intent.md` 加入 `state_dimensions.intent.evidence`。
- 不生成 Gap / Target / Intervention / Evidence / State Delta Proposal。
- 不运行 assess、target suggestion、delta apply 或模型调用。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/intake/__init__.py
src/progress_engine/intake/intent_intake.py
tests/test_cli_intake.py
src/progress_engine/README.md
```

必要时可以小幅调整 `src/progress_engine/init/init_project.py`，让 init 创建 `.progress/artifacts/` 目录；不得借机实现 assess、target suggest、delta apply 或完整 bootstrap pipeline。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- YAML 读取 / 写入使用 PyYAML。
- 默认从当前工作目录解析 `.progress/`。
- `--from` 必填，必须指向存在的非空文件。
- `.progress/state/project_state.yaml` 必须已经存在。
- `.progress/artifacts/` 不存在时可以创建。
- 写入后，`progress state show` 必须能读取更新后的 Project State。
- 多次运行可以覆盖 `.progress/artifacts/intent.md`，但不能删除其他 `.progress` 对象。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-012-01 | `progress intake --from intent.md` 在已初始化目录写入 `.progress/artifacts/intent.md`。 |
| AC-CLI-012-02 | 命令将 Project State 的 `intent` maturity 更新为 `seed` 并追加 intent artifact evidence。 |
| AC-CLI-012-03 | 写入后 `progress state show` 仍可读取 Project State。 |
| AC-CLI-012-04 | Project State 缺失、输入文件缺失或输入文件为空时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-012-05 | pytest 覆盖成功路径、缺 Project State、缺输入文件和空输入文件路径。 |
| AC-CLI-012-06 | `python3 scripts/check_repo.py` 和全量 pytest 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_cli_intake.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress init` 后运行 `progress intake --from intent.md` 和 `progress state show` 的示例输出。
- git diff 摘要，证明没有实现 assess、target suggestion、delta apply 或模型调用。

## 8. Out of Scope

本切片明确不做：

- `progress assess`
- 自动生成 Gap / Target / Intervention
- 自动更新 product、architecture、quality 等其他维度
- Evidence 对象生成
- State Delta Proposal 生成或 apply
- Fresh Context Capsule
- 模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0031: Implement intent intake CLI slice
```

`IV-0031` 的目标不是“实现自动项目理解”，而是只把用户提供的初始 intent 文件落入 `.progress/artifacts/intent.md`，并做最小 Project State 标记。
