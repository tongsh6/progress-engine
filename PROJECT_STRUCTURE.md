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

## 后续如果进入代码实现

可以在此结构基础上增加：

```text
src/
  progressengine/
    state/
    planning/
    execution/
    verification/
    ledger/
tests/
schemas/
pyproject.toml 或 package.json
```

当前包仍是项目策划书，不包含实现代码。
