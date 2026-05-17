# v3 自检与修正报告

## 1. 自检结论

v3 已按以下维度重复检查：

1. 愿景是否偏离。
2. Project State 是否仍是核心对象。
3. CLI 命令是否闭环。
4. 模板与正文是否一致。
5. State Delta 是否防止状态污染。
6. Change Event 是否支持螺旋推进。
7. Fresh Context 是否支持上下文切断。
8. Evidence Verifier 是否防止假完成。
9. 非代码产物是否避免自证循环。
10. Guarded Spiral 是否有自动化边界。

结论：没有发现阻断级缺陷；发现并修复了若干高/中优先级不一致。

## 2. 已修复问题

| 问题 | 修复 |
|---|---|
| `progress update` 与 `delta apply` 语义重叠 | 改为 `progress state refresh`，状态写入只由 `delta apply` 发生 |
| 成熟度枚举有 `seed`，矩阵无 `seed` | 成熟度矩阵增加 `seed` 列 |
| stale/reopened/superseded/blocked 未解释清楚 | 增加异常与治理状态说明 |
| State Delta 缺少 proposal/apply/rollback 元数据 | 增加 verification_id、proposed_at、gate、apply、rollback_delta_id |
| Change Event 模板缺少传播信息 | 增加 artifact effect、invalidates evidence、propagation |
| `verify` 与状态更新边界不够硬 | 明确 verify 只生成 proposal，delta apply 才写状态 |
| Intervention 模板对预期 State Delta 表达不足 | 增加 expected_state_delta 与 verification_policy |
| 状态转移缺少 stale / needs_review / reopened | Intervention 状态转移补充治理状态 |

## 3. 未承诺项

本报告不承诺 100% 无缺陷。它承诺的是：按当前检查协议，未发现新的阻断级问题；剩余不确定性已记录在 `docs/22_自检协议与开放缺口.md`。
