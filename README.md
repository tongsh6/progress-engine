# ProgressEngine

> **持续推进项目状态，而不是持续完成任务。**

ProgressEngine 是一个状态驱动的 AI 软件工程系统。它通过状态建模、目标状态规划、推进动作拆解、Fresh Context 隔离执行和 Evidence Verifier 证据验证，把模糊项目意图逐步推进为可用产品、工程资产和决策结果。

当前仓库处于 **project-state bootstrap** 阶段：已经具备项目策划书、方法论、协议、模板、初始 `.progress/` 状态账本和 GitHub 协作骨架；尚未进入 CLI 实现。

## 当前目标状态

```text
仓库从“只有远程空仓库”推进为“可协作、可审查、可继续实施的项目初始状态”。
```

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
  src/                     # 后续 CLI / 核心代码实现位置
  tests/                   # 后续测试位置
```

## 本地初始化建议

```bash
git clone git@github.com:tongsh6/progress-engine.git
cd progress-engine

# 将本包内容复制进仓库根目录后：
python3 scripts/check_repo.py

git add .
git commit -m "docs: bootstrap ProgressEngine project state"
git push origin main
```

如果使用 HTTPS：

```bash
git clone https://github.com/tongsh6/progress-engine.git
```

## 首批推进动作

`.progress/interventions/` 中已经给出第一批推进动作：

| ID | 目标 |
|---|---|
| `IV-0001` | 将 repo 初始化为可审查项目状态。 |
| `IV-0002` | 固化 v0.1 MVP 边界。 |
| `IV-0003` | 选择 v0.1 技术栈和 CLI 实现路径。 |
| `IV-0004` | 建立最小 schema / docs 自检能力。 |

## 当前状态原则

- 项目状态是核心事实；任务只是推动状态变化的手段。
- 每个推进动作必须服务于一个目标状态。
- 每个 Run 必须输出 Evidence 和 State Delta Proposal。
- Executor 不能自证完成；Verifier 必须独立验证。
- 一个推进动作使用一个 Fresh Context；不把长对话作为长期记忆。
