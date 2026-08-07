# Zero-trust audit: a strict sweep that does not fight the core audit rule

**Start time:** 2026-08-06

## Initial purpose

A first draft of `METHOD-zero-trust-audit.md` shipped into the working tree as a **fix-in-place** procedure: existential justification for every file, function and line, with the agent renaming and deleting as it went. Review of the uncommitted tree flagged it, and the owner then restated what was actually wanted: a strict rule for **algorithmic** review — surface what a mechanism can surface, keep language- and pattern-level observations as suggestions rather than verdicts ("pattern thì logic chỉ gợi ý được chứ không phán xét được"), scope either the whole project or the change and what relates to it, and output a **specific, short audit report**.

## Strategy

1. Take the restated intent as the specification, not the first draft.
2. Keep every part of the draft that is enforcement-tier (mechanical scope-lock, detectors first, signature propagation, self-challenge, no probabilistic language) and drop every part that conflicted with the core floor.
3. Change no address anywhere else in the corpus — the file already had its manifest row, group row, routing block, README entry and layout entry.

## Checklist

- [x] Diagnosed the conflicts against `agent.B5` (audit is read-only), `agent.B3` (ask before broad renames), `agent.A5` (a worker/prompt must name exact files, not a skill name)
- [x] Rewrote the file around the CERTAIN / SUGGESTED evidence split
- [x] Made detector invocation conditional on the project actually having the detector
- [x] Replaced the per-file report table with a findings-only report plus a one-line coverage statement
- [x] Registered the method as a domain application of the `agent.B5` cross-cutting lens row
- [x] Synced `payload/index.md` (manifest row, group row, lens row), `skills/akirule/SKILL.md`, `README.md`, `install.sh` (`AG_RULE_MAP`), `CHANGELOG.md`

## Result

### What was wrong with the first draft

| Defect | Why it mattered |
|---|---|
| Declared itself a fix-in-place procedure | `agent.B5` is core floor, `@`-imported into every session; a signal-routed METHOD cannot weaken it, and `index.md` §Precedence says so explicitly. An agent holding both had no tie-breaker. |
| Mass rename and mass fix with no gate | `agent.B3` requires asking before broad renames; and by stepping outside `B5` the draft also stepped outside its ban on mutating git state — the worst possible combination on a half-finished tree. |
| Armed by a deliberately over-sensitive router | `akirule` errs toward loading because a false positive "costs a few tokens". For this file a false positive would have cost an unrequested refactor. |
| `"cross-check against ALL rules in /akirule"` | A skill name is not a path; nothing loads. `agent.A5` is explicit that a brief must name exact files. |
| Unconditional `scythe.sh` and `tsc` | `scythe.sh` lives in the akidevrule source repo and was cited without a path; `tsc` assumes TypeScript. A rule naming an absent tool teaches the reader the rule is decorative — the same defect measured in `ui.A2` two days earlier. |
| `"remember this across turns, do not make mistakes"` | A reminder-tier fix for an enforcement-tier failure, the pattern `akiflow-compliance-enforcement-aug3.md` already recorded as ineffective. Dropped. |
| One report row per file in scope | A coverage claim wearing the shape of a report; on a large scope it consumes the context the findings need. Replaced by a one-line coverage statement. |

### The load-bearing idea, which the first draft did not have

**A finding weighs exactly what the mechanism that produced it weighs.** An exact match (selector defined twice, unimported export, type error, hex outside the token source, hard-wrapped comment) is machine-decidable and may be stated as a verdict and counted. A pattern, shape or naming signal is machine-*locatable* only: the script says "look here", and judgment — not the script — rules. Merging the two is what produces confident nonsense in strict-audit mode, where the register itself pressures the agent toward certainty.

Three consequences are written as rules: a SUGGESTED item never appears as a verdict, never enters a violations total, never carries an imperative; a CERTAIN item always carries `path:line` plus the producing command; and detector silence is never evidence of cleanliness for anything the detector cannot see.

### Scope, per the owner's restatement

Two scopes, declared in one line before any finding: *project-wide*, or *change-related*. The second is defined as the diff **union its callers** — a change scope without the callers is a diff, and the defect a change introduces usually lands in the file that was not touched.

## Decision

**Action.** `METHOD-zero-trust-audit.md` rewritten as a read-only, mechanical-first audit method in six groups: A Scope-lock · B Mechanical pass first · C Evidence classes · D Signature propagation · E Adversarial self-challenge · F Report. Kept from the draft: scope-lock by command rather than by diff, detectors before opinion (and the ban on running a tool afterwards to confirm an already-stated conclusion), signature propagation with the count reported even at zero, the self-challenge pass, and the ban on probabilistic language. The filename and topic address are unchanged — no cross-reference churn.

**Not done:**

- **No new detector script.** `scythe.sh` covers the format cards; everything else this method surfaces is either already covered by an existing rule file's scans (`ui.C1`, `flow`, `release.B`) or is a judgment call by construction.
- **No `/akihelp` row.** The painpoint table is keyed on recurring situations; whether "strict full sweep" is one of them is not yet known. Add it after the method has actually been used.

**Assumption to monitor:** that the CERTAIN/SUGGESTED split survives the register of a strict audit. The failure mode to look for is a report where the SUGGESTED section has quietly acquired imperatives, or where a heuristic-only area is described as clean.

**Cross-references:** `akirule-akiflow-upgrade-aug3.md` (enforcement-tier versus reminder-tier diagnosis) · `akiflow-compliance-enforcement-aug3.md` (prose-worded bans fail; the stash incident) · `ui-css-minimization-aug4.md` (a rule naming a mechanism the stack does not use).
