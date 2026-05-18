# Assess CLI Slice

本文定义 `IV-0032: Define assess CLI slice` 的实现切片。它延续当前 CLI-first 路线，但保持只读：`progress assess` 只汇总已有 Project State、open gaps 和 next targets，不自动生成新的状态对象。

## 1. 切片结论

下一条 assessment CLI 用户路径选择：

```bash
progress assess
```

该命令在已初始化的 `.progress/` 中：

- 读取 `.progress/state/project_state.yaml`。
- 读取 Project State 中声明的 open gap 文件。
- 读取 Project State 中声明的 next target 文件。
- 输出一个确定性的项目状态评估摘要。

选择它的原因：

- 当前 `aim_of_next_state` 是 `TS-0032`，对应开放缺口 `SG-0025`。
- `progress intake` 已能捕获初始 intent；下一步需要让用户看见当前状态、缺口和下一目标，而不是直接自动生成计划。
- `progress assess` 可以复用现有只读对象加载路径，风险低、可测试、符合 State-first 方法。
- 该命令不写入 `.progress/`，不会绕过 Evidence / Verification / Delta gate。

## 2. 用户路径

目标用户在已初始化并已有 Project State 的仓库根目录运行：

```bash
progress assess
```

期望输出包含：

```text
Assessment:
Project: progress-engine
Phase: repo_bootstrap

Maturity:
- intent: accepted
- product: accepted
- design: drafted
- architecture: accepted
- implementation: drafted
- quality: reviewed
- delivery: weak
- knowledge: reviewed

Open gaps:
- SG-0001 [delivery] 仓库具备可审查的项目初始状态，包括策划文档、.progress 状态账本、GitHub 模板和基础自检脚本。
- SG-0002 [product] 至少选定一个真实或代表性试点项目，用于验证 v0.1 状态闭环是否能从 accepted 推进到 validated。
- SG-0003 [quality] .progress 对象具备最小一致性检查，至少覆盖 Target State、Intervention、Evidence、State Delta Proposal 和 Change Event 的必填字段。
- SG-0025 [implementation] 下一条 assess CLI slice 被明确限定为只读地汇总 Project State maturity、open gaps 和 next targets，不自动生成新对象。

Next targets:
- TS-0032 [implementation] assess CLI slice defined

Next:
- progress target list
- progress intervention list
```

如果 Project State 缺失、open gap 引用缺失或 next target 引用缺失，命令返回 exit code `2` 并输出清晰错误。

## 3. 输入、输出和状态影响

输入：

- `.progress/state/project_state.yaml`
- `.progress/gaps/*.yaml` 中被 `open_state_gaps` 引用的文件
- `.progress/targets/*.yaml` 中被 `aim_of_next_state` 引用的文件

输出：

- stdout 的 assessment 摘要
- stderr 的错误说明

process exit code：

- `0`：assessment 摘要输出成功。
- `2`：Project State 缺失、YAML 解析失败、gap / target 引用缺失或对象结构不满足最小读取要求。

状态影响：

- 不修改 `.progress/state/project_state.yaml`。
- 不写入 `.progress/gaps/`、`.progress/targets/`、`.progress/interventions/`、`.progress/evidence/`、`.progress/deltas/` 或 `.progress/events/`。
- 不生成 Gap / Target / Intervention。
- 不运行 state refresh、delta apply 或模型调用。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
src/progress_engine/cli.py
src/progress_engine/assessment/__init__.py
src/progress_engine/assessment/assess.py
tests/test_cli_assess.py
src/progress_engine/README.md
```

必要时可以小幅复用或调整现有只读 loader 的公开函数，但不得借机实现 target suggest、intervention planning、context capsule、state refresh、delta apply 或模型调用。

## 5. 最小行为规则

- CLI 继续使用 Python 3.11+ 和 `argparse`。
- 默认从当前工作目录解析 `.progress/`。
- 输出必须是稳定纯文本，便于命令输出测试。
- assessment 只基于账本已有字段，不扫描代码库推断状态。
- open gaps 必须来自 Project State 的 `open_state_gaps`，不能扫描输出未引用 gap。
- next targets 必须来自 Project State 的 `aim_of_next_state`，不能自动排序或推荐新 target。
- 引用漂移必须失败，不能静默跳过。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-CLI-013-01 | `progress assess` 能读取 Project State 并输出 project、phase 和各维度 maturity 摘要。 |
| AC-CLI-013-02 | 命令只列出 Project State 中声明的 open gaps，并包含 gap id、dimension 和 desired_state。 |
| AC-CLI-013-03 | 命令只列出 Project State 中声明的 next targets，并包含 target id、primary_dimension 和 name。 |
| AC-CLI-013-04 | Project State、gap 或 target 引用缺失 / YAML 不可解析时返回 exit code `2` 并输出清晰错误。 |
| AC-CLI-013-05 | pytest 覆盖成功路径、缺 Project State、缺 gap 引用和缺 target 引用路径。 |
| AC-CLI-013-06 | `python3 scripts/check_repo.py` 和全量 pytest 仍通过。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_cli_assess.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果。
- `progress assess` 在 fixture 项目中的示例输出。
- git diff 摘要，证明没有实现自动 Gap / Target / Intervention 生成、state refresh、delta apply 或模型调用。

## 8. Out of Scope

本切片明确不做：

- 自动生成 Gap / Target / Intervention
- target suggestion 或 scoring
- intervention planning
- Fresh Context Capsule
- Evidence 对象生成
- Verification 或 State Delta Proposal 生成
- `progress state refresh`
- `progress delta apply`、reject 或 rollback
- 代码库扫描、模型 API、Web UI 或外部 agent 调用

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0033: Implement assess CLI slice
```

`IV-0033` 的目标不是“实现自动项目理解”，而是只把已有状态账本整理成可读、可测试、只读的 assessment 摘要。
