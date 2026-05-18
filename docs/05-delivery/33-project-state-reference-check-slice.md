# Project State Reference Check Slice

本文定义 `IV-0026: Define next progress object quality slice` 的实现切片。它暂停继续扩展 CLI 命令面，先增强 `.progress` 账本自身的一致性检查。

## 1. 切片结论

下一条 quality slice 选择：

```bash
python3 scripts/check_repo.py
```

增强点限定为：

```text
Project State reference integrity
```

也就是让 `scripts/check_repo.py` 校验 `.progress/state/project_state.yaml` 中的以下引用：

- `open_state_gaps` 中每个 gap id 必须能解析到唯一 `.progress/gaps/{id}-*.yaml` 文件。
- `aim_of_next_state` 中每个 target id 必须能解析到唯一 `.progress/targets/{id}-*.yaml` 文件。

选择它的原因：

- 只读 CLI 已经依赖这些引用读取 gap 和 target；repo check 应提前发现账本漂移。
- 这是 `.progress` 对象语义一致性的最小增强，不需要完整 schema engine。
- 该检查只读，不修改 `.progress/`，也不自动修复对象。
- 它直接收敛 `SG-0003` 的对象质量 gate，而不扩大产品功能面。

## 2. 用户路径

目标用户在仓库根目录运行：

```bash
python3 scripts/check_repo.py
```

期望输出在原有检查基础上新增一条通过信息，例如：

```text
[OK] project state references passed
```

如果 `project_state.yaml` 声明了不存在或重复匹配的 gap / target id，命令返回非零退出码并打印清晰错误。

## 3. 输入、输出和状态影响

输入：

- `.progress/state/project_state.yaml`
- `.progress/gaps/*.yaml`
- `.progress/targets/*.yaml`

输出：

- stdout 的 `[OK] project state references passed`。
- 失败时 stdout 的 `[FAIL] ...` 说明，沿用现有 `scripts/check_repo.py` 风格。
- process exit code：
  - `0`：引用解析成功。
  - `1`：project state 缺少必要引用字段、引用值类型错误、引用目标缺失或重复匹配。

状态影响：

- 不创建、修改或删除 `.progress/` 下任何文件。
- 不修改 Project State。
- 不生成 Evidence 或 State Delta Proposal。
- 不执行 CLI 业务命令。

## 4. 实现文件边界

下一轮 implementation intervention 只允许触碰以下代码边界：

```text
scripts/check_repo.py
tests/test_check_repo.py
```

必要时可以小幅调整 `src/progress_engine/README.md` 或 `docs/05-delivery/33-project-state-reference-check-slice.md` 的描述，但不得借机实现完整 schema validation engine、自动修复或 CLI 写操作。

## 5. 最小行为规则

- 继续使用 Python 标准库为主，复用现有 PyYAML 可选加载路径。
- 如果 PyYAML 不可用，沿用现有策略跳过 YAML 依赖的 `.progress` 对象检查。
- 默认从仓库根目录解析 `.progress/state/project_state.yaml`。
- `open_state_gaps` 必须是 list，元素必须是非空 string。
- `aim_of_next_state` 必须是 list，元素必须是非空 string。
- 每个 gap id 必须唯一匹配 `.progress/gaps/{id}-*.yaml`。
- 每个 target id 必须唯一匹配 `.progress/targets/{id}-*.yaml`。
- 失败信息必须包含具体字段名和 id，不能只给笼统失败。

## 6. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-QUAL-001-01 | `python3 scripts/check_repo.py` 校验 Project State 的 `open_state_gaps` 引用，并在所有 gap 文件存在且唯一时通过。 |
| AC-QUAL-001-02 | `python3 scripts/check_repo.py` 校验 Project State 的 `aim_of_next_state` 引用，并在所有 target 文件存在且唯一时通过。 |
| AC-QUAL-001-03 | 缺少 gap 或 target 文件时返回非零退出码并输出包含字段名和 id 的错误。 |
| AC-QUAL-001-04 | 引用字段不是 list 或元素不是非空 string 时返回非零退出码并输出清晰错误。 |
| AC-QUAL-001-05 | pytest 覆盖成功路径、缺 gap、缺 target、引用字段类型错误和引用元素类型错误。 |
| AC-QUAL-001-06 | `python3 scripts/check_repo.py` 仍通过，并保留 required paths、YAML、JSONL、Markdown local links 和 `.progress` 对象最小字段检查。 |

## 7. Evidence Required

下一轮实现完成后，Evidence 至少包含：

- `python3 -m pytest tests/test_check_repo.py` 命令结果。
- `python3 -m pytest` 命令结果。
- `python3 scripts/check_repo.py` 命令结果，包含新增 project state reference 检查。
- git diff 摘要，证明只触碰允许的文件边界。
- 明确声明检查只读，不修改 `.progress/`。

## 8. Out of Scope

本切片明确不做：

- 完整 YAML schema validation engine。
- 自动修复 `.progress` 对象。
- 校验所有 evidence_refs、run refs、delta refs 或 Markdown 引用语义。
- `progress state refresh`。
- `progress delta apply`、reject 或 rollback。
- 生成 Evidence / State Delta Proposal 的业务命令。
- 模型 API、Web UI 或外部 agent 调用。

## 9. 下一步 Intervention

本切片被 human gate 接受后，下一步应创建并执行：

```text
IV-0027: Implement project state reference check slice
```

`IV-0027` 的目标不是“实现完整账本校验器”，而是只让 `scripts/check_repo.py` 发现 Project State 中 open gap 和 next target 引用漂移。
