# v3 版本修正清单

本版在 v2 基础上做了以下补强：

| 类别 | 修正 |
|---|---|
| CLI 闭环 | `progress update` 改为 `progress state refresh`，避免与 `delta apply` 重叠 |
| 成熟度模型 | 成熟度矩阵补充 `seed`，并单独说明 `stale / reopened / superseded / blocked` |
| State Delta | 补充 `verification_id`、`proposed_at`、`gate`、`apply`、`rollback_delta_id` |
| Change Event | 补充 artifact effect、invalidated evidence、propagation 字段 |
| Intervention | 补充 `expected_state_delta` 与 `verification_policy` |
| 验证边界 | 明确 `verify` 只生成 proposal，`delta apply` 才能修改 Project State |
| 自检机制 | 新增 `docs/22_自检协议与开放缺口.md` 与 `v3_自检与修正报告.md` |

本版仍不声称 100% 无缺陷，只声明按当前检查协议未发现阻断级问题。
