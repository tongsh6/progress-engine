# Context Capsule: IV-0051

## Project Snapshot

- Project: progress-engine
- Phase: repo_bootstrap
- State Version: PS-0049
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

- ID: TS-0051
- Dimension: implementation
- Status: proposed
- Desired State: `progress capsule --intervention IV-ID` 作为只读 prompt-only CLI 切片可运行、可测试、可追溯。
- From: maturity=drafted; summary=Context Capsule CLI slice 已定义，但命令尚未实现。
- To: maturity=drafted; summary=`progress capsule --intervention IV-ID` 能生成 Markdown capsule，且不修改 Project State 或调用模型 API。

## Intervention

- ID: IV-0051
- Title: Implement Context Capsule CLI slice
- Goal: 实现 `progress capsule --intervention IV-ID`，生成只读 prompt-only Markdown Context Capsule。
- Status: proposed
- Primary Dimension: implementation
- Target State: TS-0051

## In Scope
- 实现 capsule CLI parser 和 renderer。
- 读取 Project State、Intervention、Target State 和必要引用。
- 写入 `.progress/context_capsules/{IV-ID}-context-capsule.md`。
- 新增 focused pytest 覆盖成功路径和错误路径。

## Out of Scope
- 不实现 run lifecycle。
- 不调用模型 API、Web UI 或外部 agent。
- 不自动执行 Intervention。
- 不生成 Evidence、Verification 或 State Delta。

## Inputs
- .progress/state/project_state.yaml
- .progress/state/state_history.jsonl
- .progress/interventions/IV-0051-implement-context-capsule-cli-slice.yaml
- .progress/targets/TS-0051-context-capsule-cli-working.yaml
- Open Gap: SG-0041
- Next Target: TS-0051

## Outputs
- .progress/context_capsules/IV-0051-context-capsule.md
- Execution artifacts and evidence must be recorded after the intervention runs.

## Acceptance Criteria
- AC-TS-0051-01: `progress capsule --intervention IV-ID` 能解析 canonical Intervention 和 Target。
- AC-TS-0051-02: 命令生成 `.progress/context_capsules/{IV-ID}-context-capsule.md`。
- AC-TS-0051-03: Capsule 包含 Fresh Context 必需章节和 evidence_required。
- AC-TS-0051-04: 命令不修改 Project State、state history、Evidence、State Delta、Gap、Target、Intervention 或 Event。
- AC-TS-0051-05: focused pytest、全量 pytest 和仓库检查通过。
- AC-TS-0051-06: 本轮不调用模型 API、Web UI 或外部 agent。

## Evidence Required
- python3 -m pytest tests/test_cli_capsule.py 通过。
- python3 -m pytest 通过。
- python3 scripts/check_repo.py 通过。
- 生成 capsule 的示例输出和关键片段。

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
