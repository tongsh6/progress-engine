# Index

## 文档章节

### Overview

- [执行摘要](docs/00-overview/00-executive-summary.md)
- [愿景定位与问题定义](docs/00-overview/01-vision-and-problem.md)
- [核心方法论：持续推进项目状态](docs/00-overview/02-core-methodology-state-driven-progress.md)

### State Engine

- [项目状态模型与成熟度矩阵](docs/01-state-engine/03-project-state-model-and-maturity-matrix.md)
- [目标状态选择策略](docs/01-state-engine/04-target-state-selection-strategy.md)
- [核心对象与数据模型](docs/01-state-engine/07-core-objects-and-data-model.md)

### Bootstrap & Workflows

- [从 0 启动角色流水线](docs/02-bootstrap-workflows/05-zero-to-project-role-pipeline.md)
- [工作流与典型场景](docs/02-bootstrap-workflows/15-workflows-and-scenarios.md)

### System Design

- [系统架构与模块边界](docs/03-system-design/06-system-architecture-and-module-boundaries.md)
- [CLI 与交互设计](docs/03-system-design/14-cli-and-interaction-design.md)

### Protocols

- [Intervention 推进动作与执行协议](docs/04-protocols/08-intervention-execution-protocol.md)
- [Fresh Context 上下文隔离协议](docs/04-protocols/09-fresh-context-isolation-protocol.md)
- [Evidence Verifier 证据验证协议](docs/04-protocols/10-evidence-verifier-protocol.md)
- [非代码产物验证协议](docs/04-protocols/11-non-code-artifact-verification-protocol.md)
- [Change Event 影响分析与失效传播](docs/04-protocols/12-change-event-impact-and-invalidation.md)
- [State Delta 提案、应用与回滚协议](docs/04-protocols/13-state-delta-proposal-apply-rollback.md)
- [Guarded Spiral 自动化边界](docs/04-protocols/18-guarded-spiral-automation-boundary.md)

### Delivery

- [MVP 范围与路线图](docs/05-delivery/16-mvp-scope-and-roadmap.md)
- [质量体系与风险管理](docs/05-delivery/17-quality-system-and-risk-management.md)
- [实施计划与推进动作清单](docs/05-delivery/19-implementation-plan-and-action-list.md)

### Business & Reference

- [运营方式、商业化与后续演进](docs/06-business-reference/20-operations-commercialization-and-evolution.md)
- [术语表](docs/06-business-reference/21-glossary.md)
- [自检协议与开放缺口](docs/06-business-reference/22-self-check-protocol-and-open-gaps.md)

## 模板

### templates/state

- [project_state.yaml](templates/state/project_state.yaml)
- [state_delta.yaml](templates/state/state_delta.yaml)
- [state_gap.yaml](templates/state/state_gap.yaml)
- [target_state.yaml](templates/state/target_state.yaml)

### templates/execution

- [context_capsule.md](templates/execution/context_capsule.md)
- [intervention.yaml](templates/execution/intervention.yaml)
- [run.yaml](templates/execution/run.yaml)

### templates/verification

- [artifact_review_checklist.yaml](templates/verification/artifact_review_checklist.yaml)
- [evidence.yaml](templates/verification/evidence.yaml)
- [outcome_scoring.yaml](templates/verification/outcome_scoring.yaml)

### templates/governance

- [automation_policy.yaml](templates/governance/automation_policy.yaml)
- [change_event.yaml](templates/governance/change_event.yaml)

## 图示

- [progressengine_architecture.mmd](diagrams/progressengine_architecture.mmd)
- [progressengine_lifecycle.mmd](diagrams/progressengine_lifecycle.mmd)
- [state_dimensions.mmd](diagrams/state_dimensions.mmd)

## 报告

- [v3-revision-checklist.md](reports/self-check/v3-revision-checklist.md)
- [v3-self-check-report.md](reports/self-check/v3-self-check-report.md)