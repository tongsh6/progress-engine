# ProgressEngine

> **持续推进项目状态，而不是持续完成任务。**

ProgressEngine 是一个状态驱动的 AI 软件工程系统。它通过状态建模、目标状态规划、推进动作拆解、Fresh Context 隔离执行和 Evidence Verifier 证据验证，把模糊项目意图逐步推进为可用产品、工程资产和决策结果。

## 推荐入口

1. `PROJECT_BRIEF.md`：项目摘要和核心口径。
2. `dist/ProgressEngine_Project_Plan_full.md`：完整 Markdown 策划书。
3. `dist/ProgressEngine_Project_Plan_full.html`：完整 HTML 策划书。
4. `PROJECT_STRUCTURE.md`：本包目录结构与设计理由。
5. `INDEX.md`：分章节文档索引。

## 目录结构

```text
ProgressEngine/
  README.md
  PROJECT_BRIEF.md
  PROJECT_STRUCTURE.md
  CHANGELOG.md
  INDEX.md
  dist/
    ProgressEngine_Project_Plan_full.md
    ProgressEngine_Project_Plan_full.html
  docs/
    00-overview/
    01-state-engine/
    02-bootstrap-workflows/
    03-system-design/
    04-protocols/
    05-delivery/
    06-business-reference/
  templates/
    state/
    execution/
    verification/
    governance/
  diagrams/
  reports/
    self-check/
  assets/
```

## 阅读顺序

```text
PROJECT_BRIEF.md
  ↓
docs/00-overview/02-core-methodology-state-driven-progress.md
  ↓
docs/01-state-engine/03-project-state-model-and-maturity-matrix.md
  ↓
docs/02-bootstrap-workflows/05-zero-to-project-role-pipeline.md
  ↓
docs/04-protocols/09-fresh-context-isolation-protocol.md
  ↓
docs/04-protocols/10-evidence-verifier-protocol.md
  ↓
docs/05-delivery/16-mvp-scope-and-roadmap.md
```

## 包结构原则

- `docs/`：源文档，按产品、状态引擎、工作流、系统设计、协议、交付和参考分类。
- `templates/`：可被工具实现复用的 YAML / Markdown 模板。
- `diagrams/`：Mermaid 图示源文件。
- `reports/`：自检、修正和审查报告。
- `dist/`：面向阅读和分发的一体化文档。
- `assets/`：HTML 样式资源。

