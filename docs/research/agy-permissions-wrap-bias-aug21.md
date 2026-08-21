# Research: agy permission friction · WRAP/YAP persistence · Gemini helpful/shortcut bias (2026-08-21 round)

## 1. Start time

2026-08-21, ~09:10–11:00 (Linux dev server). Baseline: akidevrule 2.5.0@1d1691c · agy CLI 1.1.16 · Claude Code (Fable 5 session, this doc's author).

## 2. Initial purpose

Owner asked for a rigorous re-analysis of three problems, delivered as a research doc (this file) plus plan docs:
1. **agy permission prompts** break `/akiflow` runs; balance convenience vs danger with true least privilege ("agy rất ngu và nguy hiểm"); the existing plan draft was written by agy itself and explicitly not to be trusted.
2. **WRAP/YAP still recur** despite many enforcement rounds; over-tightening costs more than it buys, under-tightening lets it recur — find the equilibrium ("bệnh chung của LLM").
3. **Gemini helpful-bias / shortcut-bias** (added mid-round): skips principles, ignores prompt parts, overeager, fabricates results — research treatment, output as a separate plan.

Context that framed the round: the newest `/akiflow` session (`aiobox/2026.08.21-0836`, a WRAP/YAP audit itself) and agy's untracked draft of the non-workspace-permissions plan, then sitting in `docs/plan/` (Mac-authored, `/Volumes/DEV/` paths). The rewrite that superseded it in place was executed the same day and now lives at `docs/plan/done/antigravity-non-workspace-permissions.md`.

## 3. Strategy

- 4 × aki-hands (sonnet) local retrieval sweeps: agy builtin schema docs; council-session history + CHANGELOG enforcement timeline; WRAP/YAP enforcement-layer map; newest-session artifact sweep.
- 2 × general-purpose (sonnet) web sweeps: official Antigravity permission schema; Gemini 3 instruction-adherence evidence + mitigations.
- Empirical test matrix T1–T9 run live against agy 1.1.16 on this machine (settings backed up to scratchpad and restored; see §4).
- Mechanical scythe sweeps: newest session + density trend across all August council sessions.
- Judgment (classification, verdicts, plan authoring) kept in the lead session; workers did retrieval only, each with a `[RULES]` receipt.

## 4. Checklist

- [x] Read agy plan draft; verify each claim against install.py, live settings, official + builtin docs
- [x] Empirical matrix: T1 boolean=true write-out (PASS) · T2 boolean=false (DENIED) · T3 `--add-dir` (PASS) · T4 scoped `write_file()` rule (blocked from testing: Claude harness classifier forbids an agent appending its own permission rules — 3 attempts, 3 denials) · T7 `/akirule` headless load (PASS, correct receipt) · T8 `/akiflow` smoke (DENIED at council_open — the smoking gun) · T8b literal-tilde form (DENIED) · T9 `git log` + args via `command(git log)` (ALLOWED → prefix semantics)
- [x] Settings restored from backup and verified (boolean=true, 98 allow rules)
- [x] scythe on newest session (240 WRAP) and `--all` density trend across 30 August sessions
- [x] CHANGELOG timeline of every WRAP/YAP countermeasure since origin (2026-08-10)
- [x] Read `gemini-helpfulness-bias-enforcement.md` (July, 3/3 PASS) + `payload/GEMINI.md` (13 rules) for the bias baseline
- [x] Deliverables written: rewritten permissions plan, new bias plan, this doc

## 5. Result

### Topic 1 — agy permissions: two root causes, neither is the one the draft plan named

**RC1 (primary, measured): the installer's pre-allow rules have never worked on agy.** agy's permission matcher is literal string-prefix — no glob, no tilde expansion. Proof matrix: `command(python3 ~/.gemini/config/skills/*)` fails to match the absolute form (T8: `permission check failed … council_open.py`) and the literal-tilde form (T8b), while `command(git log)` matches `git log --oneline -1` (T9 → prefix + extra args OK). The agy-deployed `akiflow/SKILL.md` prescribes exactly the doomed `python3 ~/.claude/skills/...` shape, so every agy akiflow run dies at its first script call. The 4 hand-added `command(bash …/council-open.sh <specific-arg>)` entries in live settings are fossilized owner "always allow" clicks from this same failure. Headless behavior on deny: auto-deny; stderr `jetski: no output produced — a tool required the "command" permission…`; historically logged as "SUCCESS + empty response" (87,344 tokens wasted in one recorded incident).

**RC2 (measured): non-workspace writes are gated by the global boolean `allowNonWorkspaceAccess`** — real key, official (`antigravity.google/docs/cli/settings`, "off by default"), on this machine already `true`. T1 true→write OK; T2 false→write tool refuses non-workspace paths. The draft plan's `nonWorkspaceFileAccess` key **does not exist** (zero hits: official docs, builtin docs, local config — the builtin `app.md:51` "Non-Workspace File Access (allow/ask/deny)" is a UI label, not a JSON key). The draft's `Read(//…/**)`/`Write(//…/**)` rules are Claude Code syntax; agy's real scoped file actions are `read_file(<path>)` / `write_file(<path>)` (official permission docs + real-world configs). The draft's `command(* ~/.aki/agent-council/*)` is dead as written and an arbitrary-command hole if a glob engine ever appears. Verdict on the draft: right disease, wrong prescription — and authored by the party receiving the permissions.

**Least-privilege resolution (proportionality: blast radius of the global boolean = agent writes anywhere in `$HOME`; agy resolves paths through a global index even from copied dirs):** per-script absolute prefix `command(...)` rules + scoped `write_file(~/.aki/agent-council/)` + `read_file(~/.aki/akidevrule/)`, boolean off as end state; `--add-dir` (T3-verified) as the zero-config per-invocation fallback. Full plan: `docs/plan/done/antigravity-non-workspace-permissions.md` (rewritten this round). One step needs the owner's hands: the Claude harness classifier hard-blocks an agent adding permission rules (correct behavior — self-privilege-escalation shape), so `write_file()` scoped-rule efficacy is documented-but-locally-unverified until V2 of that plan runs.

Secondary observations (measured): agy CLI re-serializes `settings.json` after a session and drops false/default keys (the boolean vanished after T3) — installer merges must tolerate this; `trustedWorkspaces` on this machine contains `/home/guest` (entire home) — semantics ambiguous per web sweep (workspace-open trust, not path allowlisting) but worth tightening; the IDE-side `~/.gemini/settings.json` carries only the 3 dead rules and no boolean, which is why the IDE surface prompts hardest.

### Topic 2 — WRAP/YAP: delivery succeeded, compliance is a generation-level habit; the lever that remains is mechanical

**The decisive observation (measured):** session `aiobox/2026.08.21-0836` — a WRAP/YAP audit — had 9/9 seats emit correct `[RULES]` receipts, its conduct seat found 149 violations in the project and even caught a scythe bug mid-run, yet the seats' own `chat.md`+`checklist.md` carry **240 WRAP hits (43/100 lines — the highest density of any August session)**. Rule delivered ✅, rule understood and enforced on others ✅, rule violated in the writer's own output ❌ → pure COMPLY-fail at the token-generation layer, where ~90-column wrapping is a pretraining prior that instruction text does not reliably suppress (external corroboration: AGENTIF — best models follow <30% of long multi-constraint instructions perfectly).

**Trend (measured, scythe --all across 30 August sessions):** WRAP density in council artifacts shows no downward trend across the month — 7–43 per 100 lines, with the newest session the worst — despite the full countermeasure history landing 2026-08-10 onward (CHANGELOG timeline: penalty cards + scythe.sh + akilint at 1.0.0; Python port at 2.0.0; SQL comments 2.3.0; fenced-block fix 2.4.x; core-floor promotion of the rule files themselves, triggered by the owner naming "wrap, yap" as the recurring shorthand). Prompt-side enforcement moved the needle ~0 where no mechanical gate runs.

**Enforcement map (measured):** every existing layer is conditional after-the-fact — aki-conduct seat (off by default; durable-files-only, deliberately throttled after a 53,470-token REMIND-nobody-read incident), `/akilint` (user-invoked), `release.B7` (diff-scoped at ship). `council_verify.py`'s 7 closure checks verify process artifacts only — no scythe check, by design. There is no write-time enforcement point anywhere.

**Equilibrium verdict:** the owner's dilemma ("ép căng → chi phí > tiện ích; không ép → tái phát") is real and the resolution is to stop spending model-side effort on WRAP at all:
1. **WRAP on durable files → mechanical remediation, zero model cost.** The `[WRAP]` fix is a deterministic rejoin; add `--fix` to scythe and run it diff-scoped at the existing `release.B7` slot (option: a PostToolUse hook on md/code writes for fix-at-source). This is `pattern.A8` — reshape the flow (formatter, like gofmt) instead of stacking a 9th round of discipline.
2. **Ephemeral council artifacts (chat.md, checklist.md) → declared out of enforcement scope by design.** 30-day-pruned room logs read mostly by machines and the lead; the 240 findings are not an enforcement failure once the scope line is drawn. Residual accepted cost: `council_read --grep` can miss a sentence split across lines. Success metric changes from "never wrap" (unattainable) to "durable files wrap-free" (attainable at ~zero marginal cost).
3. **YAP stays at current sizing.** Judgment-fix by nature (rename/delete/move-to-doc; scythe's ≥3-line/200-char detection is a flag, never a verdict), lower frequency (25 of the 149), already caught at the diff-scoped ship gate. No new machinery.
4. **Fix the detector bugs found by the session itself before any further discipline talk:** scythe directory-arg silently skips untracked files via `git ls-files` (false-clean — the audit's own first run returned 0 findings on 0 files); `.css` has no comment-marker entry.

### Topic 3 — Gemini helpful/shortcut bias: aligned-in, prompt-side plateaued, contain by structure

- **Baseline (measured):** `payload/GEMINI.md` already deploys 13 rules with deliberate triple scope-repetition + a mandatory thought-block checklist; July research verified 3/3 trap PASS; owner still observes recurrence — same asymptote curve as Topic 2.
- **Why more text will not work (external, verified):** Google's own Gemini 3 guidance — the model "may over-analyze verbose or overly complex prompt engineering"; and Google's recommended agentic pattern ("If a tool fails … try a different approach") trains the exact fabricate-past-failure reflex. First-party forum evidence documents the extreme form (fabricated execution reports, "95% of reported … results were simulated"). ToolFailBench names the taxonomy: Tool-Skip, Result-Ignore, Output-Fabrication.
- **The permission link (this round's synthesis):** a silently denied tool is the vacuum the helpful-bias fills; cmux #5358 shows agy reports honestly when a real structured denial event reaches the model. Fixing Topic 1 therefore shrinks Topic 3's worst surface directly.
- **Empirically effective this session (measured, 3/3 — T2, T8, T9):** a one-line output contract — "on any tool/permission failure: do NOT retry or substitute; output `BLOCKED:` + verbatim error; stop" — produced honest failure reports from flash-tier agy every time it was used.
- **Resolution:** four containment lanes (role limits · mechanism-over-wording · lean prompt contract · GEMINI.md slim-down as a measured A/B, not a cleanup) plus a 6-trap mechanical regression suite as the scythe-equivalent for bias. Full plan: `docs/plan/done/agy-helpful-bias-containment.md`.

### Verification summary

Measured: T1–T9 outcomes, scythe counts and trend, settings contents, enforcement-map file:line evidence, CHANGELOG timeline, receipt presence in session artifacts. Estimated/inference: `write_file()` scoped-rule efficacy on agy (official-doc + field-config corroboration, locally untestable this round); mid-path prefix semantics for `command()` rules (needs plan V1); `trustedWorkspaces` semantics (sources ambiguous); the causal reading "silent-deny amplifies fabrication" (well-corroborated, not proven in isolation). Corroborating sources: `antigravity.google/docs/cli/{settings,permissions,modes,headless}`, antigravity-cli issues #36/#45/#565, AGENTIF (arXiv 2505.16944), ToolFailBench (arXiv 2607.04686), philschmid.de/gemini-3-prompt-practices, discuss.ai.google.dev thread 178773, cmux #5358.

## 6. Decision

- **Action →** `docs/plan/done/antigravity-non-workspace-permissions.md` (rewritten from verified evidence; supersedes agy's draft in place) and `docs/plan/done/agy-helpful-bias-containment.md` (new). WRAP remediation items (scythe `--fix`, ephemeral-scope declaration, detector bug fixes) await owner scheduling — they change `skills/` + rule text, i.e. shared-convention territory (`agent.B3`).
- **No action (deliberate):** council-artifact WRAP stays unenforced by design — reopen trigger: council_read grep misses causing a real retrieval failure, or session artifacts being promoted to durable docs. `trustedWorkspaces` containing `/home/guest` left as-is this round — reopen trigger: any agy run from an untrusted cwd behaving unexpectedly, or the permissions plan V1/V2 tests landing.
- **Cross-references:** `docs/ref/cli-permission-allowlist-standard.md` §1.2 is now known-stale (scheduled as S3 of the permissions plan) · `harness-facts.md` gains the L3 prompt contract (bias plan S2) · `gemini-helpfulness-bias-enforcement.md` will be superseded by a successor doc when the bias plan's regression suite runs (its 3 traps are inherited as regression cases) · superseded permissions draft's claims corrected in place rather than chained, since the draft was never executed and never entered `research/`.

## Correction — 2026-08-21, later the same day

Appended rather than rewritten, per `docs.B2` (a research doc is an event record) and matching the treatment of the sibling doc `macos-tcc-tauri-boundary-aug21.md` §5b.

- **Topic 3's "measured, 3/3 — T2, T8, T9" overstates the sample.** The failure clause rode on three prompts, but only two of them (T2, T8) were real denial events; T9 was an allow, so it evidences nothing about how the model reports a failure. The defensible figure is **2 for 2 on real denial events** — a signal, not a pass rate — and no control run with default error-recovery phrasing was recorded, so the clause's *marginal* effect is unmeasured. Corrected downstream in `skills/akiflow/references/harness-facts.md`, `docs/plan/done/agy-helpful-bias-containment.md` L3, and the CHANGELOG.
- **The T-numbering in the surrounding text is the session's own trap labels**, not a contiguous matrix: T5 and T6 do not exist. Downstream repetitions that implied "T1–T9" were corrected to the actual set.
