# CLI 与交互设计

## 1. CLI 目标

CLI 是 ProgressEngine MVP 的主要入口。它不应首先成为 AI 执行器，而应成为项目状态推进工具。

## 2. 命令总览

```bash
progress init
progress intake
progress assess
progress gaps
progress target
progress plan
progress capsule
progress run
progress evidence
progress verify
progress delta
progress event
progress state
progress spiral
```

## 3. 命令语义

### 3.1 `progress init`

初始化 `.progress/` 目录。

```bash
progress init --project progressengine
```

生成：

```text
.progress/project.yaml
.progress/state/project_state.yaml
.progress/policies/*
.progress/artifacts/*
```

### 3.2 `progress intake`

捕获初始意图。

```bash
progress intake --from intent.md
```

输出：

```text
.progress/artifacts/intent.md
.progress/state/project_state.yaml
```

### 3.3 `progress assess`

评估当前项目真实状态。

```bash
progress assess
```

输出：

```text
Project State Summary
State Maturity by Dimension
Detected Gaps
Stale Claims
Recommended Next Target Candidates
```

### 3.4 `progress gaps`

列出状态缺口。

```bash
progress gaps list
progress gaps show G-001
```

### 3.5 `progress target`

推荐目标状态。

```bash
progress target suggest
progress target approve TS-001
```

注意：`target` 不执行动作，只处理目标状态。

### 3.6 `progress plan`

把目标状态转成推进动作。

```bash
progress plan --target TS-001
```

输出：

```text
Intervention Proposal IV-001
```

### 3.7 `progress capsule`

生成 Fresh Context Capsule。

```bash
progress capsule --intervention IV-001
```

输出：

```text
.progress/runs/RUN-001/context_capsule.md
```

### 3.8 `progress run`

管理 Run 生命周期。

```bash
progress run start --intervention IV-001 --mode prompt-only
progress run close RUN-001
```

MVP 第一版中，`run start` 可以只生成上下文包，不直接调用模型。

### 3.9 `progress evidence`

录入证据。

```bash
progress evidence add --run RUN-001 --file evidence.yaml
progress evidence list --run RUN-001
```

### 3.10 `progress verify`

独立验证结果。

```bash
progress verify --run RUN-001
```

输出：

```text
verification.md
state_delta_proposal.yaml
```

### 3.11 `progress delta`

管理 State Delta。

```bash
progress delta review SD-001
progress delta apply SD-001
progress delta reject SD-001
progress delta rollback SD-001
```

### 3.12 `progress event`

管理 Change Event。

```bash
progress event add --type implementation_finding
progress event list
progress event show EVT-001
```

### 3.13 `progress state`

查看、刷新和回放项目状态。`delta apply` 负责写入状态；`state refresh` 负责重新评估派生缺口和状态摘要。

```bash
progress state show
progress state history
progress state refresh --after-delta SD-001
```

### 3.14 `progress spiral`

执行受控螺旋推进。

```bash
progress spiral --mode guarded --max-runs 3
```

每轮必须 fresh context。

## 4. 标准推进命令序列

```bash
progress assess
progress target suggest
progress target approve TS-001
progress plan --target TS-001
progress capsule --intervention IV-001
progress run start --intervention IV-001 --mode prompt-only
# 用户或 AI 执行
progress evidence add --run RUN-001 --file evidence.yaml
progress verify --run RUN-001
progress delta review SD-001
progress delta apply SD-001
progress state refresh --after-delta SD-001
progress assess
```

## 5. CLI 输出原则

- 输出当前状态，而不是只输出命令结果。
- 每个命令都说明下一步建议。
- 明确区分 proposal 和 applied。
- 不用“完成”描述未验证结果。
- 失败时给出 repair / gap / event 建议。

## 6. 交互示例

```text
$ progress assess

Project: progressengine
State version: PS-0005

Dimensions:
- Intent: accepted / complete
- Product: reviewed / partial
- UX: drafted / partial
- Architecture: drafted / in_progress
- Implementation: unknown / not_started
- Quality: drafted / partial

Top Gaps:
1. G-003 Product success metrics are weak.
2. G-005 Architecture adapter boundary unclear.
3. G-007 Quality evidence rules incomplete.

Recommended Target:
TS-003 Accept measurable MVP success metrics.
```
