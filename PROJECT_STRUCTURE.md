# Project Structure

本版将原始策划书包重组为更接近软件项目仓库的结构，目标是让文档、协议、模板、图示和审查报告各归其位。

## 顶层文件

| 文件 | 作用 |
|---|---|
| `README.md` | 项目入口、核心定义、阅读顺序。 |
| `PROJECT_BRIEF.md` | 项目摘要，适合快速恢复上下文。 |
| `INDEX.md` | 所有章节、模板和报告的索引。 |
| `PROJECT_STRUCTURE.md` | 当前目录结构说明。 |
| `CHANGELOG.md` | 版本修正记录。 |

## 目录结构

```text
ProgressEngine/
  README.md
  PROJECT_BRIEF.md
  PROJECT_STRUCTURE.md
  CHANGELOG.md
  INDEX.md
  dist/
    ProgressEngine_Project_Plan_full.md
    ProgressEngine_Project_Plan_full.html
  docs/
    00-overview/
    01-state-engine/
    02-bootstrap-workflows/
    03-system-design/
    04-protocols/
    05-delivery/
    06-business-reference/
  templates/
    state/
    execution/
    verification/
    governance/
  diagrams/
  reports/
    self-check/
  assets/
```

## 为什么这样组织

1. **把可阅读成品与源文档分离。** `dist/` 放完整策划书，`docs/` 放可维护章节。
2. **把方法论和协议分离。** 方法论在 `docs/00-overview`，执行协议集中在 `docs/04-protocols`。
3. **把模板作为实现输入。** `templates/` 按状态、执行、验证和治理分组，便于后续转成 schema 或 CLI 生成物。
4. **把审查报告独立归档。** `reports/self-check` 保存自检和版本修正记录，不混入产品规格。
5. **文件名使用 ASCII。** 避免不同系统解压时出现中文文件名编码问题。

## 当前代码结构

代码实现已经按 v0.1 CLI-first 路线落入 `src/` 和 `tests/`：

```text
src/
  progress_engine/
    assessment/
    deltas/
    events/
    evidence/
    gaps/
    init/
    intake/
    interventions/
    runs/
    state/
    targets/
    verification/
    cli.py
tests/
  fixtures/
schemas/
pyproject.toml
```

当前实现仍保持小切片策略：优先提供本地 CLI、`.progress/` 对象读取、受控 bootstrap 写入和仓库质量检查，不引入 Web UI、模型 API 或外部 agent 编排。

## Repo-ready v5 增补结构

本版在策划书结构基础上增加了更接近真实 GitHub 项目的内容：

```text
.github/
  ISSUE_TEMPLATE/          # State Gap / Target State / Intervention / Change Event / Verification Gap
  workflows/docs-check.yml # 基础文档和 YAML 检查
  pull_request_template.md

.progress/
  state/                   # 当前项目状态
  gaps/                    # 状态缺口
  targets/                 # 目标状态
  interventions/           # 推进动作
  events/                  # Change Event
  runs/                    # Run 记录
  evidence/                # Evidence
  deltas/                  # State Delta Proposal
  ledger/                  # 风险、决策、假设等账本
  context_capsules/        # Fresh Context Capsule

scripts/
  check_repo.py            # 基础自检
  bootstrap_local_repo.sh  # 本地导入远程仓库辅助脚本

src/                     # CLI / 核心代码实现
tests/                   # pytest 测试与 fixture
schemas/                 # 后续 schema 实现位置
```

当前仓库已经从“项目策划书”推进到“可协作、可审查、可继续实施的 CLI-first 项目状态”。
