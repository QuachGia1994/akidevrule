# Two corpus gaps found by testing the rules against real painpoints

**Start time:** 2026-08-06

## Initial purpose

The owner ran five recurring painpoints against the full corpus (`nạp full`, all 16 files read) to see how each one is actually resolved, then asked for the gaps to be fixed. Context at the time: the corpus had just absorbed the penalty cards, `scythe.sh`, the zero-trust METHOD, and the UI subtraction pass, so enforcement-tier work was fresh and the question was whether any *content* was missing.

The five: (1) verbose docs, (2) unscientific doc naming, (3) CSS pattern sprawl, (4) repeated leaf-patching that never reaches the root flow, (5) overthinking that never asks how many users could realistically reach the state being defended against — quota abuse, client-side hacking, limits.

## Strategy

Walk each painpoint through the actual routing path — which signal fires, which file loads, which numbered item resolves it, what the output contract is — and separate "the rule exists" from "a mechanism makes it run". Then check the two proposed fixes against how akiflow really seats a lens, rather than assuming a file is enough.

## Checklist

1. Full corpus load from `payload/` (source, not the deployed copy); diffed source against `~/.aki/akidevrule` first — identical except `GEMINI.md`, so the reading applies to both.
2. Traced each painpoint to its resolving items.
3. Reported the verdict, then re-researched the two proposed fixes against `skills/akiflow/SKILL.md` before designing them.
4. Wrote both METHOD files and wired every registration site.

## Result

**Painpoints 3 and 4 are fully covered, with real enforcement.** CSS sprawl runs `ui.C1`'s inversion check → five greps → `ui.C2` severity → `ui.C3` matrix → `ui.C4` loop → `ui.C5` scorecard, under `ui.A1`'s subtraction pass and the second-copy STOP. Leaf-patching runs `design.A8` + `design.B2`'s forest pass (whose step 4 is exactly "three patches at one transition → reshape") + `METHOD-flow-audit`'s eight questions and fixed output shape, with `coding.B2` (Chesterton's Fence) at the entrance.

**Painpoints 1 and 2 have correct rules and no mechanism.** Density is `docs.B3` → `agent.A4` → card `[FLUFF]`, which §0 itself declares un-scriptable, so `scythe.sh` never sees it; and unlike `ui.C` there is no playbook for reducing a doc that has already bloated. Naming is `design.A7` → `agent.C1` → `docs.A2`, complete as text, but `docs.C3`'s drift audit checks that index entries resolve, never that a name describes its file — a meaningless name with a live link passes clean.

**Painpoint 5 was a genuine content gap.** The corpus attacks overthinking from several angles — `think.B4`'s red-flag list names the exact phrases, `think.B5` guards both directions (rat-holing on trivial edges *and* hiding a real risk behind "MVP first"), `coding.C1` forbids guards on impossible states — but **every use of "severity" in the corpus (`think.B5`, `ux.C1`, `docs.C4`, `ui.C2`) means impact alone.** Nothing multiplies it by who can actually reach the state. `biz.A1` defines the primary audience and `docs/biz/` is its SSoT, but no rule connects sizing a defense to that population. Consequence: the same question answered twice on different days can get different answers, because the reasoning is unanchored judgment each time.

**Second finding, from re-reading akiflow before building.** A new METHOD file would not have been reusable in the council as the owner intended. `skills/akiflow/SKILL.md` makes judgment specialists **standing domain consults** — any item touching their domain closes only after a recorded turn from that seat, and "nobody asked UX" is a closure defect. A file with no seat is a file the room may consult and therefore forgets. Symmetrically, the subtraction audit must *not* be a council: the same file's bulk-mechanical-work law says a sweep with known paths has nothing to arbitrate and inflates the lead's context, so its scanning routes to workers and the council enters only at classification.

### Verification

Corpus-consistency only; nothing here is runtime-verifiable.
- Source/deployed diff run before reading (identical) and `install.sh` run after wiring, so the deployed copy, the Antigravity generated rules, and the skills all carry the new files.
- Every registration site updated in one pass and re-checked by grep: `payload/index.md` (manifest, group map, two lens rows), `skills/akirule/SKILL.md` (two Tier 1 signal blocks), `skills/akiflow/SKILL.md` (the `risk-sizing` seat and the audit-mode row), `README.md`, `install.sh` `AG_RULE_MAP`, `CHANGELOG.md`.
- **Unverified:** whether the new signal words actually fire in practice. Routing is a model decision, so only real sessions can show it; the same caveat already stated for every Tier 1 entry.

## Decision

**Action — `payload/METHOD-proportionality.md`** (topic `proportion`). Four measures before any verdict (reach against the `docs/biz/` audience, capability ladder, motive, blast radius ordered by recoverability), each labeled measured or estimated. Verdict group: irreversibility outranks frequency; the `coding.C4` / `biz.C3` floor is never sizeable; a cheapest-sufficient-control ladder (impossible by shape → one existing trust boundary → detect and alert → accept and record) with client-side limits classified as UX and never enforcement. Every verdict carries a **reopen trigger** so a deliberate "not now" stays distinguishable from an oversight.

**Action — `payload/METHOD-subtraction-audit.md`** (topic `subtract`). Inherits zero-trust's scope-lock, detector-first order, CERTAIN/SUGGESTED classes and signature propagation; changes only the question to "does this need to exist". States plainly that "as minimal as possible" is not a terminating condition and terminates on two consecutive dry rounds. Nine domain passes delegating detectors to the rule that owns each. Severity classes include a mandatory **load-bearing but ugly** class, because a report listing only removals reads as though everything examined was removable. Chesterton's Fence (`coding.B2`) is the brake: a candidate whose reason cannot be found is SUGGESTED with the reason unknown, never a certain removal.

**Action — `risk-sizing` seated in akiflow** as a standing domain consult at any tier, deliberately opposed to Red Team's subtraction pass: Red Team argues everything down, `risk-sizing` is the only seat that may argue a control back up (on `proportion.B1`) and the only one that may refuse a cut. Neither may touch the security floor.

**No action, recorded with reasons.**
- No detector for `[FLUFF]` and no doc-reduction playbook (painpoints 1–2). Density is content judgment — the same conclusion `penalty-cards-scythe-aug4.md` reached for the scythe, unchanged here — and a doc-shaped `ui.C` would tax every session for a pain the owner has not yet quantified the way the CSS sprawl was measured. Reopens if a measurement shows the size of the problem.
- No name-quality check added to `docs.C3`. A name-versus-content comparison is a judgment call, and the audit's other rows are all mechanical; mixing the two would weaken the row that currently produces reliable findings.
- No new penalty card and no change to the always-loaded core floor.

**Cross-references.** `METHOD-deep-think.md` B5 now hands sizing off rather than settling it (pointer only, no duplicated text). `RULE-coding.md` C1 points at the sizing lens for guards on reachable states. `payload/index.md` gains a **Sizing a control against its real threat** lens row (root `proportion.A`) and lists `subtract` under both the audit-is-read-only and subtraction-before-abstraction rows.

**Follow-up worth watching.** Two new analytical files raise the cost of a `nạp full`; if the corpus keeps growing, the next question is whether Tier 2 should load by topic set rather than everything.
