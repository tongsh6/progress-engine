# Run Start CLI Slice

本文定义 `IV-0052: Define prompt-only run start CLI slice` 的实现切片。它承接 Context Capsule CLI 已可运行之后的缺口：用户可以生成 AI 执行上下文，但 prompt-only 执行会话仍不能作为 Run 被 repo-native 追踪。

## 1. 切片结论

下一条 run-lifecycle 用户路径选择：

```bash
progress run start --intervention IV-ID --mode prompt-only
```

该命令只创建一个 Run 对象，并确保该 Run 关联对应 Context Capsule。它不调用模型 API，不执行 Intervention，不创建 Evidence，不创建 Verification，不创建 State Delta，不修改 Project State。

成功输出应包含 Run 和 capsule 路径，例如：

```text
Run started:
- run: RUN-20260521-IV-0053
- intervention: IV-0053
- target: TS-0053
- mode: prompt-only
- capsule: .progress/context_capsules/IV-0053-context-capsule.md

Next:
- Open the capsule in an AI tool or hand it to a human executor.
- Record evidence after execution.
```

选择它的原因：

- `progress capsule` 已经提供 Fresh Context，但没有 Run 对象会导致执行会话无法追踪。
- v0.1 需要 repo-native run lifecycle，但仍应保持 prompt-only / manual-run，不进入模型 API adapter。
- Run start 是受控写入切片：它只写 `.progress/runs/` 和必要的 capsule 文件，不更新 Project State。
- 该切片继续使用 Python 3.11+、stdlib-first argparse、YAML / Markdown repo-native 账本，不引入 Web UI、模型 API 或外部服务。

## 2. 用户路径

用户先查看当前状态和候选 Intervention：

```bash
progress assess
progress intervention list
```

随后启动 prompt-only Run：

```bash
progress run start --intervention IV-0053 --mode prompt-only
```

命令应：

1. 解析 Intervention。
2. 解析 Target State。
3. 确认或生成 Context Capsule。
4. 创建 Run YAML。
5. 输出下一步提示。

用户随后把 capsule 交给 ChatGPT、Codex、Claude Code 或人类执行者。执行结束后，后续仍必须通过 Evidence、Verification、State Delta Proposal 和 human gate 更新 Project State。

## 3. 输入、输出和状态影响

输入：

- `.progress/state/project_state.yaml`
- `.progress/state/state_history.jsonl`
- `.progress/interventions/{IV-ID}-*.yaml`
- `.progress/targets/{TS-ID}-*.yaml`
- 可选：`.progress/context_capsules/{IV-ID}-context-capsule.md`
- CLI 参数 `--intervention IV-ID`
- CLI 参数 `--mode prompt-only`

输出：

- `.progress/runs/{RUN-ID}-{IV-ID-slug}.yaml`
- `.progress/context_capsules/{IV-ID}-context-capsule.md`，如果不存在则生成。
- stdout 的 run start 摘要。
- stderr 的错误说明。

process exit code：

- `0`：Run 创建成功。
- `2`：`.progress/` 缺失、Project State 缺失或不可解析、Intervention id 非法、Intervention 文件缺失或重复、Target 文件缺失或重复、mode 不支持、已有 active Run 指向同一 Intervention、Run 输出路径冲突、capsule 生成失败或 YAML 不可解析。

状态影响：

- 写入一个新的 Run YAML。
- 如 capsule 不存在，可写入一个 Context Capsule Markdown。
- 不修改 `.progress/state/project_state.yaml`。
- 不追加 `.progress/state/state_history.jsonl`。
- 不创建或修改 Gap、Target、Intervention、Evidence、Verification、State Delta 或 Change Event。
- 不调用模型 API、Web UI、外部 agent 或 shell adapter。

## 4. Run 对象要求

生成的 Run YAML 必须至少包含：

```yaml
id: RUN-YYYYMMDD-IV-ID
intervention_id: IV-ID
target_state_id: TS-ID
started_at: "ISO-8601 timestamp"
mode: prompt-only
primary_dimension: implementation
status: active
context_capsule: ".progress/context_capsules/IV-ID-context-capsule.md"
execution_session:
  fresh_context: true
  transcript_carried_forward: false
  mode: prompt-only
outputs:
  expected_evidence: []
```

最小规则：

- `run_id` 必须以 `RUN-YYYYMMDD-IV-ID` 为基础，必要时可追加后缀避免冲突。
- `target_state_id` 来自 Intervention。
- `primary_dimension` 来自 Intervention。
- `status` 初始为 `active`。
- `context_capsule` 指向对应 capsule 文件。
- `execution_session.fresh_context` 必须为 `true`。
- `execution_session.transcript_carried_forward` 必须为 `false`。

## 5. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/runs/__init__.py
src/progress_engine/runs/run_start.py
src/progress_engine/capsule/context_capsule.py
tests/test_cli_run_start.py
tests/fixtures/minimal_progress_project/.progress/context_capsules/.gitkeep
```

必要时可以小幅调整：

```text
README.md
src/progress_engine/README.md
tests/test_cli_run_list.py
```

不得借机实现：

- `progress run close`
- Evidence add / generation
- Verification generation
- State Delta generation
- model API adapter
- shell adapter
- target suggestion
- Web UI
- SaaS
- 多用户协作

## 6. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- 默认从当前工作目录解析 `.progress/`。
- 只支持 `--mode prompt-only`。
- `intervention_id` 必须以 `IV-` 开头。
- Intervention 文件必须使用 `{IV-ID}-*.yaml` canonical 解析规则。
- Target 文件必须使用 `{TS-ID}-*.yaml` canonical 解析规则。
- 如果同一 Intervention 已有 `active` 或 `planned` Run，命令必须拒绝重复 start。
- 如果 capsule 不存在，可以复用 `progress capsule` 的 renderer 生成。
- 如果 capsule 已存在，命令应复用它，不覆盖。
- 任一前置检查失败时，不得写入部分 Run 文件。

## 7. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-019-01 | `progress run start --intervention IV-ID --mode prompt-only` 能解析 canonical Intervention 和 Target State。 |
| AC-CLI-019-02 | 命令创建 `.progress/runs/{RUN-ID}-*.yaml`，Run status 为 `active`。 |
| AC-CLI-019-03 | 命令生成或复用 `.progress/context_capsules/{IV-ID}-context-capsule.md`。 |
| AC-CLI-019-04 | 命令拒绝 unsupported mode 和同一 Intervention 的重复 active/planned Run。 |
| AC-CLI-019-05 | 命令不修改 Project State、state history、Evidence、State Delta、Gap、Target、Intervention 或 Event。 |
| AC-CLI-019-06 | pytest 覆盖成功路径、缺 intervention、缺 target、unsupported mode、重复 Run 和 state/history 未变。 |
| AC-CLI-019-07 | `python3 scripts/check_repo.py` 和全量 pytest 仍通过。 |

## 8. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_cli_run_start.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress run start` 在 fixture 项目或当前项目中的示例输出。
- 生成的 Run YAML 关键字段摘要。
- 关联 capsule 的路径和关键片段摘要。
- git diff 摘要，证明没有引入模型 API、Web UI、外部 agent、Evidence generation、Verification generation 或 State Delta generation。
- 对 Project State 和 state history 未变的断言结果。

## 9. Out of Scope

本切片明确不做：

- 实现 `progress run start`
- 自动调用 OpenAI、Claude、Codex 或其他模型 API
- 自动执行 Intervention
- 自动关闭 Run
- 自动创建 Evidence、Verification、State Delta、Gap、Target、Intervention 或 Event
- 修改 Project State 或 state history
- Web UI、SaaS、多用户协作或远程同步

## 10. 下一步 Intervention

本切片被 verifier gate 接受后，下一步应创建并执行：

```text
IV-0053: Implement prompt-only run start CLI slice
```

`IV-0053` 的目标不是“自动运行 AI”，而是只把 prompt-only execution session 变成一个可追踪、可测试、可回滚边界清晰的 repo-native Run 对象。
