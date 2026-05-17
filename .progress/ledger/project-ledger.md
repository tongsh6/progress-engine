# ProgressEngine 项目推进台账

本台账记录项目状态如何被推进。它不是任务列表，也不是完成清单；每条记录都必须说明目标状态、证据、State Delta 和 remaining gaps。

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
- 结果：已提交 Evidence 和 State Delta Proposal，等待 human gate；未将 `EV-0015` 直接写入 Project State evidence
- 实现结论：`progress run list` 的最小 CLI、Run 只读加载和 pytest 覆盖已完成
- Evidence：`.progress/evidence/EV-0015-run-list-cli.yaml`
- State Delta Proposal：`.progress/deltas/SDP-0015-run-list-cli.yaml`
- 主要产物：
  - `src/progress_engine/cli.py`
  - `src/progress_engine/runs/run_list.py`
  - `tests/test_cli_run_list.py`
- 检查结果：

```text
python3 -m pytest
20 passed in 0.07s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 106 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 81 files
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`drafted`

## 下一步推荐

- human gate 审查 `SDP-0015: run list CLI slice`
