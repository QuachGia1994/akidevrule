---
name: akiship
description: Run the full release ritual end-to-end with one command — front-loaded checks, then an unattended pass. Sequences RULE-release.md B7 (leftover triage, diff-scoped hygiene, external-action completeness, record truthfulness, doc sync, verification honesty, version decision) under the B8 autonomy contract (invocation = authorization; stop only on public-history ambiguity, unclassifiable work, or design contradiction — completion-intensity phrasing like "trọn vẹn"/"hoàn thành, hoàn thiện" collapses the unclassifiable-work stop toward finish-it-anyway AND authorizes push/tag/GitHub-Release without a separate ask). Commits via akigitcommit with confirmation pre-answered. Push/deploy stay opt-in — named explicitly, or via completion-intensity phrasing. Use on "akiship", "release trọn gói", "chạy full release", "ship đợt này".
---

# akiship — one-command full release

Invoke with `/akiship`. Goal: replace the daily hand-typed ritual ("resolve leftovers, sync every doc, lint, fix drift, changelog, commit, release…") with one invocation that runs to completion or stops once, early, with every blocker in a single batch.

**This skill sequences; it does not own content.** The checklist is `RULE-release.md` B7 and the autonomy/escalation contract is B8 — read that file first (installed at `~/.aki/akidevrule/RULE-release.md`), plus `RULE-docs.md` for the doc-sync step. If a step here ever disagrees with the rule file, the rule file wins.

## Phase 1 — front check (all asks happen here or never)

1. Derive release state cold per `release.B1` (manifest, CHANGELOG top, boundary commit, accumulation log).
2. Triage the tree per B7 step 0 (the `/akigitcommit` step-0 taxonomy; read-only, `agent.B5`).
3. Collect every hit on the B8 escalation floor — public-history ambiguity, unclassifiable work, design contradiction / scope beyond the invocation. **Completion-intensity phrasing in the invocation** ("trọn vẹn", "hoàn thành"/"hoàn thiện", "làm/xong hết", "tất cả"/"toàn bộ", or equivalent sentiment insisting the run finish everything) resolves the unclassifiable-work hit toward mid-edit by default — finish and integrate it, do not flag it — **and stands in for a named push/deploy authorization** (see Phase 3 step 4). **Any hit on the remaining two → report them all in one batch and stop.** No hits → proceed; from here the run asks nothing (`release.B8`: a question the repo already answers is a violation).

## Phase 2 — gate, fixing in place

Run B7 steps 2–6 in order, fixing findings as they surface (this is a gate, not an audit — no findings doc):

- **Hygiene, diff scope only**: `python3 ~/.claude/skills/akiflow/scripts/scythe.py <files changed since boundary>` for `[WRAP]`/`[YAP]`; dead code / redundant guards / duplication the accumulation introduced (`pattern.A8`); doc refs in touched comments still resolve (`docs.B3`). Never widen to the whole repo.
- External-action completeness, record truthfulness (CHANGELOG + `releases.json` parity where it exists), doc sync (plans → `done/`, `arch`/`feat` stamps per `docs.A4`), verification honesty — anything runtime-only is carried to the final report as **unverified**, never silently assumed (`coding.B3`).

## Phase 3 — commit, mint, artifacts

1. Commit in logical groups per `/akigitcommit` (domain-grouped mode; anti-stage-loss rules apply in full). B8 pre-answers its confirmation step — "commit luôn" semantics.
2. Version decision per `release.A4`/`A5`: mint exactly once at the highest accumulated severity, or defer on the materiality test. Deferring is a normal outcome, not a failure.
3. Artifacts per the repo's own convention: bare tag only if the repo already tags (`release.A3` B8 exception); GitHub Release per `release.B4`; `releases.json` sync check per `release.C4`.
4. **Push / deploy only if the invocation named them, or carries completion-intensity phrasing (§ Phase 1 step 3).** A plain invocation with no intensity marker stays local-only. If pushed and the stack deploys, run live verification per `release.C5` afterward.

## Report

One dense summary (`agent.A4`): state derived → findings fixed (counts per gate step) → commits made → version minted or deferred with the reason → artifacts created → anything left **unverified**, each with the exact command that would settle it.

## Boundaries

- The B8 escalation floor is the only reason to stop mid-run; everything else is self-answered from repo, docs, and rules.
- Never push, deploy, or push tags on an invocation that neither named them nor carried completion-intensity phrasing.
- A repo-wide hygiene/subtraction sweep is out of scope — point the user at `METHOD-subtraction-audit.md` instead of widening the gate.
