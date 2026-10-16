# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-16

### Changed
- **Renamed: `对抗性审查面板 / Adversarial Review Panel` → `对抗性复核 / Adversarial Review`.** "`面板`" / "`panel`" implied a UI, and this skill has none — it is a prompt workflow plus a ledger script. "`对抗性`" is kept because the red-team framing is still what it does; note that the 1.1.x design actually leans on *isolation* (reviewers cannot see each other, each gathers evidence by a different method) and *computable convergence* (R_t/E_t/C_t/S_t/K_t) rather than on conflict as such.
- **Breaking for installers**: the machine name changed from `adversarial-review-panel` to `adversarial-review` (`SKILL.md` frontmatter `name:`). Anyone who installed the old name must re-install; references to the old identifier will not resolve.
- Repository renamed to `LetheChen/adversarial-review` — the old GitHub URL redirects.
- The end-to-end diagram (`assets/business-process.html`) carries the new name in its title.

### Removed
- `业务流程图-对抗性复核.html` — the hand-written vertical swimlane is gone. Side by side, the archify sequence diagram reads better: the roles become columns and every arrow points the way the message actually flows. `assets/business-process.html` is now the single end-to-end diagram; the hand-written ①–⑮ step-by-step walkthrough survives only in git history.

## [1.1.2] - 2026-10-16

Remaining P1/P2 items from the same review (`REVIEW-优化评估面板-2026-10-15.md` §6 items 10 and 12).

### Changed
- **Process diagram replaced.** The old vertical swimlane (`assets/workflow-r1-rk.html`) is gone: it was too tall to read at a glance, and its connectors crossed in ways that misread as a wrong direction. Replaced by a horizontal **sequence diagram** (`assets/business-process.html`, with `assets/business-process.preview.png` for viewers where inline HTML does not render) — the six roles (user / host / executor / reviewer pool / file ledger / convergence gate) become columns and time runs downward, so every arrow points the way the message actually flows. Four phase bands (触发与定规 → 取证与独立结论 → 落盘质询与裁决 → 收敛定档), four guided views, and the same four explanatory cards. Generated with [archify](https://github.com/tt-a1i/archify); passes all 9 showcase artifact checks with 0 composition errors and 0 crossings.

### Fixed
- **`SKILL.md` §4.3 — layered source-fingerprint recipe** (item 10). `E_t` said "去除重提旧证据" but only carried the paragraph-level recipe. Now documents all four levels from the knowledge document §3.2 (文档级 / 段落级 / 检索级 / 推理链级), plus which level to use for which evidence shape:
  - 段落级 `sha256(normalize(text)[:512])` — default
  - 检索级 `hash(normalize(query) + 时间窗 + topk 文档ID集合)` — when there is a retrieval trail but no stable source text
  - 推理链级 SimHash/MinHash over the argument sequence — fallback for pure inference with nothing quotable
  - 文档级 — **auxiliary hint only**, never used alone to decide same-source; it is too coarse and would merge genuinely independent papers that cite the same review
  - Fingerprints must be immune to irrelevant surface differences (timestamps, temp IDs, language rewording, whitespace, punctuation). Without that, independence checking silently passes same-source evidence as independent.
  - Added the tie-back: equal fingerprints count as **one** piece of evidence and may not be recorded as multi-party independent confirmation (`:212`).
- **`references/pitfalls.md` §7 — new, 12 anti-patterns with authoritative numbers** (item 12). Number-recall was the measured failure: ~40% of the reviewed document's knowledge-document citations were wrong and one was a fabricated citation label. The table gives each of the 12 anti-patterns its number, the knowledge document's stated fix, and **where this skill already blocks it** — which is the part that makes it usable rather than a copy. Also records the known-stale citation points so nobody quotes them again.
- **`SKILL.md` 文件地图** — new row pointing at `references/pitfalls.md` §7, marked ⛔ 禁止凭记忆写编号.

### Notes
- Anti-pattern 12 (same model, different seed) and anti-pattern 4 (no source fingerprint) together are why `SKILL.md` §4.3 carries the "method diversity ≠ completeness" clause: 12 blocks the internal path, 4 blocks the external one, so L1-class shared factual errors stay unreachable from both directions.

## [1.1.1] - 2026-10-15

Fixes from the first native-subagent smoke review of `优化评估_对抗性审查面板.md`
(3 reviewers / 3 evidence-gathering methods / 1 round). Full record:
`REVIEW-优化评估面板-2026-10-15.md`; reviewer transcripts preserved verbatim under `_raw/`.

### Fixed
- `scripts/extract_session_ids.py` — four defects, all reproduced by the moderator after being reported:
  - **stdout is now reconfigured to UTF-8 at entry.** On a Chinese Windows console (GBK) the script previously raised `UnicodeEncodeError` at **all three** warning sites and exited 1 — it crashed exactly when it had something to report, and its non-warning path already printed mojibake Chinese. Verified: `--help` and both warning paths now exit 0 under a GBK pipe with no exception.
  - **`--help` / `-h` now print usage and exit 0**, instead of being parsed as a filename and exiting 0 having done nothing (a false success that passes any "just check --help works" routine).
  - **Same-source detection is now vendor/base-family based** (`model_family()`), not exact string equality. `MiniMax-M3.1-Flash-Preview` vs `MiniMax-M3` previously passed as "different"; both are MiniMax, so REVIEW metadata was auto-marked independent when it was not. Unknown families now report the check as **not completed** rather than "different".
  - **When a stream yields no model, the script states the cross-check did not complete** instead of silently skipping. REVIEW metadata must not claim the real model was verified when this fires. (On the codex `--json` event stream this currently always fires — see Known issues.)
- `.gitignore` — removed 15 lines of video/scrape pipeline rules (`dl/ frames/ kf/ douyin_* spider.html fetch*.py asr.py transcript* contact_sheet.jpg`) that had nothing to do with this skill and overlapped with the existing `*.visual-check.*` rules.
- **`SKILL.md` §4.3 — five adjudication-semantics defects**, all ruled on by the moderator after independent review (`REVIEW-优化评估面板-2026-10-15.md` §4 and §6):
  - `:244` / `:263` — **`R_t == 0` no longer means "adopt and end".** `R_t` counts unresolved disagreements *excluding* 已登记 items, so registering everything as unverifiable drove it to 0 and the panel declared convergence having resolved nothing — contradicting `:280`「已登记」≠「已解决」. The stop condition now reads 「本轮无新未解决分歧，但有 `K_t` 项已登记」and must not be written as 全部一致/已收敛. (Rejected the alternative fix of adding `且 已登记项 == 0`: it would make the normal state un-terminatable and introduce a new spin.) A new `K_t` row was added to the ledger table and to all three ledger sites (`:47`, `:311`, `:336`).
  - `:265` — the `S_t` action is now **拒答, not 登记**: the panel must explicitly write that the item is undecidable and produce **no** conclusion, downgrading to `证据不足` if the main conclusion depends on it. This aligns `SKILL.md` with the knowledge document's 拒绝给结论 branch, which two reviewers independently flagged as the gap.
  - `:255` — **L2 boundary stated.** Transcribing an *opponent reviewer or the moderator* is now counted as 无独立证据 per the `:212` circular-argument ban and is excluded from L2, resolving the overlap between the two rules.
  - after the three strength tiers — **method diversity ≠ completeness.** L1-class shared factual errors (agents equally wrong from model memory) are unreachable by any internal debate, L0–L4 grading, or stop condition. Backstopped by external signals only: re-runnable command output, production data, human spot-checks. A key premise in that class forces `证据不足`; ⛔ agreeing wording across reviewers is a danger signal there, not a convergence signal.
  - `:245` — `E_t` "去除重提旧证据" now defines fingerprint equality: `sha256(normalize(text)[:512])`, with `normalize` required to strip timestamps, temp IDs, language rewording, whitespace and punctuation (adopted from the knowledge document §3.2).
- `CHANGELOG.md` — the `1.1.0` entry had been inserted **above** the `# Changelog` header; the document is now in order under a single header.

### Known issues (still open)
- **The real-model cross-check is not reachable on the codex `--json` event stream.** `extract_session_ids.py` no longer claims otherwise: it now reports 流内/配置交叉校验未完成 whenever the stream carries no model field, and REVIEW metadata must not assert the model was verified when that fires. Getting a real value needs the session store or the CLI header, which is not wired up yet.
- **No cost baseline for the native executor**, still unmeasured — `SKILL.md §7` says so explicitly, and this review did not close it. The native smoke run did not record token count or wall time.

### Notes
- The reviewed document `优化评估_对抗性审查面板.md` was **stale as a change list**: every P0 it raised was already implemented by the 22:51 rewrite of `SKILL.md`, and ~40% of its knowledge-document section numbers are wrong. It now carries a header version anchor and a partial-invalidation notice pointing at the REVIEW adjudications, so it can no longer mislead the next reader. Conclusion strength for it: `仅供参考`.
- First end-to-end validation that the native subagent executor plus method assignment works. The three reviewers produced structurally disjoint reports (assertion table / executed-recomputation table / premise-attack table) with no overlapping finding IDs.

## [1.1.0] - 2026-10-15

### Added
- **Pluggable execution layer** (`SKILL.md` §1). Protocol layer (role definition, brief format, artifact naming, ledger & convergence, read-only constraints) is now separated from the executor. Four executors: native subagent (default), CLI subprocess (fallback), mixed, external channel.
- **Native subagent executor** as the default path (`SKILL.md` §4.0–§4.1, §4.2). Explicit `fork_context=false`; per-round single-target incremental delivery replaces `resume`; mandatory `close_agent` cleanup after each round.
- **Evidence-gathering method catalog S1–S4** (`assets/prompts.md`) — static check / live execution / reverse-premise attack / edge-case hunt. Enforced rule: no two reviewers in the same round get the same method. Reviewer count guidance (2 / 3 default / 4, never more) with rationale on why same-model resampling is not diversity.
- **Four computable convergence metrics** `R_t / E_t / C_t / S_t` and five stop conditions (`SKILL.md` §4.3), replacing "have all the disagreements been enumerated" judgement. Includes the cost-saving stagnation rule: `E_t == 0 and R_t > 0` for 2 consecutive rounds ⇒ stop and escalate.
- **Evidence grading L4–L0** (`SKILL.md` §4.3, threaded through templates A/B/C/D). L1/L0 may not drive convergence.
- **Conclusion strength levels** `可执行 / 仅供参考 / 证据不足` (`SKILL.md` §4.3). `证据不足` blocks automatic edits to the reviewed document.
- **Circular-argument ban**: reviewers may not use another reviewer's or the moderator's conclusion as evidence; such items are marked `无独立证据` and excluded from convergence. Moderator must merge overlapping evidence positions into a single source instead of counting them as multi-party confirmation.
- **Moderator recall audit checklist (template E)** — 7 checks run by the moderator every round from R2 to catch false convergence.
- **Two information-flow rules** for cross-examination: the opponent's objections are never omitted, but the moderator's verdict is delivered to **only the ruled party** (anti-symmetric-information drift).
- **Anti-"only refute" balance**: every reviewer must first list ≥3 points it confirmed as correct.
- `references/pitfalls.md` §6 — native subagent pitfalls + measured parameters (concurrency limit 6 on this machine; completed agents hold their slot until closed; no sandbox ⇒ soft read-only; no reliable resume) + native-vs-CLI comparison table.

### Changed
- `SKILL.md` — restructured around the protocol/executor split; §3 persistence and §5 cost model no longer assume CLI-only operation; "最容易死的事" now leads with the four execution-layer traps.
- `assets/prompts.md` — templates A–D rewritten; added the method-assignment preamble, evidence grading, circular-argument ban, and template E.
- `README.md` — bilingual; native subagent path documented as the default, CLI CLIs now optional requirements.
- `references/pitfalls.md` — header now points to §6 for the native executor.

### Notes
- `scripts/extract_session_ids.py` is now **CLI-channel only** (there are no external sessions to track on the native path). Behaviour unchanged.
- Unmeasured previously: the native executor's cost baseline is not yet characterized the way §3 of `pitfalls.md` characterizes the CLI channel.

able changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-14

### Added
- Initial open-source release.
- `SKILL.md` — Full methodology for single- and multi-round adversarial review.
- `assets/prompts.md` — R1 red-team & Rk cross-examination prompt templates (A–D), with per-reviewer micro-tweaks.
- `references/pitfalls.md` — Complete pitfall catalog, with worked examples and the model/config auto-detection logic.
- `scripts/extract_session_ids.py` — Session/thread ID extraction + same-source-model detection + cost summary.
- Dual-language `README.md` (English + 中文).
- `LICENSE` (MIT).
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`.
- GitHub issue & PR templates.
- Minimal `.gitignore` (system / IDE / Python / skill runtime artifacts).

