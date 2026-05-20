# Context Capsule: IV-0053

## Project Snapshot

- Project: progress-engine
- Phase: repo_bootstrap
- State Version: PS-0051
- Current Maturity:
  - intent: accepted
  - product: accepted
  - design: drafted
  - architecture: accepted
  - implementation: drafted
  - quality: reviewed
  - delivery: reviewed
  - knowledge: reviewed

## Target State

- ID: TS-0053
- Dimension: implementation
- Status: proposed
- Desired State: `progress run start --intervention IV-ID --mode prompt-only` 作为受控写入切片可运行、可测试、可追踪。
- From: maturity=drafted; summary=prompt-only run start CLI slice 已定义，但命令尚未实现。
- To: maturity=drafted; summary=`progress run start --intervention IV-ID --mode prompt-only` 能创建 active Run 并关联 capsule，且不修改 Project State 或调用模型 API。

## Intervention

- ID: IV-0053
- Title: Implement prompt-only run start CLI slice
- Goal: 实现 `progress run start --intervention IV-ID --mode prompt-only`，创建 active Run 并关联 Context Capsule。
- Status: proposed
- Primary Dimension: implementation
- Target State: TS-0053

## In Scope
- 实现 run start CLI parser 和 writer。
- 读取 Project State、Intervention、Target State 和 Context Capsule。
- 必要时生成缺失 capsule。
- 写入 `.progress/runs/{RUN-ID}-*.yaml`。
- 新增 focused pytest 覆盖成功路径和错误路径。

## Out of Scope
- 不实现 run close。
- 不调用模型 API、Web UI 或外部 agent。
- 不自动执行 Intervention。
- 不生成 Evidence、Verification 或 State Delta。

## Inputs
- .progress/state/project_state.yaml
- .progress/state/state_history.jsonl
- .progress/interventions/IV-0053-implement-run-start-cli-slice.yaml
- .progress/targets/TS-0053-run-start-cli-working.yaml
- Open Gap: SG-0043
- Next Target: TS-0053

## Outputs
- .progress/context_capsules/IV-0053-context-capsule.md
- Execution artifacts and evidence must be recorded after the intervention runs.

## Acceptance Criteria
- AC-TS-0053-01: `progress run start --intervention IV-ID --mode prompt-only` 能解析 canonical Intervention 和 Target。
- AC-TS-0053-02: 命令创建 active Run YAML 并关联 Context Capsule。
- AC-TS-0053-03: 命令拒绝 unsupported mode 和重复 active/planned Run。
- AC-TS-0053-04: 命令不修改 Project State、state history、Evidence、State Delta、Gap、Target、Intervention 或 Event。
- AC-TS-0053-05: focused pytest、全量 pytest 和仓库检查通过。
- AC-TS-0053-06: 本轮不调用模型 API、Web UI 或外部 agent。

## Evidence Required
- python3 -m pytest tests/test_cli_run_start.py 通过。
- python3 -m pytest 通过。
- python3 scripts/check_repo.py 通过。
- 生成 Run YAML 的示例输出和关键字段。

## Rules

- Use only this context and referenced files.
- Do not carry forward prior transcript.
- Do not expand scope.
- Do not claim completion without acceptance mapping.
- Do not defer silently.
- Output evidence and remaining gaps.
- Do not modify Project State or state history directly.

## Failure Handling

- If required context is missing, stop and report the missing input.
- If scope exceeds this capsule, propose a split intervention.
- If acceptance criteria cannot be satisfied, report remaining gaps.
- Do not create Evidence, Verification, or State Delta objects unless explicitly assigned.
