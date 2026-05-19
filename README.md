# ProgressEngine

> **持续推进项目状态，而不是持续完成任务。**

ProgressEngine 是一个状态驱动的 AI 软件工程系统。它通过状态建模、目标状态规划、推进动作拆解、Fresh Context 隔离执行和 Evidence Verifier 证据验证，把模糊项目意图逐步推进为可用产品、工程资产和决策结果。

当前仓库处于 **v0.1 CLI bootstrap** 阶段：已经具备项目策划书、方法论、协议、模板、初始 `.progress/` 状态账本、GitHub 协作骨架和一组可测试的本地 CLI 切片。

## 当前目标状态

```text
仓库从“可审查项目状态”推进为“可在本地维护最小状态推进闭环的 CLI-first 工具”。
```

## 当前已实现 CLI

<!-- progress-engine-cli-commands:start -->
```bash
progress init --project PROJECT_ID
progress intake --from FILE
progress assess
progress state show
progress state history
progress gaps list
progress target list
progress intervention list
progress run list
progress evidence list
progress verify list
progress delta list
progress delta apply SDP-ID --approved-by NAME
progress event list
```
<!-- progress-engine-cli-commands:end -->

这些命令仍遵守 v0.1 边界：除 `init`、`intake` 和 human-gated `delta apply` 这三个受控写入切片外，当前命令只读取 `.progress/` 账本，不自动生成 Gap、Target、Intervention、Evidence、State Delta，不执行 reject / rollback / state refresh，也不调用模型或外部 agent。

## 推荐阅读顺序

1. `PROJECT_BRIEF.md`：项目摘要和核心口径。
2. `dist/ProgressEngine_Project_Plan_full.md`：完整 Markdown 策划书。
3. `docs/00-overview/02-core-methodology-state-driven-progress.md`：核心方法论。
4. `docs/01-state-engine/03-project-state-model-and-maturity-matrix.md`：项目状态成熟度矩阵。
5. `docs/02-bootstrap-workflows/05-zero-to-project-role-pipeline.md`：从 0 启动角色流水线。
6. `docs/04-protocols/09-fresh-context-isolation-protocol.md`：上下文隔离协议。
7. `docs/04-protocols/10-evidence-verifier-protocol.md`：证据验证协议。
8. `.progress/state/project_state.yaml`：当前项目状态。

## 仓库结构

```text
progress-engine/
  README.md
  PROJECT_BRIEF.md
  PROJECT_STRUCTURE.md
  INDEX.md
  CHANGELOG.md
  LICENSE.TODO.md

  docs/                    # 分章节策划书与协议
  dist/                    # 完整 Markdown / HTML 策划书
  templates/               # 状态、执行、验证、治理模板
  diagrams/                # Mermaid 图示
  reports/                 # 自检与版本报告
  examples/                # 示例项目状态材料

  .progress/               # ProgressEngine 自身的项目状态账本
    state/
    gaps/
    targets/
    interventions/
    events/
    runs/
    evidence/
    deltas/
    ledger/
    context_capsules/

  .github/                 # GitHub 协作模板和自检 workflow
  scripts/                 # 仓库检查与初始化脚本
  schemas/                 # 后续 schema 实现位置
  src/                     # CLI / 核心代码实现位置
  tests/                   # pytest 测试
```

## 本地使用建议

```bash
git clone git@github.com:tongsh6/progress-engine.git
cd progress-engine

python3 -m pytest
python3 scripts/check_repo.py
PYTHONPATH=src python3 -m progress_engine assess
```

如果使用 HTTPS：

```bash
git clone https://github.com/tongsh6/progress-engine.git
```

## 当前推进入口

当前状态判断以 `.progress/state/project_state.yaml`、`.progress/ledger/project-ledger.md` 和 State Delta Proposal 为准。常用本地观察入口：

```bash
PYTHONPATH=src python3 -m progress_engine assess
PYTHONPATH=src python3 -m progress_engine target list
PYTHONPATH=src python3 -m progress_engine intervention list
PYTHONPATH=src python3 -m progress_engine event list
```

Project State 只能通过 Evidence、Verification、State Delta Proposal 和 gate 流程更新；不要把 CLI 输出或文档改动直接视为状态已 apply。

## 当前状态原则

- 项目状态是核心事实；任务只是推动状态变化的手段。
- 每个推进动作必须服务于一个目标状态。
- 每个 Run 必须输出 Evidence 和 State Delta Proposal。
- Executor 不能自证完成；Verifier 必须独立验证。
- 一个推进动作使用一个 Fresh Context；不把长对话作为长期记忆。
