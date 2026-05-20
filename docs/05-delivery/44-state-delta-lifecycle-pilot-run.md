# State Delta Lifecycle Pilot Run

本文记录 `IV-0047: Run State Delta lifecycle pilot validation` 的执行结果。它把 `docs/05-delivery/43-state-delta-lifecycle-pilot.md` 中定义的 State Delta lifecycle 试点固化为 focused pytest。

## 1. 执行结论

新增测试：

```text
tests/test_state_delta_lifecycle_pilot.py
```

该测试在 pytest `tmp_path` 中复制 `tests/fixtures/minimal_progress_project/`，分别验证：

- `progress delta apply SDP-1002 --approved-by human_user`
- `progress state refresh --after-delta SDP-1002`
- `progress delta rollback SDP-1003 --approved-by human_user`
- `progress delta reject SDP-1004 --approved-by human_user --reason "..."`

## 2. 验证结果

```text
python3 -m pytest tests/test_state_delta_lifecycle_pilot.py
1 passed in 0.04s

python3 -m pytest
122 passed in 0.73s

python3 scripts/check_repo.py
[OK] required paths exist
[OK] YAML parse passed for 297 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 264 files
[OK] Project State reference checks passed
[OK] CLI status documentation checks passed
```

## 3. 分支断言

Apply + refresh 分支：

- `SDP-1002` apply 成功。
- Project State implementation maturity 更新为 `drafted`。
- state history 追加 `PS-1002 <- SDP-1002`。
- `state refresh --after-delta SDP-1002` 匹配 latest history。

Rollback 分支：

- `SDP-1003` rollback 成功。
- Project State 恢复为 rollback restore 指定的 seed 状态。
- state history 追加 `ROLLBACK-SDP-1003`。
- proposal status 更新为 `rolled_back`。

Reject 分支：

- `SDP-1004` reject 成功。
- proposal status 更新为 `rejected`，并记录 reason 和 previous_status。
- Project State 保持不变。
- state history 保持不变。

## 4. 产品结论

该 pilot 证明 v0.1 的 State Delta lifecycle 已具备本地可演示闭环：

```text
apply -> refresh -> rollback
reject un-applied proposal
```

本轮不声称完整产品达到 `validated`。原因是 delivery 仍为 `weak`：安装、发布、版本边界和用户上手路径尚未形成。

## 5. Remaining Gap

下一步应转向 delivery：

```text
SG-0038: v0.1 release readiness gap
```

目标不是继续增加 lifecycle CLI，而是定义 v0.1 本地发布 / 安装 / 使用入口，使已有状态引擎能被真实用户稳定试用。
