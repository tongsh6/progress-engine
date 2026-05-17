# 目标状态选择策略

## 1. 为什么需要目标状态选择策略

如果系统只根据已有任务池选择任务，就会退化成任务工具。ProgressEngine 每轮必须先判断：

```text
当前最有价值的项目状态变化是什么？
```

这需要一个可解释的目标状态选择策略。

## 2. 从 State Gap 到 Target State

流程：

```text
Project State Assessment
  ↓
State Gaps
  ↓
Gap Scoring
  ↓
Target State Candidate
  ↓
Target State Selection
  ↓
Intervention Planning
```

## 3. State Gap 数据结构

```yaml
gap:
  id: G-001
  dimension: product
  current_state: "Product scope is drafted but not reviewed."
  desired_state: "MVP scope accepted with explicit non-goals and success metrics."
  severity: high
  evidence:
    - artifacts/prd.md
  impact:
    - "Implementation tasks may encode wrong scope."
    - "Quality acceptance criteria cannot be finalized."
```

## 4. 评分模型

每个目标状态候选使用 0-5 分评分：

| 因子 | 说明 |
|---|---|
| risk_reduction | 是否降低关键风险 |
| downstream_unlock | 是否解锁后续工作 |
| user_value_proximity | 是否更接近用户价值 |
| quality_confidence_gain | 是否提升质量信心 |
| prevents_wrong_work | 是否避免在错误方向上继续实现 |
| implementation_capability_gain | 是否增加可运行能力 |
| knowledge_clarity_gain | 是否提升项目可追溯性 |
| effort | 预计成本，越高越扣分 |
| reversibility | 是否容易回退，越容易越加分 |
| automation_suitability | 是否适合自动或半自动执行 |

推荐公式：

```text
score =
  risk_reduction
+ downstream_unlock
+ user_value_proximity
+ quality_confidence_gain
+ prevents_wrong_work
+ implementation_capability_gain
+ knowledge_clarity_gain
+ reversibility
+ automation_suitability
- effort
```

## 5. 选择策略

### 5.1 Explore 模式

适合项目早期。

优先级：

```text
降低最大不确定性 > 增加代码量
```

常见目标状态：

- Intent accepted。
- Product scope reviewed。
- Architecture options reviewed。
- Quality plan drafted。

### 5.2 Converge 模式

适合从概念收敛到 MVP。

优先级：

```text
明确范围 > 明确架构 > 明确验收 > 再实现
```

### 5.3 Build 模式

适合主要方向已定后。

优先级：

```text
增加可运行能力 > 补文档
```

但如果实现中发现设计缺口，必须回退到对应状态维度。

### 5.4 Harden 模式

适合发布前。

优先级：

```text
质量证据 > 新功能
```

### 5.5 Release 模式

适合交付阶段。

优先级：

```text
部署、回滚、监控、已知问题、反馈入口
```

## 6. Target State 模板

```yaml
target_state:
  id: TS-001
  dimension: product
  from:
    maturity: drafted
    summary: "PRD exists but scope is not reviewed."
  to:
    maturity: accepted
    summary: "MVP scope accepted with explicit non-goals and success metrics."
  why_now:
    - "Implementation tasks depend on stable scope."
    - "Avoid building features outside MVP."
  score:
    risk_reduction: 4
    downstream_unlock: 5
    user_value_proximity: 4
    quality_confidence_gain: 3
    prevents_wrong_work: 5
    effort: 2
  required_interventions:
    - IV-001
  gate_required: true
```

## 7. 输出要求

`progress target` 不应只输出一个答案，而应输出：

```text
Top 3 Target State Candidates
  - 推荐目标状态
  - 为什么现在做
  - 不做的风险
  - 需要的人类确认
  - 对应推进动作建议
```

## 8. 禁止规则

- 不允许直接从状态缺口跳到代码实现。
- 不允许忽略高风险状态缺口继续刷实现任务。
- 不允许选择无法验证的目标状态。
- 不允许选择没有 State Delta 定义的目标状态。
