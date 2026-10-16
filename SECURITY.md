# Security Policy · 安全策略

## Supported versions · 支持的版本

Only the latest minor version receives security fixes.

只有最新的 minor 版本会收到安全修复。

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | ✅                 |
| < 1.0   | ❌                 |

## Reporting a vulnerability · 报告漏洞

**Please do not file a public issue.** Use one of:

- **GitHub Security Advisories** (preferred): [Report a vulnerability](https://github.com/LetheChen/adversarial-review/security/advisories/new) — private channel, tracked, disclosable.
- **Email**: lethe@chen.com (PGP key TBD if requested).

What to include:

1. Reproduction steps (the exact `claude` / `codex` command, the input prompt, the output).
2. Expected vs. actual behavior.
3. Impact assessment (e.g., "attacker could...").
4. Your name / handle for credit in the advisory (optional).

## Response targets · 响应时间

- **Acknowledgment**: within 7 days.
- **Triage & severity assessment**: within 14 days.
- **Patch**: target ≤ 30 days for high/critical, ≤ 90 days for medium/low.

## Out of scope · 不在范围

- The behavior of upstream tools (Claude Code, Codex CLI) — file those upstream.
- Issues in the user's own prompt content or the reviewed document.
- "Skill did not catch this issue" reports — that's a methodology tuning request, not a vulnerability; use the issue tracker.
