# 术语表

## ProgressEngine

持续推进项目状态的 AI 软件工程系统。

## Project State

当前项目真实状态，由多个维度组成。

## State Dimension

项目状态的一个维度，例如 Product、Architecture、Quality。

## Maturity

状态维度的可信成熟度，例如 drafted、reviewed、accepted、validated。

## State Gap

当前项目状态与期望状态之间的缺口。

## Target State

下一步希望项目达到的状态。

## Intervention

为了推动状态变化而设计的推进动作。Task 是其可执行形态之一。

## Run

一次隔离上下文执行。

## Fresh Context

为单个 Intervention 重新生成的独立上下文空间。

## Context Capsule

用于执行一个 Intervention 的最小充分上下文包。

## Evidence

证明状态变化的证据。

## Evidence Verifier

独立验证 Evidence 是否支持状态变化的模块或角色。

## State Delta

状态变化提案。只有通过验证和 gate 后才能 apply。

## Change Event

项目推进中产生的变化事件，例如实现发现、验证失败、用户反馈、架构冲突。

## Artifact

项目事实源文件，例如 PRD、技术设计、质量计划。

## Ledger

项目长期账本，包括状态、决策、风险、证据、反馈。

## Guarded Spiral

带人工 gate 和自动化边界的连续推进模式。

## No Silent Deferral

禁止口头延期；任何延期必须转成结构化 gap、event 或 intervention。
