# Context Capsule CLI Slice

本文定义 `IV-0050: Define Context Capsule CLI slice` 的实现切片。它承接 release readiness 之后的实现缺口：ProgressEngine 已有 Fresh Context 协议和 Context Capsule 模板，但用户仍需要手动整理 AI 执行上下文，容易遗漏目标状态、Intervention 边界、证据要求和失败处理规则。

## 1. 切片结论

下一条 capsule-focused 用户路径选择：

```bash
progress capsule --intervention IV-ID
```

该命令只生成 prompt-only Markdown 胶囊，不执行 Intervention，不调用模型 API，不创建 Evidence，不创建 State Delta，不修改 Project State。

成功输出应包含生成路径，例如：

```text
Context capsule generated:
- intervention: IV-0051
- target: TS-0051
- capsule: .progress/context_capsules/IV-0051-context-capsule.md

Next:
- Open the capsule in an AI tool or hand it to a human executor.
- Record evidence after execution.
```

选择它的原因：

- v0.1 已明确采用 prompt-only / manual-run 优先；自动模型 adapter 不是下一步。
- Fresh Context 协议已经存在，但没有 CLI 入口会让用户继续手工拼上下文。
- `progress capsule` 是 AI 协作入口的最小可执行切片：它提升上下文质量，但不扩大到 agent 编排。
- 该切片继续使用 Python 3.11+、stdlib-first argparse、YAML / Markdown repo-native 账本，不引入 Web UI、模型 API 或外部服务。

## 2. 用户路径

用户先查看当前状态和候选 Intervention：

```bash
progress assess
progress intervention list
```

随后生成胶囊：

```bash
progress capsule --intervention IV-0051
```

命令读取当前仓库 `.progress/` 中的状态对象，生成：

```text
.progress/context_capsules/IV-0051-context-capsule.md
```

用户复制该 Markdown 给 ChatGPT、Codex、Claude Code 或其他 AI 工具，也可以交给人类执行者。执行结束后，仍必须通过 Evidence、Verification、State Delta Proposal 和 human gate 更新 Project State。

## 3. 输入、输出和状态影响

输入：

- `.progress/state/project_state.yaml`
- `.progress/state/state_history.jsonl`
- `.progress/interventions/{IV-ID}-*.yaml`
- Intervention 的 `target_state_id`
- `.progress/targets/{TS-ID}-*.yaml`
- Intervention / Target 中列出的 in_scope、out_of_scope、acceptance_criteria、evidence_required、related_gaps
- 可选：当前 Project State 的 `open_state_gaps` 和 `aim_of_next_state`

输出：

- `.progress/context_capsules/{IV-ID}-context-capsule.md`
- stdout 的生成摘要。
- stderr 的错误说明。

process exit code：

- `0`：capsule 生成成功。
- `2`：`.progress/` 缺失、Project State 缺失或不可解析、Intervention id 非法、Intervention 文件缺失或重复、Target 文件缺失或重复、YAML 不可解析、必填字段缺失、输出路径已存在且未允许覆盖。

状态影响：

- 只写入 `.progress/context_capsules/{IV-ID}-context-capsule.md`。
- 不修改 `.progress/state/project_state.yaml`。
- 不追加 `.progress/state/state_history.jsonl`。
- 不创建或修改 Gap、Target、Intervention、Run、Evidence、Verification、State Delta 或 Change Event。
- 不调用模型 API、Web UI、外部 agent 或 shell adapter。

## 4. Capsule 内容要求

生成的 Markdown 必须至少包含：

```text
# Context Capsule: IV-ID

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

最小内容规则：

- Project Snapshot 包含 project id、phase、state version 或 latest history、当前 maturity 摘要。
- Target State 包含 id、dimension、from、to、desired_state 和 acceptance criteria。
- Intervention 包含 id、name、goal、status、primary_dimension 和 target_state_id。
- Inputs 列出被读取的 Project State、Target、Intervention 和相关 evidence refs。
- Rules 必须包含 Fresh Context 规则：不继承旧聊天、不扩大 scope、不自证完成、不静默延期。
- Failure Handling 必须说明如果发现 scope 超出、上下文不足或验收失败，应输出 remaining gaps，而不是自行扩大任务。

## 5. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/capsule/__init__.py
src/progress_engine/capsule/context_capsule.py
tests/test_cli_capsule.py
tests/fixtures/minimal_progress_project/.progress/context_capsules/.gitkeep
```

必要时可以小幅调整：

```text
README.md
src/progress_engine/README.md
```

不得借机实现：

- `progress run start`
- model API adapter
- shell adapter
- automatic Evidence / Verification / State Delta generation
- target suggestion
- Web UI
- SaaS
- 多用户协作

## 6. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- 默认从当前工作目录解析 `.progress/`。
- `intervention_id` 必须以 `IV-` 开头。
- Intervention 文件必须使用 `{IV-ID}-*.yaml` canonical 解析规则。
- Target 文件必须使用 `{TS-ID}-*.yaml` canonical 解析规则。
- 命令默认拒绝覆盖已有 capsule 文件。
- 如果引入 `--force`，只能覆盖同一 `IV-ID` 的 capsule 文件；不得删除目录或其他 capsule。
- Capsule 输出必须是 Markdown。
- 不读取完整聊天历史、未落账本地临时笔记或未引用文件。
- 不调用模型 API、Web UI 或外部 agent。
- 任一前置检查失败时，不得写入部分 capsule。

## 7. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-018-01 | `progress capsule --intervention IV-ID` 能解析 canonical Intervention 和 Target State。 |
| AC-CLI-018-02 | 命令生成 `.progress/context_capsules/{IV-ID}-context-capsule.md`。 |
| AC-CLI-018-03 | Capsule 包含 Project Snapshot、Target State、Intervention、scope、inputs、outputs、acceptance criteria、evidence required、rules 和 failure handling。 |
| AC-CLI-018-04 | 命令不修改 Project State、state history、Evidence、State Delta、Gap、Target、Intervention 或 Event。 |
| AC-CLI-018-05 | pytest 覆盖成功路径、缺 intervention、缺 target、重复输出拒绝、非法 id 和 Project State 缺失。 |
| AC-CLI-018-06 | `python3 scripts/check_repo.py` 和全量 pytest 仍通过。 |

## 8. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_cli_capsule.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- 生成 capsule 的示例输出。
- 生成的 capsule 关键片段摘要。
- git diff 摘要，证明没有引入模型 API、Web UI、外部 agent、run lifecycle、Evidence generation 或 State Delta generation。
- 对 Project State 和 state history 未变的断言结果。

## 9. Out of Scope

本切片明确不做：

- 实现 `progress capsule`
- 自动调用 OpenAI、Claude、Codex 或其他模型 API
- 自动执行 Intervention
- 自动创建 Run、Evidence、Verification、State Delta 或 Event
- 自动生成 Target 或 Intervention
- 修改 Project State 或 state history
- Web UI、SaaS、多用户协作或远程同步
- 通用 prompt 编排系统

## 10. 下一步 Intervention

本切片被 verifier gate 接受后，下一步应创建并执行：

```text
IV-0051: Implement Context Capsule CLI slice
```

`IV-0051` 的目标不是“配置 AI”或“自动执行 AI”，而是只把 Fresh Context Capsule 变成一个可运行、可测试、可追溯的 repo-native Markdown 生成命令。
