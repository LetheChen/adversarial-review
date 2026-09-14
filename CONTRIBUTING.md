# Contributing · 贡献指南

Thanks for considering a contribution. This skill is small on purpose — the bar for additions is "would the next person trying to do adversarial review actually need this?"

## How to contribute

1. **Open an issue first** for non-trivial changes. Describe the use case in 2–3 sentences and the proposed fix.
2. Fork the repo, create a feature branch (`feat/short-name` or `fix/short-name`).
3. Make the change. Keep diffs small and focused.
4. Verify locally:
   - Python script: `python scripts/extract_session_ids.py --help` (or feed it a real Codex `--json` and Claude `stream-json` output, check it doesn't crash).
   - Markdown: render in your editor or a Markdown preview, check links resolve.
5. Open a Pull Request using the template. Reference the original issue.

## What we especially welcome

- **New prompt templates** in `assets/prompts.md` — for domains we haven't covered (legal, finance, ML models, security audits...).
- **New pitfalls** in `references/pitfalls.md` — each one with a concrete reproduction (what you ran, what broke, what to do instead). Without a repro it's just a complaint.
- **Bug fixes** in the extractor script — false positives in the same-source check, parser crashes on real-world Codex/Claude output, etc.
- **Translations** — README.md is bilingual EN/ZH; SKILL.md is mostly Chinese. Contributions in other languages are welcome if you can also maintain them.

## Style

- Markdown: ATX headings (`#`, `##`), fenced code blocks with language tags.
- Code: PEP 8 for Python. No external dependencies in the extractor — stdlib only.
- Commit messages: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).
- One logical change per commit. Squash before merging is fine.

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md). Be specific, be kind, cite evidence.

## License

By contributing you agree your contribution is licensed under the project's [MIT](LICENSE) license.
