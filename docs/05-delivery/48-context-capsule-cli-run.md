# Context Capsule CLI Run

本文记录 `IV-0051: Implement Context Capsule CLI slice` 的执行结果。该 run 按 `docs/05-delivery/47-context-capsule-cli-slice.md` 定义，实现最小 prompt-only Context Capsule 生成命令。

## 1. Run 结论

`progress capsule --intervention IV-ID` 已实现并验证通过。

本轮新增能力：

```bash
progress capsule --intervention IV-ID
```

该命令会读取：

- `.progress/state/project_state.yaml`
- `.progress/state/state_history.jsonl`
- `.progress/interventions/{IV-ID}-*.yaml`
- `.progress/targets/{TS-ID}-*.yaml`

并生成：

```text
.progress/context_capsules/{IV-ID}-context-capsule.md
```

本轮没有调用模型 API，没有执行 Intervention，没有创建 Evidence / Verification / State Delta，没有修改 Project State 或 state history。Project State 仍只通过 human-gated State Delta apply 更新。

## 2. 实现摘要

新增模块：

```text
src/progress_engine/capsule/__init__.py
src/progress_engine/capsule/context_capsule.py
```

修改 CLI：

```text
src/progress_engine/cli.py
```

新增测试：

```text
tests/test_cli_capsule.py
tests/fixtures/minimal_progress_project/.progress/context_capsules/.gitkeep
```

更新文档命令清单：

```text
README.md
src/progress_engine/README.md
```

## 3. 命令示例

在当前仓库执行：

```bash
PYTHONPATH=src python3 -m progress_engine capsule --intervention IV-0051
```

输出：

```text
Context capsule generated:
- intervention: IV-0051
- target: TS-0051
- capsule: .progress/context_capsules/IV-0051-context-capsule.md

Next:
- Open the capsule in an AI tool or hand it to a human executor.
- Record evidence after execution.
```

生成的 capsule 包含：

```text
# Context Capsule: IV-0051
## Project Snapshot
## Target State
## Intervention
## In Scope
## Out of Scope
## Inputs
## Outputs
## Acceptance Criteria
## Evidence Required
## Rules
## Failure Handling
```

关键规则包括：

- 不继承旧聊天。
- 不扩大 scope。
- 不自证完成。
- 不静默延期。
- 不直接修改 Project State 或 state history。

## 4. 测试结果

Focused pytest：

```bash
python3 -m pytest tests/test_cli_capsule.py
```

结果：

```text
7 passed in 0.08s
```

全量 pytest：

```bash
python3 -m pytest
```

结果：

```text
129 passed in 0.77s
```

仓库检查：

```bash
python3 scripts/check_repo.py
```

结果：

```text
[OK] required paths exist
[OK] YAML parse passed
[OK] JSONL parse passed
[OK] local Markdown links passed
[OK] .progress object checks passed
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

## 5. Acceptance Mapping

| Criterion | Result | Evidence |
|---|---|---|
| `progress capsule --intervention IV-ID` 能解析 canonical Intervention 和 Target。 | pass | `tests/test_cli_capsule.py` |
| 命令生成 `.progress/context_capsules/{IV-ID}-context-capsule.md`。 | pass | `.progress/context_capsules/IV-0051-context-capsule.md` |
| Capsule 包含 Fresh Context 必需章节和 evidence_required。 | pass | generated capsule content |
| 命令不修改 Project State、state history、Evidence、State Delta、Gap、Target、Intervention 或 Event。 | pass | focused pytest state/history unchanged assertions |
| focused pytest、全量 pytest 和仓库检查通过。 | pass | command results above |
| 本轮不调用模型 API、Web UI 或外部 agent。 | pass | scope check and git diff |

## 6. Scope Check

本轮只实现 prompt-only Markdown capsule 生成。没有实现：

- `progress run start`
- shell adapter
- model API adapter
- OpenAI / Claude / Codex API 调用
- automatic Evidence / Verification / State Delta generation
- target suggestion
- Web UI
- SaaS
- 多用户协作

## 7. Remaining Gap

Context Capsule CLI 已经可运行。下一条自然缺口是 prompt-only 执行仍缺少 Run lifecycle 写入入口：用户能生成胶囊，但还不能通过 `progress run start --intervention IV-ID --mode prompt-only` 创建可追踪 Run 并关联 capsule。

下一轮应先定义 `progress run start` 的最小切片，而不是直接进入模型 API adapter。
