# ProgressEngine 项目推进台账

本台账记录项目状态如何被推进。它不是任务列表，也不是完成清单；每条记录都必须说明目标状态、证据、State Delta 和 remaining gaps。

## 2026-05-20

### IV-0043: Implement state refresh CLI slice

- Target State：`TS-0043: state refresh CLI working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 选择理由：
  - `SG-0033` 是当前 Project State open gap，要求把已定义的 state refresh slice 变成可运行 CLI。
  - `progress delta apply` 和 `progress delta rollback` 已能改变 Project State；refresh 必须提供 apply / rollback 后的只读再观察入口。
  - 本轮实现只读取 Project State、latest state history、open gaps 和 next targets，不写入任何 `.progress/` 文件。
  - 失败路径覆盖 delta 格式错误、delta 不匹配、delta 缺失、history 缺失和 open gap 引用缺失。
- Evidence：`.progress/evidence/EV-0043-state-refresh-cli.yaml`
- State Delta：`.progress/deltas/SDP-0043-state-refresh-cli.yaml`
- 状态历史：`PS-0042`
- 主要产物：
  - `src/progress_engine/state/state_refresh.py`
  - `src/progress_engine/cli.py`
  - `tests/test_cli_state_refresh.py`
  - `README.md`
  - `src/progress_engine/README.md`
- 检查结果：

```text
python3 -m pytest tests/test_cli_state_refresh.py
8 passed in 0.06s

python3 -m pytest
112 passed in 0.56s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 278 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 246 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0034` 已创建：State Delta reject 尚未定义下一条切片。
  - 下一轮应处理 `TS-0044: next delta reject slice defined` / `IV-0044: Define delta reject CLI slice`。

### IV-0042: Define state refresh CLI slice

- Target State：`TS-0042: next state refresh slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 选择理由：
  - `SG-0032` 是当前 Project State open gap，要求先定义 state refresh-focused CLI slice。
  - `progress delta apply` 和 `progress delta rollback` 已能受控写入和回退 Project State，但 apply / rollback 后缺少专门的状态再观察入口。
  - 本轮把 refresh 明确限定为 read / derive：只读取 Project State、state history、open gaps 和 next targets，不写状态账本。
  - 直接实现 reject、automatic generation、模型 API 或 Web UI 会扩大 v0.1 范围。
- Evidence：`.progress/evidence/EV-0042-state-refresh-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0042-state-refresh-cli-slice.yaml`
- 状态历史：`PS-0041`
- 主要产物：
  - `docs/05-delivery/41-state-refresh-cli-slice.md`
  - `.progress/gaps/SG-0033-state-refresh-implementation-gap.yaml`
  - `.progress/targets/TS-0043-state-refresh-cli-working.yaml`
  - `.progress/interventions/IV-0043-implement-state-refresh-cli-slice.yaml`
- 明确边界：
  - `progress state refresh [--after-delta SDP-ID]` 是只读 reconciliation 命令。
  - 不修改 `.progress/state/project_state.yaml`，不追加 state history，不修改 State Delta Proposal。
  - 不生成 Gap、Target、Intervention、Evidence、Verification 或 State Delta Proposal。
- 检查结果：

```text
python3 -m pytest
104 passed in 0.51s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 272 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 240 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0033` 已创建：`progress state refresh` 已定义但尚未实现。
  - 下一轮应处理 `TS-0043: state refresh CLI working` / `IV-0043: Implement state refresh CLI slice`。

### IV-0041: Implement delta rollback CLI slice

- Target State：`TS-0041: delta rollback CLI working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 选择理由：
  - `SG-0031` 是当前 Project State open gap，且直接阻断 State Delta apply 后的受控可回滚路径。
  - `docs/05-delivery/40-state-delta-rollback-cli-slice.md` 已把实现边界限定为 `progress delta rollback SDP-ID --approved-by NAME`。
  - 本轮实现只处理最新 applied、reversible、rollback gate approved 的 proposal；不实现 reject、state refresh、verification generation 或通用 patch engine。
  - 失败路径在写入前返回，并用测试断言 Project State 和 state history 不发生部分修改。
- Evidence：`.progress/evidence/EV-0041-delta-rollback-cli.yaml`
- State Delta：`.progress/deltas/SDP-0041-delta-rollback-cli.yaml`
- 状态历史：`PS-0040`
- 主要产物：
  - `src/progress_engine/deltas/delta_rollback.py`
  - `src/progress_engine/cli.py`
  - `tests/test_cli_delta_rollback.py`
  - `tests/fixtures/minimal_progress_project/.progress/deltas/SDP-1003-rollback-ready-delta.yaml`
  - `tests/fixtures/minimal_progress_project/.progress/evidence/EV-1003-rollback-ready.yaml`
- 自审处理：
  - `progress delta rollback` 不把 `--approved-by` 当自动审批；proposal 必须已经有 `rollback.gate.decision: approved`。
  - rollback 只允许回退最新 state history version，避免回退旧 delta 污染当前 Project State。
  - Project State 恢复只允许 `state_dimensions`、`open_state_gaps` 和 `aim_of_next_state` 的 allow-list 字段。
  - `SG-0032` 已创建：state refresh 尚未定义下一条切片，reject 仍保持 out_of_scope。
- 检查结果：

```text
python3 -m pytest tests/test_cli_delta_rollback.py
9 passed in 0.15s

python3 -m pytest
104 passed in 0.51s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 266 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 234 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0032` 已创建：下一条 state refresh-focused CLI slice 尚未定义。
  - 下一轮应处理 `TS-0042: next state refresh slice defined` / `IV-0042: Define state refresh CLI slice`。

### IV-0040: Define delta rollback CLI slice

- Target State：`TS-0040: next delta rollback slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 选择理由：
  - 当前 Project State 唯一 open gap 是 `SG-0030`，它要求先定义 rollback-focused State Delta CLI slice。
  - `progress delta apply` 已能把 approved proposal 写入 Project State 和 state history，但 apply 后缺少受控回退路径。
  - 直接实现 reject、state refresh 或完整 delta management 会扩大 v0.1 范围；本轮只定义 `progress delta rollback` 的最小实现边界。
  - rollback 必须复用 apply metadata、state history 和 human gate，不能删除既有 history 或执行任意 YAML merge。
- Evidence：`.progress/evidence/EV-0040-delta-rollback-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0040-delta-rollback-cli-slice.yaml`
- 状态历史：`PS-0039`
- 主要产物：
  - `docs/05-delivery/40-state-delta-rollback-cli-slice.md`
  - `.progress/gaps/SG-0031-delta-rollback-implementation-gap.yaml`
  - `.progress/targets/TS-0041-delta-rollback-cli-working.yaml`
  - `.progress/interventions/IV-0041-implement-delta-rollback-cli-slice.yaml`
- 自审处理：
  - 本轮不改运行时代码，避免在未完成 rollback 行为定义前修改 CLI。
  - `progress delta rollback` 被限定为 human-gated allow-list restore；reject、state refresh、verification generation、模型 API 和 Web UI 均保持 out of scope。
  - rollback history 只能追加，不能删除或重写既有 state history。
- 检查结果：

```text
python3 -m pytest
95 passed in 0.41s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 258 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 228 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0031` 已创建：`progress delta rollback` 已定义但尚未实现。
  - 下一轮应处理 `TS-0041: delta rollback CLI working` / `IV-0041: Implement delta rollback CLI slice`。

### IV-0039: Implement delta apply CLI slice

- Target State：`TS-0039: delta apply CLI working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 选择理由：
  - `SG-0029` 是当前 Project State 唯一 open gap，且直接阻断 State Delta Proposal 从只读列表进入受控状态历史写入。
  - `docs/05-delivery/39-state-delta-apply-cli-slice.md` 已把实现边界限定为 `progress delta apply SDP-ID --approved-by NAME`。
  - 本轮实现只处理 human-gated apply：校验 gate、evidence refs、acceptance summary 和 allow-list `project_state_update`，不实现 reject、rollback、state refresh 或 verification generation。
  - 失败路径在写入前返回，并用测试断言 Project State 和 state history 不发生部分修改。
- Evidence：`.progress/evidence/EV-0039-delta-apply-cli.yaml`
- State Delta：`.progress/deltas/SDP-0039-delta-apply-cli.yaml`
- 状态历史：`PS-0038`
- 主要产物：
  - `src/progress_engine/deltas/delta_apply.py`
  - `src/progress_engine/cli.py`
  - `src/progress_engine/state/project_state.py`
  - `src/progress_engine/state/state_history.py`
  - `tests/test_cli_delta_apply.py`
  - `tests/fixtures/minimal_progress_project/.progress/deltas/SDP-1002-apply-ready-delta.yaml`
  - `tests/fixtures/minimal_progress_project/.progress/evidence/EV-1002-apply-ready.yaml`
- 自审处理：
  - `progress delta apply` 不把 `--approved-by` 当自动审批；proposal 必须已经有 `gate.decision: approved` 且 `requires_human_approval: true`。
  - Project State 更新只允许 `state_dimensions`、`open_state_gaps` 和 `aim_of_next_state` 的 allow-list 字段。
  - `SG-0030` 已创建：rollback / reject / state refresh 尚未定义下一条切片，其中 rollback 是质量体系发布阻断风险。
- 检查结果：

```text
python3 -m pytest tests/test_cli_delta_apply.py
7 passed

python3 -m pytest tests/test_cli_delta_apply.py tests/test_cli_delta_list.py tests/test_cli_state_history.py tests/test_cli_state_show.py
23 passed

python3 -m pytest
95 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 252 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 222 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0030` 已创建：下一条 rollback-focused State Delta CLI slice 尚未定义。
  - 下一轮应处理 `TS-0040: next delta rollback slice defined` / `IV-0040: Define delta rollback CLI slice`。

### IV-0038: Define next full state-loop write slice

- Target State：`TS-0038: next full state-loop write slice defined`
- 主维度：implementation
- 结果：已按 `verifier_required` policy apply，implementation maturity 保持 `drafted`
- 选择理由：
  - 当前 Project State 唯一 open gap 是 `SG-0028`，且它直接要求先定义下一条完整 State Delta 写闭环切片。
  - v0.1 试点只覆盖 bootstrap 和只读状态观察；继续推进必须进入 gate 后的状态写入，否则 v0.1 仍停留在 proposal/list 层。
  - 直接实现完整 `apply/reject/rollback/refresh` 会扩大 MVP 范围；本轮选择先定义最小 `progress delta apply` 写路径。
  - 该切片强制 human gate、allow-list Project State patch、state history 和 rollback 准备，不引入模型 API、Web UI、外部 agent 或通用 patch engine。
- Evidence：`.progress/evidence/EV-0038-next-full-state-loop-write-slice.yaml`
- State Delta：`.progress/deltas/SDP-0038-next-full-state-loop-write-slice.yaml`
- 状态历史：`PS-0037`
- 主要产物：
  - `docs/05-delivery/39-state-delta-apply-cli-slice.md`
  - `.progress/gaps/SG-0029-delta-apply-implementation-gap.yaml`
  - `.progress/targets/TS-0039-delta-apply-cli-working.yaml`
  - `.progress/interventions/IV-0039-implement-delta-apply-cli-slice.yaml`
- 自审处理：
  - 本轮不改运行时代码，避免在未定义 patch/gate 边界前写入 Project State。
  - `progress delta apply` 被限定为 human-gated allow-list 写操作；reject、rollback、state refresh 和 verification generation 均保持 out of scope。
  - implementation maturity 保持 `drafted`，因为本轮只完成实现切片定义。
- 检查结果：

```text
python3 -m pytest
88 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 244 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 216 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0029` 已创建：`progress delta apply` 已定义但尚未实现。
  - 下一轮应处理 `TS-0039: delta apply CLI working` / `IV-0039: Implement delta apply CLI slice`。

## 2026-05-19

### IV-0037: Run v0.1 pilot validation scenario

- Target State：`TS-0037: v0.1 pilot validation run accepted`
- 主维度：product
- 结果：已按 `verifier_required` policy apply，product maturity 保持 `accepted`
- 选择理由：
  - `SDP-0036` 明确推荐下一步执行 `IV-0037`。
  - 该试点直接验证 v0.1 的核心 bootstrap 路径：从 `examples/initial-project/intent.md` 到 repo-native `.progress` 状态账本，再到只读状态观察。
  - 本任务复用已实现 CLI，不引入模型 API、Web UI、外部 agent 或完整调度器，符合 v0.1 边界。
  - 一次性人工试点不足以支撑长期质量；本轮将它固化为 pytest 集成测试。
- Evidence：`.progress/evidence/EV-0037-v0.1-pilot-validation-run.yaml`
- State Delta：`.progress/deltas/SDP-0037-v0.1-pilot-validation-run.yaml`
- 状态历史：`PS-0036`
- 主要产物：
  - `docs/05-delivery/38-v0.1-pilot-validation-run.md`
  - `tests/test_pilot_validation.py`
- 自审处理：
  - `SG-0001` 仍为 open，但其 desired state 已被当前仓库事实满足。
  - 本轮通过 State Delta 关闭 `SG-0001`，而不是在 CLI 中隐藏该 gap。
  - delivery maturity 保持 `weak`，因为发布方案仍未形成。
- 检查结果：

```text
python3 -m pytest tests/test_pilot_validation.py
1 passed

python3 -m pytest
88 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 237 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 209 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0028` 已创建：下一条完整 State Delta 写闭环切片尚未定义。
  - 下一轮应处理 `TS-0038: next full state-loop write slice defined` / `IV-0038: Define next full state-loop write slice`，而不是直接把 product 升级到 validated。

### IV-0036: Select v0.1 pilot validation scenario

- Target State：`TS-0036: v0.1 pilot validation scenario selected`
- 主维度：product
- 结果：已按 `verifier_required` policy apply，product maturity 保持 `accepted`
- 选择理由：
  - `SG-0002` 明确要求选定真实或代表性试点，否则 product 不能进入 validated。
  - 选择 `examples/initial-project/intent.md` 能覆盖 v0.1 核心承诺：从模糊 intent 进入 repo-native Project State。
  - 本试点可本地重复执行，不依赖模型 API、Web UI 或外部服务。
  - 本轮只选定试点，不执行试点，也不声称 product validated。
- Evidence：`.progress/evidence/EV-0036-v0.1-pilot-validation-scenario.yaml`
- State Delta：`.progress/deltas/SDP-0036-v0.1-pilot-validation-scenario.yaml`
- 状态历史：`PS-0035`
- 主要产物：
  - `docs/05-delivery/37-v0.1-pilot-validation-scenario.md`
- 检查结果：

```text
python3 -m pytest
87 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 230 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 202 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0001` 仍是唯一 open gap，需要后续复核它是否已被仓库事实满足或需要新的 delivery target。
  - 试点尚未执行；后续可按 `SDP-0036` 推荐创建 `IV-0037: Run v0.1 pilot validation scenario`。

### IV-0035: Project State evidence gate

- Target State：`TS-0035: project state evidence gate working`
- 主维度：quality
- 结果：已按 `verifier_required` policy apply，quality maturity 保持 `reviewed`
- 选择理由：
  - `SG-0003` 仍是主要质量缺口，且直接影响状态账本可信度。
  - Project State 已能检查 open gap / next target 引用，但 dimension maturity 枚举和 evidence refs 仍可能漂移。
  - 该切片只读、可测试，收敛质量门禁，不扩张为完整 schema engine。
- Evidence：`.progress/evidence/EV-0035-project-state-evidence-gate.yaml`
- State Delta：`.progress/deltas/SDP-0035-project-state-evidence-gate.yaml`
- 状态历史：`PS-0034`
- 主要产物：
  - `scripts/check_repo.py`
  - `tests/test_check_repo.py`
- 检查结果：

```text
python3 -m pytest tests/test_check_repo.py
14 passed

python3 -m pytest
87 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 225 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 197 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0002` 是当前主要产品验证缺口。
  - `SG-0001` 仍是 delivery bootstrap 缺口。

### IV-0034: Fix reference resolution consistency

- Target State：`TS-0034: reference resolution consistent`
- 主维度：quality
- 结果：已按 `verifier_required` policy apply，quality maturity 保持 `reviewed`
- 选择理由：
  - 代码审查发现运行时 Gap loader 使用宽松前缀匹配，可能把相似 ID 文件当成 Project State 引用对象。
  - Target loader 允许 `{id}.yaml`，与 Project State reference check 的 `{id}-*.yaml` canonical 规则不一致。
  - 该问题会削弱 State Assessment Gate 和 Project State reference integrity，影响 `progress gaps list`、`progress target list` 以及复用二者的 `progress assess`。
  - 修复根因是统一引用解析规则，而不是为单个命令补特殊判断。
- Evidence：`.progress/evidence/EV-0034-reference-resolution-consistency.yaml`
- State Delta：`.progress/deltas/SDP-0034-reference-resolution-consistency.yaml`
- 状态历史：`PS-0031`
- 主要产物：
  - `src/progress_engine/state/references.py`
  - `src/progress_engine/gaps/gap_list.py`
  - `src/progress_engine/targets/target_list.py`
  - `tests/test_cli_gaps_list.py`
  - `tests/test_cli_target_list.py`
- 检查结果：

```text
python3 -m pytest tests/test_cli_gaps_list.py tests/test_cli_target_list.py tests/test_cli_assess.py
17 passed

python3 -m pytest
84 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 220 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 192 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0002` 和 `SG-0003` 仍是长期产品/质量缺口。

### IV-0032: Define assess CLI slice

- Target State：`TS-0032: assess CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：下一条 assessment CLI 路径为只读的 `progress assess`
- Evidence：`.progress/evidence/EV-0032-assess-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0032-assess-cli-slice.yaml`
- 状态历史：`PS-0032`
- 主要产物：`docs/05-delivery/36-assess-cli-slice.md`
- 明确边界：
  - 只读取 Project State、Project State 声明的 open gaps 和 next targets
  - 不自动生成 Gap / Target / Intervention
  - 不执行 target suggestion、state refresh、delta apply 或模型调用
- 后续导航：
  - `SG-0026` 已由 `IV-0033` 处理并在 `SDP-0033` 中 apply

### IV-0033: Implement assess CLI slice

- Target State：`TS-0033: assess CLI working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress assess` 已作为只读 assessment 摘要命令实现并测试通过
- Evidence：`.progress/evidence/EV-0033-assess-cli.yaml`
- State Delta：`.progress/deltas/SDP-0033-assess-cli.yaml`
- 状态历史：`PS-0033`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/assessment/assess.py`
  - `tests/test_cli_assess.py`
- 检查结果：

```text
python3 -m pytest tests/test_cli_assess.py
7 passed

python3 -m pytest
84 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 220 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 192 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

- Remaining gaps：
  - `SG-0002` 和 `SG-0003` 仍是长期产品/质量缺口。
  - 当前 `aim_of_next_state` 暂为空，下一轮应先定义后续 target，而不是直接扩展实现。

## 2026-05-17

### IV-0002: Freeze v0.1 MVP boundary

- Target State：`TS-0002: v0.1 MVP boundary accepted`
- 主维度：product
- 结果：已通过 human gate apply，product maturity 从 `reviewed` 推进到 `accepted`
- Evidence：`.progress/evidence/EV-0002-v0.1-mvp-boundary.yaml`
- State Delta：`.progress/deltas/SDP-0002-v0.1-mvp-boundary.yaml`
- 状态历史：`PS-0002`
- 主要产物：`docs/05-delivery/16-mvp-scope-and-roadmap.md`
- Remaining gaps：
  - `SG-0002`: v0.1 真实试点项目尚未选定
  - `SG-0003`: `.progress` 对象 schema、命名约定和必填字段检查仍偏弱

### IV-0003: Select v0.1 technical stack

- Target State：`TS-0003: v0.1 technical stack selected`
- 主维度：architecture
- 结果：已通过 human gate apply，architecture maturity 从 `reviewed` 推进到 `accepted`
- 技术栈结论：Python 3.11+、stdlib-first `argparse` CLI、YAML / Markdown / JSONL repo-native 状态账本
- Evidence：`.progress/evidence/EV-0003-v0.1-tech-stack.yaml`
- State Delta：`.progress/deltas/SDP-0003-v0.1-tech-stack.yaml`
- 状态历史：`PS-0003`
- 主要产物：
  - `docs/03-system-design/06-system-architecture-and-module-boundaries.md`
  - `decisions/ADR-0001-v0.1-tech-stack.md`
- Remaining gaps：
  - `SG-0003`: 完整 schema 校验仍未实现
  - `SG-0004`: 第一批 CLI implementation slice 尚未定义

### IV-0004: Strengthen docs and YAML check

- Target State：`TS-0004: minimum docs and YAML checks working`
- 主维度：quality
- 结果：按 `auto_allowed` policy apply，quality maturity 从 `drafted` 推进到 `reviewed`
- Evidence：`.progress/evidence/EV-0004-docs-and-yaml-check.yaml`
- State Delta：`.progress/deltas/SDP-0004-docs-and-yaml-check.yaml`
- 状态历史：`PS-0004`
- 主要产物：`scripts/check_repo.py`
- 新增质量门禁：
  - required paths 检查
  - YAML parse 检查
  - JSONL parse 检查
  - Markdown local links 检查
  - `.progress` 对象最小必填字段检查
  - `.progress` 对象文件名与 id 前缀一致性检查
- 检查结果：

```text
[OK] required paths exist
[OK] YAML parse passed for 42 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 24 files
```

### IV-0006: Define first Python CLI implementation slice

- Target State：`TS-0006: first Python CLI implementation slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 从 `not_started` 推进到 `seed`
- 切片结论：第一条 Python CLI 用户路径为只读的 `progress state show`
- Evidence：`.progress/evidence/EV-0006-first-python-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0006-first-python-cli-slice.yaml`
- 状态历史：`PS-0005`
- 主要产物：`docs/05-delivery/23-first-python-cli-implementation-slice.md`
- 明确边界：
  - 只读取 `.progress/state/project_state.yaml`
  - 输出 project、phase、dimension maturity、open gaps 和 next target
  - 不修改 `.progress/`
  - 不实现完整 CLI、Delta apply、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0007: Implement first Python CLI state show slice`

### IV-0007: Implement first Python CLI state show slice

- Target State：`TS-0007: first CLI state show slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 从 `seed` 推进到 `drafted`
- 实现结论：`progress state show` 的最小 Python CLI、Project State 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0007-first-cli-state-show.yaml`
- State Delta：`.progress/deltas/SDP-0007-first-cli-state-show.yaml`
- 状态历史：`PS-0006`
- 主要产物：
  - `pyproject.toml`
  - `src/progress_engine/README.md`
  - `src/progress_engine/cli.py`
  - `src/progress_engine/state/project_state.py`
  - `tests/test_cli_state_show.py`
- 检查结果：

```text
python3 -m pytest tests/test_cli_state_show.py
4 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 52 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 33 files
```

### IV-0008: Define next read-only state CLI slice

- Target State：`TS-0008: next read-only CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第二条 Python CLI 用户路径为只读的 `progress gaps list`
- Evidence：`.progress/evidence/EV-0008-next-read-only-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0008-next-read-only-cli-slice.yaml`
- 状态历史：`PS-0007`
- 主要产物：`docs/05-delivery/24-next-read-only-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/state/project_state.yaml` 和 `.progress/gaps/*.yaml`
  - 只输出 Project State 中声明的 open gaps
  - 不修改 `.progress/`
  - 不实现完整 gap management、target suggest、delta apply、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0009: Implement read-only gaps list CLI slice`
- 检查结果：

```text
python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 58 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 39 files
```

### IV-0009: Implement read-only gaps list CLI slice

- Target State：`TS-0009: gaps list CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress gaps list` 的最小 CLI、State Gap 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0009-gaps-list-cli.yaml`
- State Delta：`.progress/deltas/SDP-0009-gaps-list-cli.yaml`
- 状态历史：`PS-0008`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/gaps/gap_list.py`
  - `tests/test_cli_gaps_list.py`
- 检查结果：

```text
python3 -m pytest
8 passed in 0.03s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 65 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 45 files
```

### IV-0010: Define next CLI state object slice

- Target State：`TS-0010: target list CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第三条 Python CLI 用户路径为只读的 `progress target list`
- Evidence：`.progress/evidence/EV-0010-target-list-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0010-target-list-cli-slice.yaml`
- 状态历史：`PS-0009`
- 主要产物：`docs/05-delivery/25-target-list-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/state/project_state.yaml` 和 `.progress/targets/*.yaml`
  - 只输出 Project State 中声明的 next targets
  - 不修改 `.progress/`
  - 不实现 target suggest / approve、intervention planning、delta apply、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0011: Implement read-only target list CLI slice`
- 检查结果：

```text
python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 71 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 51 files
```

### IV-0011: Implement read-only target list CLI slice

- Target State：`TS-0011: target list CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress target list` 的最小 CLI、Target State 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0011-target-list-cli.yaml`
- State Delta：`.progress/deltas/SDP-0011-target-list-cli.yaml`
- 状态历史：`PS-0010`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/targets/target_list.py`
  - `tests/test_cli_target_list.py`
- 检查结果：

```text
python3 -m pytest
12 passed in 0.04s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 78 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 57 files
```

### IV-0012: Define next CLI intervention object slice

- Target State：`TS-0012: intervention list CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第四条 Python CLI 用户路径为只读的 `progress intervention list`
- Evidence：`.progress/evidence/EV-0012-intervention-list-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0012-intervention-list-cli-slice.yaml`
- 状态历史：`PS-0011`
- 主要产物：`docs/05-delivery/26-intervention-list-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/interventions/*.yaml`
  - 默认只输出未完成 Intervention
  - 不修改 `.progress/`
  - 不实现 progress plan、run lifecycle、Evidence、Delta apply、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0013: Implement read-only intervention list CLI slice`
- 检查结果：

```text
python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 84 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 63 files
```

### IV-0013: Implement read-only intervention list CLI slice

- Target State：`TS-0013: intervention list CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress intervention list` 的最小 CLI、Intervention 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0013-intervention-list-cli.yaml`
- State Delta：`.progress/deltas/SDP-0013-intervention-list-cli.yaml`
- 状态历史：`PS-0012`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/interventions/intervention_list.py`
  - `tests/test_cli_intervention_list.py`
- 检查结果：

```text
python3 -m pytest
16 passed in 0.05s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 92 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 69 files
```

### IV-0014: Define next CLI run object slice

- Target State：`TS-0014: run list CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第五条 Python CLI 用户路径为只读的 `progress run list`
- Evidence：`.progress/evidence/EV-0014-run-list-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0014-run-list-cli-slice.yaml`
- 状态历史：`PS-0013`
- 主要产物：`docs/05-delivery/27-run-list-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/runs/*.yaml`
  - 默认只输出未关闭 Run
  - 不修改 `.progress/`
  - 不实现 progress run start、run lifecycle 写操作、Evidence、Delta apply、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0015: Implement read-only run list CLI slice`
- 检查结果：

```text
python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 101 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 78 files
```

### IV-0015: Implement read-only run list CLI slice

- Target State：`TS-0015: run list CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress run list` 的最小 CLI、Run 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0015-run-list-cli.yaml`
- State Delta：`.progress/deltas/SDP-0015-run-list-cli.yaml`
- 状态历史：`PS-0014`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/runs/run_list.py`
  - `tests/test_cli_run_list.py`
- 检查结果：

```text
python3 -m pytest
20 passed in 0.07s

python3 -m pytest tests/test_cli_run_list.py
4 passed in 0.02s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 106 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 81 files
```

### IV-0016: Define next evidence object CLI slice

- Target State：`TS-0016: evidence list CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第六条 Python CLI 用户路径为只读的 `progress evidence list`
- Evidence：`.progress/evidence/EV-0016-evidence-list-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0016-evidence-list-cli-slice.yaml`
- 状态历史：`PS-0015`
- 主要产物：`docs/05-delivery/28-evidence-list-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/evidence/*.yaml`
  - 读取 `evidence` 根 mapping 下的最小 Evidence 字段
  - 不修改 `.progress/`
  - 不实现 progress evidence add、Verification、Delta apply、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0017: Implement read-only evidence list CLI slice`
- 检查结果：

```text
python3 -m pytest
20 passed in 0.07s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 112 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 87 files
```

### IV-0017: Implement read-only evidence list CLI slice

- Target State：`TS-0017: evidence list CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress evidence list` 的最小 CLI、Evidence 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0017-evidence-list-cli.yaml`
- State Delta：`.progress/deltas/SDP-0017-evidence-list-cli.yaml`
- 状态历史：`PS-0016`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/evidence/evidence_list.py`
  - `tests/test_cli_evidence_list.py`
- 明确边界：
  - 只读取 `.progress/evidence/*.yaml`
  - 读取 `evidence` 根 mapping 下的最小 Evidence 字段
  - 不修改 `.progress/`
  - 不实现 progress evidence add、Verification、Delta apply、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0015` 和 `TS-0018`，下一步先定义 Verification 相关只读 CLI 切片
- 检查结果：

```text
python3 -m pytest tests/test_cli_evidence_list.py
7 passed in 0.07s

python3 -m pytest
27 passed in 0.09s

PYTHONPATH=src python3 -m progress_engine evidence list
Printed Evidence summaries for EV-0002 through EV-0017.

PYTHONPATH=src python3 -m progress_engine target list
Next targets:
- TS-0018 [implementation] next verification CLI slice defined (proposed)

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 120 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 94 files
```

### IV-0018: Define next verification CLI slice

- Target State：`TS-0018: next verification CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第七条 Python CLI 用户路径为只读的 `progress verify list`
- Evidence：`.progress/evidence/EV-0018-verify-list-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0018-verify-list-cli-slice.yaml`
- 状态历史：`PS-0017`
- 主要产物：`docs/05-delivery/29-verify-list-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/evidence/*.yaml`
  - 复用 Evidence loader，读取 reviewer result 和 acceptance mapping status
  - 不修改 `.progress/`
  - 不实现 progress verify --run、verification artifact 生成、State Delta Proposal 生成、Delta apply、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0019: Implement read-only verify list CLI slice`
- 检查结果：

```text
python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 131 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 105 files
```

### IV-0019: Implement read-only verify list CLI slice

- Target State：`TS-0019: verify list CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress verify list` 的最小 CLI、Verification review 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0019-verify-list-cli.yaml`
- State Delta：`.progress/deltas/SDP-0019-verify-list-cli.yaml`
- 状态历史：`PS-0018`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/verification/verify_list.py`
  - `tests/test_cli_verify_list.py`
- 明确边界：
  - 只读取 `.progress/evidence/*.yaml`
  - 复用 Evidence loader
  - 只汇总 reviewer result 和 acceptance mapping status
  - 不修改 `.progress/`
  - 不实现 progress verify --run、verification artifact 生成、State Delta Proposal 生成、Delta apply、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0016` 和 `TS-0020`，下一步先定义 State Delta Proposal 相关只读 CLI 切片
- 检查结果：

```text
python3 -m pytest tests/test_cli_verify_list.py
7 passed in 0.04s

python3 -m pytest
34 passed in 0.11s

PYTHONPATH=src python3 -m progress_engine verify list
Printed Verification review summaries for EV-0002 through EV-0019.

PYTHONPATH=src python3 -m progress_engine target list
Next targets:
- TS-0020 [implementation] next state delta CLI slice defined (proposed)

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 131 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 105 files
```

### IV-0020: Define next state delta CLI slice

- Target State：`TS-0020: next state delta CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第八条 Python CLI 用户路径为只读的 `progress delta list`
- Evidence：`.progress/evidence/EV-0020-delta-list-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0020-delta-list-cli-slice.yaml`
- 状态历史：`PS-0019`
- 主要产物：`docs/05-delivery/30-delta-list-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/deltas/*.yaml`
  - 读取 `state_delta_proposal` 根 mapping 下的最小 proposal 字段和 acceptance summary
  - 不修改 `.progress/`
  - 不实现 progress delta apply、reject、rollback、Project State 写入、state history 写入、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0021: Implement read-only delta list CLI slice`
- 检查结果：

```text
python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 143 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 116 files
```

### IV-0021: Implement read-only delta list CLI slice

- Target State：`TS-0021: delta list CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress delta list` 的最小 CLI、State Delta Proposal 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0021-delta-list-cli.yaml`
- State Delta：`.progress/deltas/SDP-0021-delta-list-cli.yaml`
- 状态历史：`PS-0020`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/deltas/delta_list.py`
  - `tests/test_cli_delta_list.py`
- 明确边界：
  - 只读取 `.progress/deltas/*.yaml`
  - 读取 `state_delta_proposal` 根 mapping 下的最小 proposal 字段和 acceptance summary
  - 不修改 `.progress/`
  - 不实现 progress delta apply、reject、rollback、Project State 写入、state history 写入、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0017` 和 `TS-0022`，下一步先定义 Change Event 相关只读 CLI 切片
- 检查结果：

```text
python3 -m pytest tests/test_cli_delta_list.py
7 passed in 0.04s

python3 -m pytest
41 passed in 0.14s

PYTHONPATH=src python3 -m progress_engine delta list
Printed State Delta Proposal summaries for SDP-0002 through SDP-0021.

PYTHONPATH=src python3 -m progress_engine target list
Next targets:
- TS-0022 [implementation] next change event CLI slice defined (proposed)

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 143 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 116 files
```

### IV-0022: Define next change event CLI slice

- Target State：`TS-0022: next change event CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第九条 Python CLI 用户路径为只读的 `progress event list`
- Evidence：`.progress/evidence/EV-0022-event-list-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0022-event-list-cli-slice.yaml`
- 状态历史：`PS-0021`
- 主要产物：`docs/05-delivery/31-event-list-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/events/*.yaml`
  - 读取 `change_event` 根 mapping 下的最小 event 字段
  - 不修改 `.progress/`
  - 不实现 progress event add、event show、invalidation propagation、Project State 写入、JSONL event log 写入、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0023: Implement read-only event list CLI slice`
- 检查结果：

```text
python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 155 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 127 files
```

### IV-0023: Implement read-only event list CLI slice

- Target State：`TS-0023: event list CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress event list` 的最小 CLI、Change Event 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0023-event-list-cli.yaml`
- State Delta：`.progress/deltas/SDP-0023-event-list-cli.yaml`
- 状态历史：`PS-0022`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/events/event_list.py`
  - `tests/test_cli_event_list.py`
- 明确边界：
  - 只读取 `.progress/events/*.yaml`
  - 读取 `change_event` 根 mapping 下的最小 event 字段
  - 不修改 `.progress/`
  - 不实现 progress event add、event show、invalidation propagation、Project State 写入、JSONL event log 写入、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0018` 和 `TS-0024`，下一步先定义 State History 相关只读 CLI 切片
- 检查结果：

```text
python3 -m pytest tests/test_cli_event_list.py
8 passed in 0.04s

python3 -m pytest
49 passed in 0.18s

PYTHONPATH=src python3 -m progress_engine event list
Printed Change Event summary for EVT-0002.

PYTHONPATH=src python3 -m progress_engine target list
Next targets:
- TS-0024 [implementation] next state history CLI slice defined (proposed)

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 155 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 127 files
```

### IV-0024: Define next state history CLI slice

- Target State：`TS-0024: next state history CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第十条 Python CLI 用户路径为只读的 `progress state history`
- Evidence：`.progress/evidence/EV-0024-state-history-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0024-state-history-cli-slice.yaml`
- 状态历史：`PS-0023`
- 主要产物：`docs/05-delivery/32-state-history-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/state/state_history.jsonl`
  - 读取每条 history entry 的最小字段
  - 不修改 `.progress/`
  - 不实现 progress state refresh、state replay、rollback、delta apply、模型 API、Web UI 或 agent 编排
- 推荐下一步：
  - 执行 `IV-0025: Implement read-only state history CLI slice`
- 检查结果：

```text
python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 166 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 138 files
```

### IV-0025: Implement read-only state history CLI slice

- Target State：`TS-0025: state history CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress state history` 的最小 CLI、State History JSONL 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0025-state-history-cli.yaml`
- State Delta：`.progress/deltas/SDP-0025-state-history-cli.yaml`
- 状态历史：`PS-0024`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/state/state_history.py`
  - `tests/test_cli_state_history.py`
- 明确边界：
  - 只读取 `.progress/state/state_history.jsonl`
  - 读取每条 history entry 的最小字段
  - 不修改 `.progress/`
  - 不实现 progress state refresh、state replay、rollback、delta apply、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0019` 和 `TS-0026`，下一步先定义 .progress 对象质量检查增强切片
- 检查结果：

```text
python3 -m pytest tests/test_cli_state_history.py
6 passed in 0.04s

python3 -m pytest
55 passed in 0.20s

PYTHONPATH=src python3 -m progress_engine state history
Printed State History summaries for PS-0002 through PS-0022.

PYTHONPATH=src python3 -m progress_engine target list
Next targets:
- TS-0026 [quality] next progress object quality slice defined (proposed)

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 166 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 138 files
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- 定义 `TS-0032: assess CLI slice`

### IV-0031: Implement intent intake CLI slice

- Target State：`TS-0031: intent intake CLI working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress intake --from FILE` 可捕获初始 intent artifact，并把 Project State intent 维度更新为 `seed`
- Evidence：`.progress/evidence/EV-0031-intent-intake-cli.yaml`
- State Delta：`.progress/deltas/SDP-0031-intent-intake-cli.yaml`
- 状态历史：`PS-0030`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/intake/intent_intake.py`
  - `tests/test_cli_intake.py`
- 明确边界：
  - 只写入 `.progress/artifacts/intent.md`
  - 只更新 Project State 的 intent 维度
  - 不实现 assess、target suggestion、Gap / Target / Intervention 自动生成、Evidence 对象、State Delta Proposal、delta apply、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0025` 和 `TS-0032`，下一步先定义只读 `progress assess` slice
- 检查结果：

```text
python3 -m pytest tests/test_cli_intake.py tests/test_cli_init.py
9 passed in 0.06s

python3 -m pytest
69 passed in 0.27s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 202 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 174 files
[OK] Project State reference checks passed

progress init -> progress intake -> progress state show
intent: seed
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- 定义 `TS-0032: assess CLI slice`

### IV-0032: Define assess CLI slice

- Target State：`TS-0032: assess CLI slice defined`
- 主维度：implementation
- 结果：已完成 artifact review，State Delta Proposal 保持 `proposed`，等待 human gate；implementation maturity 暂不变更
- 切片结论：下一条 assessment CLI 路径为只读的 `progress assess`
- Evidence：`.progress/evidence/EV-0032-assess-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0032-assess-cli-slice.yaml`
- 状态历史：未写入；`TS-0032` 要求 human gate，当前未执行 delta apply
- 主要产物：`docs/05-delivery/36-assess-cli-slice.md`
- 明确边界：
  - 只读取 `.progress/state/project_state.yaml`
  - 只读取 Project State 声明的 open gaps 和 next targets
  - 不自动生成 Gap / Target / Intervention
  - 不实现 target suggestion、state refresh、delta apply、模型 API、Web UI 或 agent 编排
- Remaining gaps：
  - `SG-0026`: `progress assess` 已定义但尚未实现；下一步应在 human gate 接受后执行 `IV-0033: Implement assess CLI slice`
- 检查结果：

```text
python3 -m pytest
69 passed in 0.28s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 208 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 180 files
[OK] Project State reference checks passed
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- human gate review `SDP-0032`；接受后执行 `IV-0033: Implement assess CLI slice`

### IV-0033: Implement assess CLI slice

- Target State：`TS-0033: assess CLI working`
- 主维度：implementation
- 结果：已完成代码实现、测试和 verifier evidence；State Delta Proposal 保持 `proposed`，等待 human gate；implementation maturity 暂不变更
- 实现结论：`progress assess` 可以只读输出当前 Project State maturity、Project State 声明的 open gaps 和 Project State 声明的 next targets
- Evidence：`.progress/evidence/EV-0033-assess-cli.yaml`
- State Delta：`.progress/deltas/SDP-0033-assess-cli.yaml`
- 状态历史：未写入；`TS-0033` 要求 human gate，当前未执行 delta apply
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/assessment/assess.py`
  - `tests/test_cli_assess.py`
  - `src/progress_engine/README.md`
- 明确边界：
  - 只读取 `.progress/state/project_state.yaml`
  - 只读取 Project State 声明的 open gaps 和 next targets
  - 不自动生成 Gap / Target / Intervention
  - 不实现 target suggestion、state refresh、delta apply、模型 API、Web UI 或 agent 编排
- Remaining gaps：
  - `SG-0026`: 代码实现已完成，但等待 human gate apply 前仍不更新 Project State 和 state history
- 检查结果：

```text
python3 -m pytest tests/test_cli_assess.py
7 passed

python3 -m pytest
76 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 212 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 184 files
[OK] Project State reference checks passed

PYTHONPATH=src python3 -m progress_engine assess
Assessment:
Project: progress-engine
Phase: repo_bootstrap
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- human gate review `SDP-0033`；接受后再更新 Project State / state history 并选择下一条 target

### EVT-0003: Repair CLI status documentation drift

- Change Event：`EVT-0003: readme cli status drift`
- 主维度：quality / knowledge / implementation
- 结果：已修复入口文档、结构文档、ADR 和系统架构文档中的实现前状态漂移；未修改 Project State，未执行 State Delta apply
- Evidence：本轮 git diff、`python3 -m pytest`、`python3 scripts/check_repo.py`、`PYTHONPATH=src python3 -m progress_engine assess`
- State Delta：无。本轮是质量缺口修复和门禁增强，不声明 Project State 成熟度变化
- 状态历史：未写入；不绕过 human gate / State Delta apply 流程
- 主要产物：
  - `README.md`
  - `PROJECT_STRUCTURE.md`
  - `decisions/ADR-0001-v0.1-tech-stack.md`
  - `docs/03-system-design/06-system-architecture-and-module-boundaries.md`
  - `scripts/check_repo.py`
  - `tests/test_check_repo.py`
  - `src/progress_engine/README.md`
  - `.progress/events/EVT-0003-readme-cli-status-drift.yaml`
- 修复内容：
  - 顶层 README 从早期 bootstrap 指令更新为当前 CLI-first 本地使用入口
  - Project Structure 从“预留实现目录”更新为真实 `src/progress_engine/` 和 pytest 结构
  - ADR-0001 从 `Proposed` 更新为已通过 human gate 的 `Accepted`
  - 系统架构文档删除 `pyproject.toml` 尚未创建、代码实现前等过期叙述
  - 仓库检查新增 CLI 状态文档漂移门禁，覆盖 README、PROJECT_STRUCTURE、ADR-0001 和系统架构文档
- 检查结果：

```text
python3 -m pytest
82 passed

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 213 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 185 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed

PYTHONPATH=src python3 -m progress_engine assess
Assessment output remained read-only and continued to show Project State before SDP-0033 apply.
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- human gate review `SDP-0033`；接受后再更新 Project State / state history
- 继续处理 remaining gaps：`SG-0002`、`SG-0003` 和未 apply 的 `SG-0025` / `SG-0026`

### IV-0030: Define intent intake CLI slice

- Target State：`TS-0030: intent intake CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：下一条 bootstrap CLI 路径为 `progress intake --from FILE`
- Evidence：`.progress/evidence/EV-0030-intent-intake-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0030-intent-intake-cli-slice.yaml`
- 状态历史：`PS-0029`
- 主要产物：`docs/05-delivery/35-intent-intake-cli-slice.md`
- 明确边界：
  - 只写入 `.progress/artifacts/intent.md`
  - 只把 Project State intent 维度标记为 `seed`
  - 不实现 assess、target suggestion、Gap / Target / Intervention 自动生成、Evidence 对象生成、State Delta Proposal、delta apply、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0024` 和 `TS-0031`，下一步有限实现 `progress intake --from FILE`

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- 执行 `IV-0031: Implement intent intake CLI slice`

### IV-0029: Implement init CLI slice

- Target State：`TS-0029: init CLI slice working`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 实现结论：`progress init --project PROJECT_ID` 可创建最小 `.progress/` 骨架，并拒绝覆盖已有 `.progress/`
- Evidence：`.progress/evidence/EV-0029-init-cli.yaml`
- State Delta：`.progress/deltas/SDP-0029-init-cli.yaml`
- 状态历史：`PS-0028`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/init/init_project.py`
  - `tests/test_cli_init.py`
- 明确边界：
  - 只在不存在 `.progress/` 时创建最小骨架
  - 生成的 `.progress/state/project_state.yaml` 可被 `progress state show` 读取
  - 不实现 intake、assess、state refresh、delta apply、自动 gap / target 生成、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0023` 和 `TS-0030`，下一步先定义 intent intake CLI slice
- 检查结果：

```text
python3 -m pytest tests/test_cli_init.py
4 passed in 0.03s

python3 -m pytest
64 passed in 0.29s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 190 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 162 files
[OK] Project State reference checks passed

PYTHONPATH=src python3 -m progress_engine init --project sample-project
Initialized ProgressEngine project: sample-project

PYTHONPATH=src python3 -m progress_engine state show
Project: sample-project
Phase: initialized
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- 定义 `TS-0030: intent intake CLI slice`

### IV-0028: Define next state-changing CLI slice

- Target State：`TS-0028: next state-changing CLI slice defined`
- 主维度：implementation
- 结果：已通过 human gate apply，implementation maturity 保持 `drafted`
- 切片结论：第一条写操作 CLI 路径为 `progress init --project PROJECT_ID`
- Evidence：`.progress/evidence/EV-0028-state-changing-cli-slice.yaml`
- State Delta：`.progress/deltas/SDP-0028-state-changing-cli-slice.yaml`
- 状态历史：`PS-0027`
- 主要产物：`docs/05-delivery/34-init-cli-slice.md`
- 明确边界：
  - 只在不存在 `.progress/` 时创建最小骨架
  - 拒绝覆盖或迁移已有 `.progress/`
  - 不实现 intake、assess、state refresh、delta apply、自动 gap / target 生成、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0022` 和 `TS-0029`，下一步有限实现 `progress init --project PROJECT_ID`

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- 执行 `IV-0029: Implement init CLI slice`

### IV-0027: Implement project state reference check slice

- Target State：`TS-0027: project state reference check working`
- 主维度：quality
- 结果：已通过 human gate apply，quality maturity 保持 `reviewed`
- 实现结论：`scripts/check_repo.py` 已能检查 Project State 的 `open_state_gaps` 和 `aim_of_next_state` 引用完整性
- Evidence：`.progress/evidence/EV-0027-project-state-reference-check.yaml`
- State Delta：`.progress/deltas/SDP-0027-project-state-reference-check.yaml`
- 状态历史：`PS-0026`
- 主要产物：
  - `scripts/check_repo.py`
  - `tests/test_check_repo.py`
- 明确边界：
  - 只检查 Project State 的 open gap 和 next target 引用
  - 不自动修复 `.progress` 对象
  - 不实现完整 schema engine、state refresh、delta apply、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0021` 和 `TS-0028`，下一步先定义第一个受控写操作 CLI slice
- 检查结果：

```text
python3 -m pytest tests/test_check_repo.py
5 passed in 0.03s

python3 -m pytest
60 passed in 0.24s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 178 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 150 files
[OK] Project State reference checks passed
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- 定义 `TS-0028: next state-changing CLI slice`

### IV-0026: Define next progress object quality slice

- Target State：`TS-0026: next progress object quality slice defined`
- 主维度：quality
- 结果：已通过 human gate apply，quality maturity 保持 `reviewed`
- 切片结论：下一条质量检查切片为 Project State reference integrity check
- Evidence：`.progress/evidence/EV-0026-progress-object-quality-slice.yaml`
- State Delta：`.progress/deltas/SDP-0026-progress-object-quality-slice.yaml`
- 状态历史：`PS-0025`
- 主要产物：`docs/05-delivery/33-project-state-reference-check-slice.md`
- 明确边界：
  - 只增强 `python3 scripts/check_repo.py`
  - 只校验 `open_state_gaps` 和 `aim_of_next_state` 引用
  - 不自动修复 `.progress` 对象
  - 不实现完整 schema engine、state refresh、delta apply、模型 API、Web UI 或 agent 编排
- 后续导航：
  - 新增 `SG-0020` 和 `TS-0027`，下一步有限实现 Project State 引用完整性检查
- 检查结果：

```text
python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 172 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 144 files
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- 执行 `IV-0027: Implement project state reference check slice`
