# Run Start CLI Run

本文记录 `IV-0053: Implement prompt-only run start CLI slice` 的执行结果。该 run 按 `docs/05-delivery/49-run-start-cli-slice.md` 定义，实现最小 prompt-only Run 创建命令。

## 1. Run 结论

`progress run start --intervention IV-ID --mode prompt-only` 已实现并验证通过。

本轮新增能力：

```bash
progress run start --intervention IV-ID --mode prompt-only
```

该命令会：

- 解析 canonical Intervention 和 Target State。
- 生成或复用对应 Context Capsule。
- 创建 active Run YAML。
- 拒绝 unsupported mode。
- 拒绝同一 Intervention 的重复 active / planned Run。

本轮没有调用模型 API，没有执行 Intervention，没有创建 Evidence / Verification / State Delta，没有修改 Project State 或 state history。Project State 仍只通过 human-gated State Delta apply 更新。

## 2. 实现摘要

新增模块：

```text
src/progress_engine/runs/run_start.py
```

修改：

```text
src/progress_engine/cli.py
src/progress_engine/capsule/context_capsule.py
README.md
src/progress_engine/README.md
```

新增测试：

```text
tests/test_cli_run_start.py
```

## 3. 命令示例

在当前仓库执行：

```bash
PYTHONPATH=src python3 -m progress_engine run start --intervention IV-0053 --mode prompt-only
```

输出：

```text
Run started:
- run: RUN-20260521-IV-0053
- intervention: IV-0053
- target: TS-0053
- mode: prompt-only
- capsule: .progress/context_capsules/IV-0053-context-capsule.md
- run file: .progress/runs/RUN-20260521-IV-0053.yaml

Next:
- Open the capsule in an AI tool or hand it to a human executor.
- Record evidence after execution.
```

生成的 Run YAML 关键字段：

```yaml
id: RUN-20260521-IV-0053
intervention_id: IV-0053
target_state_id: TS-0053
mode: prompt-only
primary_dimension: implementation
status: active
context_capsule: .progress/context_capsules/IV-0053-context-capsule.md
execution_session:
  fresh_context: true
  transcript_carried_forward: false
  mode: prompt-only
```

生成的 capsule 路径：

```text
.progress/context_capsules/IV-0053-context-capsule.md
```

## 4. 测试结果

Focused pytest：

```bash
python3 -m pytest tests/test_cli_run_start.py
```

结果：

```text
7 passed in 0.07s
```

全量 pytest：

```bash
python3 -m pytest
```

结果：

```text
136 passed in 0.76s
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
| `progress run start --intervention IV-ID --mode prompt-only` 能解析 canonical Intervention 和 Target。 | pass | `tests/test_cli_run_start.py` |
| 命令创建 active Run YAML 并关联 Context Capsule。 | pass | `.progress/runs/RUN-20260521-IV-0053.yaml` |
| 命令拒绝 unsupported mode 和重复 active/planned Run。 | pass | `tests/test_cli_run_start.py` |
| 命令不修改 Project State、state history、Evidence、State Delta、Gap、Target、Intervention 或 Event。 | pass | focused pytest state/history unchanged assertions |
| focused pytest、全量 pytest 和仓库检查通过。 | pass | command results above |
| 本轮不调用模型 API、Web UI 或外部 agent。 | pass | scope check and git diff |

## 6. Scope Check

本轮只实现 prompt-only Run 创建。没有实现：

- `progress run close`
- model API adapter
- shell adapter
- automatic Evidence generation
- Verification generation
- State Delta generation
- target suggestion
- Web UI
- SaaS
- 多用户协作

## 7. Remaining Gap

Run start CLI 已经可运行。下一条自然缺口是 Evidence 仍缺少受控写入入口：用户可以生成 capsule 并启动 Run，但执行后还不能通过 CLI 录入 Evidence。

下一轮应先定义 `progress evidence add --run RUN-ID --file evidence.yaml` 的最小切片，而不是直接进入 verifier 或模型 API adapter。
