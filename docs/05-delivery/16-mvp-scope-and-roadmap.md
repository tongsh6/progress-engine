# MVP 范围与路线图

## 1. MVP 定义

ProgressEngine MVP 的目标不是自动完成整个软件项目，而是证明：

```text
一个模糊项目意图可以被转化为可审查项目状态，
并通过目标状态、推进动作、隔离上下文、证据验证和 State Delta，
完成至少一轮真实的项目状态推进。
```

## 2. Must Have

### 2.1 Project State

- `.progress/` 初始化。
- Project State schema。
- 状态维度与成熟度矩阵。
- State Gap 记录。

### 2.2 从 0 启动

- intent intake。
- 角色流水线 prompt 模板。
- 初始 artifacts 生成。
- 初始 Project State 合成。

### 2.3 Target State

- gaps list。
- target suggest。
- target scoring。
- target approve。

### 2.4 Intervention

- Intervention schema。
- plan target to intervention。
- readiness check。

### 2.5 Fresh Context

- context capsule 生成。
- context budget 检查。
- prompt-only run start。

### 2.6 Evidence / Verification

- evidence add。
- acceptance mapping。
- verifier checklist。
- State Delta proposal。

### 2.7 State Delta

- delta apply。
- delta reject。
- delta rollback。
- state history。

### 2.8 Change Event

- event add/list/show。
- basic impact analysis。
- mark artifact stale/reopened。

## 3. Should Have

- Mermaid 图生成。
- 基础 TUI。
- Git diff 检查。
- 自动检测 stale interventions。
- shell-adapter 调用测试命令。
- markdown/html report。

## 4. Won’t Have

第一阶段不做：

- Web SaaS。
- 多用户权限。
- 实时 agent 编排。
- 自动调用所有模型。
- 自动发布生产环境。
- 全自动高风险架构决策。
- 复杂项目组合管理。

## 5. 版本路线图

### v0.1 — State Loop MVP

目标：跑通状态推进闭环。

功能：

```text
init / intake / assess / gaps / target / plan / capsule / evidence / verify / delta apply
```

成功标准：

```text
能从一个意图生成第一版 project state，并完成一轮 State Delta 应用。
```

### v0.2 — Bootstrap Role Pipeline

目标：强化从 0 启动。

功能：

- Product Lead Pass。
- Product Critic Pass。
- Tech Lead Pass。
- QA Lead Pass。
- State Synthesizer。

成功标准：

```text
能为新项目生成可审查 artifacts 和初始 target states。
```

### v0.3 — Change Event + Reassessment

目标：支持螺旋式回退。

功能：

- Change Event 捕获。
- 影响分析。
- stale/reopened 标记。
- intervention invalidation。

### v0.4 — Guarded Spiral

目标：连续推进，但每轮 fresh context。

功能：

```bash
progress spiral --mode guarded --max-runs N
```

### v1.0 — Adapter Integration

目标：连接外部 AI 执行工具。

支持：

- shell adapter。
- API adapter。
- GitHub/Codex/Claude Code 等执行接口。

## 6. MVP 验收标准

MVP 通过标准：

```text
1. 可以初始化新项目。
2. 可以记录原始意图。
3. 可以生成并评估 Project State。
4. 可以识别 State Gap。
5. 可以推荐 Target State。
6. 可以生成 Intervention。
7. 可以为 Intervention 生成 Context Capsule。
8. 可以收集 Evidence。
9. 可以独立 Verify。
10. 可以生成并应用 State Delta。
11. 可以在下一轮 assess 中看到状态变化。
```

## 7. 第一批推进动作

建议从这些动作开始实现：

```text
IV-001 Define project_state schema
IV-002 Implement progress init
IV-003 Implement intent intake
IV-004 Implement state assessment from static files
IV-005 Implement gap list
IV-006 Implement target scoring
IV-007 Implement intervention schema
IV-008 Implement context capsule generator
IV-009 Implement evidence schema
IV-010 Implement verifier checklist
IV-011 Implement state delta apply/rollback
```
