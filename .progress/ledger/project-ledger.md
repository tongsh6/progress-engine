# ProgressEngine 项目推进台账

本台账记录项目状态如何被推进。它不是任务列表，也不是完成清单；每条记录都必须说明目标状态、证据、State Delta 和 remaining gaps。

## 2026-05-17

### IV-0002: Freeze v0.1 MVP boundary

- Target State：`TS-0002: v0.1 MVP boundary accepted`
- 主维度：product
- 结果：已通过 human gate apply，product maturity 从 `reviewed` 推进到 `accepted`
- Evidence：`.progress/evidence/EV-0002-v0.1-mvp-boundary.yaml`
- State Delta：`.progress/deltas/SDP-0002-v0.1-mvp-boundary.yaml`
- 状态历史：`PS-0002`
- 主要产物：`docs/05-delivery/16-mvp-scope-and-roadmap.md`
- Remaining gaps：
  - `SG-0002`: v0.1 真实试点项目尚未选定
  - `SG-0003`: `.progress` 对象 schema、命名约定和必填字段检查仍偏弱

### IV-0003: Select v0.1 technical stack

- Target State：`TS-0003: v0.1 technical stack selected`
- 主维度：architecture
- 结果：已通过 human gate apply，architecture maturity 从 `reviewed` 推进到 `accepted`
- 技术栈结论：Python 3.11+、stdlib-first `argparse` CLI、YAML / Markdown / JSONL repo-native 状态账本
- Evidence：`.progress/evidence/EV-0003-v0.1-tech-stack.yaml`
- State Delta：`.progress/deltas/SDP-0003-v0.1-tech-stack.yaml`
- 状态历史：`PS-0003`
- 主要产物：
  - `docs/03-system-design/06-system-architecture-and-module-boundaries.md`
  - `decisions/ADR-0001-v0.1-tech-stack.md`
- Remaining gaps：
  - `SG-0003`: 完整 schema 校验仍未实现
  - `SG-0004`: 第一批 CLI implementation slice 尚未定义

### IV-0004: Strengthen docs and YAML check

- Target State：`TS-0004: minimum docs and YAML checks working`
- 主维度：quality
- 结果：按 `auto_allowed` policy apply，quality maturity 从 `drafted` 推进到 `reviewed`
- Evidence：`.progress/evidence/EV-0004-docs-and-yaml-check.yaml`
- State Delta：`.progress/deltas/SDP-0004-docs-and-yaml-check.yaml`
- 状态历史：`PS-0004`
- 主要产物：`scripts/check_repo.py`
- 新增质量门禁：
  - required paths 检查
  - YAML parse 检查
  - JSONL parse 检查
  - Markdown local links 检查
  - `.progress` 对象最小必填字段检查
  - `.progress` 对象文件名与 id 前缀一致性检查
- 检查结果：

```text
[OK] required paths exist
[OK] YAML parse passed for 42 files
[OK] JSONL parse passed for 2 files
[OK] local Markdown links passed
[OK] .progress object checks passed for 24 files
```

## 当前状态

- product：`accepted`
- architecture：`accepted`
- quality：`reviewed`
- implementation：`not_started`

## 下一步推荐

- `TS-0006: first Python CLI implementation slice defined`
- `IV-0006: Define first Python CLI implementation slice`

下一步仍应先冻结第一个最小实现切片，再进入代码实现，避免从技术栈选择直接膨胀成完整 CLI。
