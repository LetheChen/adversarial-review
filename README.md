# Adversarial Review · 对抗性复核

> Send analysis / proposals / code changes to **independent reviewer perspectives** for adversarial (red-team) review — single-reviewer, multi-perspective, or N-round cross-examination until convergence. Uses **native subagents by default** (2–4 reviewers with *different evidence-gathering methods*), and falls back to **CLI subprocesses** (Claude Code / Codex CLI) for cross-harness or cross-model-family work. Produces a `REVIEW-` document.

> 把分析文档 / 方案 / 代码改动交给**多个独立审查视角**做对抗性审查（红队复核）—— 单审查者、多视角并行、N 轮交叉质询与可计算的收敛判定。**默认用原生 subagent**（2–4 家，**取证方法互不相同**），跨 harness / 需要跨模型家族时走 **CLI 子进程外部通道**（Claude Code / Codex CLI）。产出 `REVIEW-` 文档。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)
[![Skill Type](https://img.shields.io/badge/type-AI%20Agent%20Skill-green.svg)](#)

---

## English

### What is this?

A **Codex / Claude Code / Cursor skill** that turns "review this" into a structured adversarial review. Instead of trusting the model that wrote the doc, the skill dispatches the work to 2–4 **independent reviewer perspectives**, enforces file-based accounting, and supports N-round cross-examination until disagreements are resolved.

**Three core principles:**
1. **The file is the ledger (authoritative), the session is the accelerator.**
2. **Artifacts are the contract, the execution layer is pluggable** — native subagents by default, CLI subprocesses as fallback, mixable.
3. **Diversity comes from evidence-gathering methods, not from model families.**

### Why?

Because the model that wrote the document is the model most likely to **defend** it. And because "I asked another LLM and it agreed" is not actually a review. This skill forces:

- A **different** reviewer perspective — and a **different evidence-gathering method** per reviewer (static check / live execution / reverse-premise attack / edge-case hunt), so reviewers miss *different* things rather than converging on the same blind spot.
- **Independent** verification (the reviewer must open the file, not paraphrase it).
- **Accountability** (every claim is anchored to `file:line` + raw evidence + an evidence grade L4–L0).
- **Convergence** (N-round debate with explicit "maintain / revise / withdraw" on each contested point, stopped by *four computable metrics*, not by feel).

### What can it review?

Anything that lives in a git repository as a document or diff:

- Analysis reports / design docs / proposals
- Schema migrations / refactor plans
- Code changes (PR-equivalent)
- Cross-team business designs

### Quick start

This is a **skill** — install it under your Claude Code or Cursor skills directory, then trigger it with phrases like:

| Phrase | What happens |
|---|---|
| "Have Claude review this" | External channel: Claude Code CLI, 1 round |
| "Have Codex review this" | External channel: Codex CLI, 1 round |
| "Send to team review" | Claude + Codex — cross-model-family diversity |
| "Spawn a few subagents to review this" | **Default** — 3 native subagents, 3 different methods, 1 round |
| "Mixed review (both subagents and cross-family)" | Native reviewers (N rounds) + 1 external-channel round |
| "Team review for 3 rounds" | R1 independent + 2 rounds of cross-examination |
| "Red-team this analysis" | Same as default multi-perspective review (alias) |

### File map

| When you need | Read this |
|---|---|
| The full methodology, decision rules, execution steps | [`SKILL.md`](SKILL.md) |
| R1 red-team prompt, Rk cross-exam brief, the **evidence-gathering method catalog (S1–S4)**, and the abort-round audit checklist | [`assets/prompts.md`](assets/prompts.md) |
| Every pitfall — CLI channel **and** native subagent (concurrency, `fork_context`, cleanup) | [`references/pitfalls.md`](references/pitfalls.md) |
| Extract session/thread IDs, detect same-source model, compute cost | [`scripts/extract_session_ids.py`](scripts/extract_session_ids.py) |
| The end-to-end process as an interactive diagram (roles as columns, time downward) | [`assets/business-process.html`](assets/business-process.html) · [`preview`](assets/business-process.preview.png) |

### Requirements

- **For the default (native subagent) path**: a harness that provides a subagent / sub-task capability. No CLI required.
- **For the external-channel path**: a local install of [Claude Code CLI](https://docs.claude.com/en/docs/claude-code) **and/or** [OpenAI Codex CLI](https://github.com/openai/codex), runnable in the target repository's working directory.
- Python 3.8+ (only for the session-id extractor script, external channel only).

### License

[MIT](LICENSE) — Copyright (c) 2026 LetheChen &lt;lethe@chen.com&gt;.

### Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Bug reports, new prompt templates, and worked examples are especially welcome.

### Security

See [`SECURITY.md`](SECURITY.md) — please report vulnerabilities privately, not via public issues.

---

## 中文

### 这是什么？

一个 **Codex / Claude Code / Cursor skill**，把"审一下"变成结构化的对抗性审查。不信任写出文档的那个模型，让 skill 把工作分发给 **2–4 个独立审查视角**，强制文件账本，支持 N 轮交叉质询直到分歧收敛。

**三条核心设计原则：**
1. **文件是账本（权威），会话是加速器**（省钱）
2. **产物是契约，执行层可插拔**（通用）—— 默认原生 subagent，兜底 CLI 子进程，可混用
3. **多样性来自取证方法，不来自模型家族**（有效）

### 为什么要这样？

因为写出文档的那个模型最有可能**维护**它。因为"我又问了个 LLM 它同意"根本不是审查。这个 skill 强制：

- **不同的**审查视角，以及**互不相同的取证方法**（静态核验 / 实测执行 / 反向重建 / 边界专项）—— 让他们漏掉的东西不一样，而不是撞进同一个盲区
- **独立的**核验（审查者必须打开文件，不能只复述）
- **可追溯的**证据（每条断言锚定到 `文件:行号` + 原文片段，并标证据等级 L4–L0）
- **收敛的**讨论（N 轮辩论，对每个争议点显式"维持/修正/撤回"，停机由**四个可计算指标**决定，不靠感觉）

### 能审什么？

仓库里以文档或 diff 形式存在的任何东西：

- 分析报告 / 设计文档 / 方案
- 数据库迁移 / 重构计划
- 代码改动（PR 等价物）
- 跨团队业务设计

### 快速开始

这是一个 **skill** —— 安装到你的 Claude Code 或 Cursor skills 目录后，用下面这类话触发：

| 用户说法 | 行为 |
|---|---|
| "让 claude code 审核" | 外部通道：Claude Code CLI，1 轮 |
| "让 codex 审核" | 外部通道：Codex CLI，1 轮 |
| "发给团队审核" | Claude + Codex，跨模型家族多样性 |
| "起几个 subagent 审一下" | **默认** —— 3 个原生 subagent，3 种取证方法，1 轮 |
| "综合审一下（既要 subagent 又要跨家族）" | 原生跑 N 轮 + 外轨补 1 轮 |
| "团队审核 3 轮" | R1 独立 + 2 轮交叉质询 |
| "红队审一下" | 同默认多视角审查（别名） |

### 文件地图

| 你需要 | 读这个 |
|---|---|
| 完整方法论、决策规则、执行步骤 | [`SKILL.md`](SKILL.md) |
| R1 红队 prompt、Rk 交叉质询 brief、**取证方法清单（S1–S4）**、中止轮自查表 | [`assets/prompts.md`](assets/prompts.md) |
| 全部坑点 —— CLI 通道**与**原生 subagent（并发上限、`fork_context`、收尾清理） | [`references/pitfalls.md`](references/pitfalls.md) |
| 提取 session/thread id、检测同源模型、算账 | [`scripts/extract_session_ids.py`](scripts/extract_session_ids.py) |
| 端到端流程交互图（角色竖排成列、时间自上而下） | [`assets/business-process.html`](assets/business-process.html) · [`预览图`](assets/business-process.preview.png) |

### 依赖

- **默认（原生 subagent）路径**：需要宿主提供 subagent / 子任务能力；**不需要装任何 CLI**
- **外部通道路径**：本地安装 [Claude Code CLI](https://docs.claude.com/en/docs/claude-code) **和/或** [OpenAI Codex CLI](https://github.com/openai/codex)，且在目标仓库的工作目录里可执行
- Python 3.8+（仅 `extract_session_ids.py` 脚本需要，且仅外部通道用）

### 协议

[MIT](LICENSE) —— Copyright (c) 2026 LetheChen &lt;lethe@chen.com&gt;。

### 参与贡献

见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。特别欢迎：bug 报告、新 prompt 模板、实战案例。

### 安全

见 [`SECURITY.md`](SECURITY.md) —— 漏洞请私下报告，不要在公开 issue 里发。

---

<sub>Maintained by [LetheChen](https://github.com/LetheChen). Built for the day when "I asked the model and it said it's fine" stops being a review.</sub>
