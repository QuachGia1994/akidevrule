# Plan: Stop Redundant Owner Interrupts — Asks and Manual-Test Hand-offs

## 1. Problem Statement

Two owner-reported painpoints survived several rounds of rule changes. Both are **delivery failures, not compliance failures**: the governing rule exists but never reaches the agent that produces the violation.

### P1 — Redundant asks

Evidence: council session `~/.aki/agent-council/aiobox/2026.08.18-0439-init-standard-unify/` (Fable 5 lead, Opus 5 judges) produced four owner escalations, recorded as §9 `E-1..E-4` of `docs/plan/INIT-STANDARD-UNIFY-REPO.md` in the aiobox project (the repo-unification plan). The owner's next message called all four self-answerable by a weak model.

Three of the four were raised by **seats** (`judge-ux`, `judge-market`) as `CONFLICT→escalate to owner` inside their own verdict turns; the lead forwarded them. Where the anti-over-asking rules live, and why none of them fired:

| Rule | Read by | Why it did not fire |
|---|---|---|
| `release.B8` "a question the repo already answers is a violation" | `/akiship` runs only | A council run never passes through the release ritual |
| `akiflow/SKILL.md` Step 4 "exactly three things escalate" | the lead only | Seats do not read the skill body; also satisfied to the letter — the lead shipped them as "decisions-with-recommendation", the shape Step 4 explicitly permits |
| `agent.A3` "over-asking is as much a failure as acting unasked" | every session | One general sentence with no checkable test |
| `claude/agents/aki-judge.md` | the seat | Names `agent.B5` (report, never fix) and says nothing about what a seat may push toward the owner |

The four escalations fail three tests the corpus does not currently state:

| Escalation | Fails |
|---|---|
| E-1 sidebar donor | **Impact** — `judge-ux` itself wrote "structural conclusions survive either answer"; the answer changes no artifact |
| E-2 `positioning.md` names no platform | **Silence ≠ contradiction** — a doc that omits X does not conflict with X; that is a one-line work item, not a question |
| E-3 "this run advances no USP clause" | **Already authorized** — asks the owner to re-confirm the course the owner had just ordered |
| E-4 D1 default destination | **Reversibility** — already covered by `agent.A3`, but the seat never read it |

### P2 — Redundant manual-test hand-offs

The anti-over-verification clauses the owner remembers do exist — in `RULE-coding.md` B3 (CHANGELOG: "`coding.B3` gains anti-over-verification clauses aimed at done-gating"), reinforced by `release.B7` step 6 and `akiship` Phase 1. They forbid **gating on the wrong tier** (parking a done-transition on a human for something static reading settles). They say nothing about **repetition**.

Same plan, §7: the owner is handed three separate Mac sessions for one flow — a pre-P0 baseline run, the P0 `clone → launch → back → error-exit` check, and P2's re-run of the same flow post-migration — plus the Windows ledger. Each is individually legal under the current rules. Only the baseline has a stated reason (attributing a later regression).

That the model can reach the right answer unprompted is on record: in the follow-up session `2026.08.18-0534-init-standard-execute`, once pushed with "trọn vẹn", the lead cut the duplicate itself (`LD-2`: "every phase ships to Mac in the same verification batch, so writing it twice buys nothing"). The rule was missing, not the reasoning.

## 2. Target Scope

Root fix in the two core files that load every session (`pattern.A1` — one statement, referenced everywhere else). No rule text is restated at any pointer site.

### 2.1 `payload/RULE-agent-behavior.md` — `A3`, three kill-tests

New bullet after the existing reversibility bullet. Draft wording:

> - **Three kill-tests before any question reaches the user — failing one means answer it yourself and record the answer.** Reversibility (above) is the fourth. **Impact:** if the user answers against your default, does any artifact change? "The conclusion holds either way" is a default to write down, never a question to ask. **Already authorized:** the request may have settled it — asking the user to re-confirm a course they just ordered charges them twice for one decision. **Silence is not contradiction:** a doc that does not mention X does not conflict with X; that is a one-line gap to close, i.e. a work item, not a question. A question dressed as a "decision with a recommendation" still costs a read and an answer — the shape does not exempt it from these tests.

### 2.2 `payload/RULE-coding.md` — `B3`, one hand-off ledger

New bullet after the runtime-check bullet. Draft wording:

> - **When a runtime check genuinely needs a human, hand over one ledger, not one per phase.** Collect every human-run check into a single batch at the end of the run, deduped by flow: the same flow is run once, at its final state. Re-running one flow at several milestones is legitimate only when an earlier run is the baseline that makes a later regression attributable — and that reason is written beside it. Three requests to run one launch-and-navigate flow is not three times the verification, it is three interruptions.

### 2.3 Pointer sites — no restatement

| File | Change |
|---|---|
| `payload/RULE-release.md` `B8` | The "a question the repo already answers" bullet gains "run every candidate through `agent.A3`'s kill-tests first" — one clause, no copy of the tests |
| `skills/akiflow/SKILL.md` Step 4 | State that a seat-raised `CONFLICT` is a candidate, not an escalation: the lead runs it through `agent.A3`'s kill-tests, and only survivors reach the owner. Closes the "decision-with-recommendation" shape loophole |
| `claude/agents/aki-judge.md`, `claude/agents/aki-challenger.md` | One line each: the seat never escalates to the owner; a conflict goes to the lead as `CONFLICT:`, and only after the seat's own impact test — a verdict that holds under either answer is a recorded default, not a conflict |
| `payload/index.md` | New cross-cutting lens row (subject: interrupting the owner — root `agent.A3`, domains `coding.B3` hand-off ledger, `release.B8`, akiflow Step 4); manifest rows for `agent` and `coding` extended with the new items |

`aki-maker`, `aki-hands`, `aki-conduct` need no change: maker already carries `agent.B1`/`B3`, hands already refuses out-of-mandate decisions, conduct judges process and produces no owner questions.

### 2.4 Non-goals

- **No new penalty card** (`[ASK]`). It would be judgment-only like `[FLUFF]`, so `scythe.py` cannot detect it, and it would propagate to `§0`, `README.md`, and the akilint surface for a word the owner already has ("redundant ask"). Fails the `pattern.B3` subtract-first gate.
- **No change to the three-case escalation floors** in `release.B8` and akiflow Step 4. The kill-tests are a filter that runs *before* those floors, not a replacement for them.
- **No edits in the aiobox project.** Its plan is the evidence, not the target.
- **No version minted here** — the bump happens at the release event (`release.A`).

## 3. Implementation Steps

- [x] Step 1: `payload/RULE-agent-behavior.md` — add the `A3` kill-tests bullet (2.1).
- [x] Step 2: `payload/RULE-coding.md` — add the `B3` hand-off ledger bullet (2.2).
- [x] Step 3: `payload/RULE-release.md` — `B8` pointer clause.
- [x] Step 4: `skills/akiflow/SKILL.md` — Step 4 seat-conflict filter.
- [x] Step 5: `claude/agents/aki-judge.md` + `aki-challenger.md` — no-direct-escalation line.
- [x] Step 6: `payload/index.md` — lens row added. Manifest-row extension dropped: executed in the same pass as `trim-resident-rule-context.md`, which collapsed the `agent`/`coding` rows to fixed pointers — a summary of an already-resident file saves no read.
- [x] Step 7: `docs/index.md` — registered directly under `plan/done/` (executed in the registering session).
- [x] Step 8: `CHANGELOG.md` — `[Unreleased]` entry.
- [x] Step 9: `bash install.sh` — propagated; deployed copies diffed clean against source 2026-08-19.
- [x] Step 10: Moved to `docs/plan/done/` 2026-08-19.

## 4. Verification

- **Retrospective test (the load-bearing one):** run `E-1..E-4` through the new `A3` tests — all four must be killed, each by the test named in §1. Static reading settles this; it is what the rules are for.
- **`scythe.py`** over every touched file for `[WRAP]`/`[YAP]`: `python3 ~/.claude/skills/akiflow/scripts/scythe.py <files>`.
- **No restatement:** every pointer site names `agent.A3` and carries no copy of the three tests (`pattern.A1`, repo dogfood rule).
- **Deployed copy matches source** after `install.sh` — diff `~/.aki/akidevrule/RULE-agent-behavior.md` against `payload/`.
- **Unverifiable here, stated as such:** whether a live council seat now withholds a conflict cannot be proven without a future run. First real akiflow session after this ships is the check; no claim of "fixed" before then.

## 5. Execution record — 2026-08-19

Retrospective test passed by static reading: E-1 killed by **Impact** (the seat's own verdict said the conclusion survives either answer), E-2 by **Silence ≠ contradiction**, E-3 by **Already authorized**, E-4 by **Reversibility** (now reachable by the seat via the aki-judge/aki-challenger pointer line). `scythe.py` clean over all nine touched files. No pointer site restates the tests — each names `agent.A3` only. Deployed copies diffed clean after `install.sh`. Open check: first real akiflow run confirms seat behavior.
