# akirule + akiflow upgrade — density, MVP counterweight, roster mapping

**Start time:** 2026-08-03

## Initial purpose

The owner now runs nearly all work with akirule + akiflow together, across projects that have grown large. Recurring pains, in the owner's priority order: (1) behavior floor violations by workers (hard-wrapping above all), (2) chronic verbosity — code comments, docs, UI content all over-written with no density discipline, (3) structural work patches instead of reshaping unless `RULE-design-core.md` is named explicitly. Plus: no structural counterweight to council over-engineering, recurring docs/comment/content drift, no named principle for worker context modes, and a roster/model map lagging the real fleet (proxy-gateway Claude lane, kiro-cli tiers, a separate content-writer need).

**Context at the time:** corpus state as of commit 6b33dc6; Claude Code with OAuth main login plus an owner-provisioned 9router gateway lane (`~/.claude-9rt`); agy 1.1.9; kiro-cli 2.16.0.

## Strategy

`/akithink` session on the full corpus (`nạp full`) plus `harness-facts.md`, `docs/arch/akiflow.md`, and `docs/research/headless-cli-workers-aug1.md`. Unifying diagnosis before proposing: classify each pain as "rule missing" vs "rule exists on the wrong enforcement tier". Three tiers, strongest last: signal-routed prose < floor pasted into every prompt, stated as checkable format < harness mechanism.

## Checklist

1. Full corpus + akiflow reference load; map each owner pain to existing rule coverage.
2. Goal excavation, first principles, mandatory critique (steelman, inversion, pre-mortem, second-order).
3. Owner decisions collected: P1 placement, enforcement ceiling.
4. Apply edits across payload, skills, README, CHANGELOG; run install.sh.

## Result

**Root finding:** the three worst pains were all tier-1 failures, not missing rules. `agent.C3` (wrapline) existed but subagents never met it in force; "keep content concise" (`content.B2`) was an adjective, the exact form the corpus itself proves unenforceable ("adjectives do not enforce thinking; format does"); `RULE-design-core.md` was signal-gated so structural work ran without it unless named. Verbosity/wrapline are default model behavior, so only structural enforcement — not reminders — changes them.

**Verification:** corpus texts cross-read directly this session; worker economics and CLI facts taken from the already-verified `harness-facts.md` / `headless-cli-workers-aug1.md` measurements. Two new facts are owner-supplied and marked `[owner]` where recorded: the 9router "Sn" alias routes to a deepseek-v4-pro-class core; `gemini-3.1-pro` writes softer user-facing prose than Sonnet-class implementers. Neither carries a rule without a probe/verification step. The central assumption — that floor-level format clauses reduce hand-reminders — is **unverified**; measure over ~2 weeks of real sessions.

## Decision

**Action** — seven changes applied (plan: `../plan/done/density-roster-upgrade.md`):

1. **P1 density rules at domain tier** — new `coding.B4` (self-documenting code: naming/shape first, comment only what code cannot say, deletion test, one-line budget, rationale→docs), `content.B2` rewritten around the deletion test + first-sentence-carries-the-point, density bullet in `docs.B3`, and a Cross-cutting lens row in `payload/index.md` with root `agent.A4`. Owner explicitly chose domain files over the core floor.
2. **P2 enforcement tier** — akiflow thinking-floor clause 5 OUTPUT HYGIENE (no hard-wrap, file:line citations, comment budget, deletion test): the tier that actually reaches subagents.
3. **P3 MVP counterweight** — Red Team second standing assignment: the subtraction pass against over-engineering; closure rationale must name what was cut and why this is the smallest shape.
4. **P4 design-core promoted** — default ON with `RULE-coding` for any structural work (akirule SKILL); in akiflow the Architect/structural items already had it via the lead-as-router rule.
5. **P5 drift guard** — drift sweep folded into the Phase B verifier and the Tier 0 verifier: enumerate docs/comments/i18n/CHANGELOG references to changed behavior, report stale ones.
6. **P6 roster map** — 9router generalized to "Claude via a proxy gateway": parallel explore/bandwidth seat, possibly non-Anthropic core behind an alias, API-key auth so `--bare --tools "Read,Grep,Bash"` works there, probe + recommend-setup-where-absent; writer role split from implementer (default agy `gemini-3.1-pro`, anti-fabrication brief).
7. **P7 context modes named** — BLANK / INHERIT-BY-ARTIFACT / OWN-ACCUMULATING as a mandatory per-spawn declaration in akiflow Step 2.

**Rejected/closed:**
- Density root in the core floor (`RULE-agent-behavior.md`) — owner chose to keep core small; revisit only if main-thread (non-akiflow) verbosity persists after this round.
- PostToolUse lint hook for wrapline/density — owner: the property is content understanding, not mechanical format; a hook is too rigid.
- A standing drift agent and a standing simplifier agent — both violate the item-driven roster (gate law 4); delivered instead as a verifier lens and a Red Team mandate.

**Assumptions to monitor:** floor clause 5 measurably cuts hand-reminders (falsifier: still reminding >~2×/week after two weeks → escalate placement); Red Team carries two mandates without dropping one (falsifier: subtraction passes missing from closures → split a separate consult); `gemini-3.1-pro` agy quota suffices for real content batches (probe before first long batch).

### Cross-references

- `skills/akiflow/SKILL.md`, `skills/akirule/SKILL.md`, `payload/RULE-coding.md`, `payload/RULE-content-write.md`, `payload/RULE-docs.md`, `payload/index.md`, `skills/akiflow/references/harness-facts.md`, `README.md` — the edits themselves
- `docs/arch/akiflow.md` — design rationale this builds on (victory-audit gap now partially covered by the closure two-liner)
- `docs/research/headless-cli-workers-aug1.md` — the measurements behind the worker-shape rows this doc extends
