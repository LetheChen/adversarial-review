# Adversarial Review Panel · 对抗性审查面板

> Send analysis / proposals / code changes to **independent reviewers** (Claude Code + Codex) for adversarial (red-team) review — single-reviewer, team-parallel, or N-round cross-examination until convergence. Produces a `REVIEW-` document.

> 把分析文档 / 方案 / 代码改动交给**独立审核方**（Claude Code 与 Codex）做对抗性审查（红队复核）—— 单审核方、团队并行、N 轮交叉质询与收敛判定，产出 `REVIEW-` 文档。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![Skill Type](https://img.shields.io/badge/type-AI%20Agent%20Skill-green.svg)](#)

---

## English

### What is this?

A **Claude Code / Cursor skill** that turns "review this" into a structured adversarial review. Instead of trusting the model that wrote the doc, the skill dispatches the work to one or more **independent reviewers** (Claude Code itself, or OpenAI Codex CLI), enforces file-based accounting, and supports N-round cross-examination until disagreements are resolved.

**Core principle: the file is the ledger (authoritative), the session is the accelerator (cost-saver).**

### Why?

Because the model that wrote the document is the model most likely to **defend** it. And because "I asked another LLM and it agreed" is not actually a review. This skill forces:

- A **different** reviewer (different CLI, possibly different model).
- **Independent** verification (the reviewer must open the file, not paraphrase it).
- **Accountability** (every claim is anchored to `file:line` + raw evidence).
- **Convergence** (N-round debate with explicit "maintain / revise / withdraw" on each contested point).

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
| "Have Claude review this" | Single reviewer, 1 round |
| "Have Codex review this" | Single reviewer (Codex CLI), 1 round |
| "Send to team review" | Claude + Codex, independent reports |
| "Team review for 3 rounds" | R1 independent + 2 rounds of cross-examination |
| "Red-team this analysis" | Same as "team review" (alias) |

### File map

| When you need | Read this |
|---|---|
| The full methodology, decision rules, execution steps | [`SKILL.md`](SKILL.md) |
| R1 red-team prompt, Rk cross-exam brief, micro-prompts per reviewer | [`assets/prompts.md`](assets/prompts.md) |
| Every pitfall, with worked examples and the model/config detection logic | [`references/pitfalls.md`](references/pitfalls.md) |
| Extract session/thread IDs, detect same-source model, compute cost | [`scripts/extract_session_ids.py`](scripts/extract_session_ids.py) |

### Requirements

- A local install of [Claude Code CLI](https://docs.claude.com/en/docs/claude-code) **and/or** [OpenAI Codex CLI](https://github.com/openai/codex).
- Both must be runnable in the target repository's working directory.
- Python 3.8+ (only for the session-id extractor script).

### License

[MIT](LICENSE) — Copyright (c) 2026 LetheChen &lt;lethe@chen.com&gt;.

### Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Bug reports, new prompt templates, and worked examples are especially welcome.

### Security

See [`SECURITY.md`](SECURITY.md) — please report vulnerabilities privately, not via public issues.

---

## 中文

### 这是什么？

一个 **Claude Code / Cursor skill**，把"审一下"变成结构化的对抗性审查。不信任写出文档的那个模型，让 skill 把工作分发给**一个或多个独立审核方**（Claude Code 自己、或 OpenAI Codex CLI），强制文件账本，支持 N 轮交叉质询直到分歧收敛。

**核心设计原则：文件是账本（权威），会话是加速器（省钱）。**

### 为什么要这样？

因为写出文档的那个模型最有可能**维护**它。因为"我又问了个 LLM 它同意"根本不是审查。这个 skill 强制：

- **不同的**审核方（不同 CLI，可能不同模型）
- **独立的**核验（审核方必须打开文件，不能只复述）
- **可追溯的**证据（每条断言锚定到 `文件:行号` + 原文片段）
- **收敛的**讨论（N 轮辩论，对每个争议点显式"维持/修正/撤回"）

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
| "让 claude code 审核" | 单审核方 1 轮 |
| "让 codex 审核" | 单审核方（Codex CLI）1 轮 |
| "发给团队审核" | Claude + Codex，各自独立报告 |
| "团队审核 3 轮" | R1 独立 + 2 轮交叉质询 |
| "红队审一下" | 同"团队审核"（别名） |

### 文件地图

| 你需要 | 读这个 |
|---|---|
| 完整方法论、决策规则、执行步骤 | [`SKILL.md`](SKILL.md) |
| R1 红队 prompt、Rk 交叉质询 brief、每家微调 | [`assets/prompts.md`](assets/prompts.md) |
| 全部坑点 + 实测案例 + 模型/配置自动检测逻辑 | [`references/pitfalls.md`](references/pitfalls.md) |
| 提取 session/thread id、检测同源模型、算账 | [`scripts/extract_session_ids.py`](scripts/extract_session_ids.py) |

### 依赖

- 本地安装 [Claude Code CLI](https://docs.claude.com/en/docs/claude-code) **和/或** [OpenAI Codex CLI](https://github.com/openai/codex)
- 两者都必须在目标仓库的工作目录里可执行
- Python 3.8+（仅 `extract_session_ids.py` 脚本需要）

### 协议

[MIT](LICENSE) —— Copyright (c) 2026 LetheChen &lt;lethe@chen.com&gt;。

### 参与贡献

见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。特别欢迎：bug 报告、新 prompt 模板、实战案例。

### 安全

见 [`SECURITY.md`](SECURITY.md) —— 漏洞请私下报告，不要在公开 issue 里发。

---

<sub>Maintained by [LetheChen](https://github.com/LetheChen). Built for the day when "I asked the model and it said it's fine" stops being a review.</sub>
