# 工作流与典型场景

## 1. 场景一：从 0 创建项目

```text
用户输入意图
  ↓
progress init
  ↓
progress intake
  ↓
角色流水线生成第一版 artifacts
  ↓
progress assess
  ↓
progress target suggest
  ↓
生成第一个 Target State
```

示例：

```bash
progress init --project my-tool
progress intake --from intent.md
progress assess
progress target suggest
```

输出不是任务池，而是：

```text
当前项目状态
主要状态缺口
推荐目标状态
建议推进动作
```

## 2. 场景二：产品状态不清，阻止继续编码

状态：

```text
Implementation ready tasks exist, but Product State is weak.
```

系统行为：

```text
不继续执行代码任务
  ↓
推荐产品澄清 Target State
  ↓
生成 product_clarification Intervention
```

## 3. 场景三：执行中发现架构缺口

执行 `IV-008 Implement context capsule generator` 时发现：

```text
artifact priority rules missing
```

系统行为：

```text
生成 EVT-002 implementation_finding
  ↓
technical_design reopened
  ↓
IV-008 blocked
  ↓
生成 TS-010 artifact priority rules accepted
  ↓
生成 IV-020 define artifact priority rules
```

这是正常的螺旋推进，不是失败。

## 4. 场景四：AI 假完成被拦截

Executor 输出：

```text
功能已经基本完成，后续可以补异常路径。
```

Verifier 检测：

```text
missing acceptance mapping
silent deferral detected
error path untested
```

结果：

```text
verification: fail
state_delta: not proposed
new intervention: IV-021 add error-path tests
```

## 5. 场景五：非代码产物验证

用户更新 PRD。

系统不直接升级 Product State，而是：

```text
PRD artifact exists
  ↓
Product Checklist
  ↓
Product Critic Review
  ↓
State Delta Proposal
  ↓
Apply
```

如果成功指标仍然不清楚，则 Product State 保持 reviewed / partial，不升级到 accepted。

## 6. 场景六：上下文超预算

Intervention 需要读取 30 个文件和 15 条验收标准。

系统输出：

```text
Context budget exceeded.
This intervention must be split.
```

生成：

```text
META intervention: split IV-030
```

## 7. 场景七：发布前状态评估

发布前运行：

```bash
progress assess --mode release
```

系统检查：

- Implementation 是否 validated。
- Quality 是否 accepted/validated。
- Delivery 是否 reviewed/accepted。
- Known gaps 是否存在 release blocker。
- Rollback 是否定义。
- Feedback channel 是否存在。

## 8. 场景八：持续螺旋推进

```bash
progress spiral --mode guarded --max-runs 3
```

每轮：

```text
assess
select target state
plan intervention
build fresh capsule
execute / prompt-only
verify
propose state delta
apply if allowed
reassess
```

如果任何一轮产生 high severity event，spiral 停止，等待人工 gate。
