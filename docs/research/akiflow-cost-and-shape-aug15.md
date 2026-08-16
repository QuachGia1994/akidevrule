# akiflow: the lead is the cost, the gate had one exit, and three published measurements did not reproduce

**Start time:** 2026-08-15

## Initial purpose

The owner asked for an optimization pass over `/akiflow` across five named surfaces, verbatim: *"kiểm tra các thay đổi hiện tại / nghiên cứu kỹ lưỡng / tìm cách tối ưu hơn mọi thứ hiện tại"* — token context, cost (hands / cross-CLI), each agent's own flow, interaction between agents, and chat management. Scope was declared *"tất cả"*.

Context at the time, needed later to judge whether these findings still hold:
- 70 live council rooms under `~/.aki/agent-council/`, 1094 transcripts under `~/.claude/projects/`, both corpora growing during the investigation.
- The Claude Code harness had at some point moved subagent turns out of the main session transcript into `<session-id>/subagents/agent-<id>.jsonl` with a `agent-<id>.meta.json` sidecar. Nothing in the corpus recorded that change; `harness-facts.md` still asserted the old single-file layout from a 2026-07-31 observation.
- The prior investigation of this skill (`akiflow-drift-diagnosis-aug6.md`) had ruled cost out of scope on the owner's instruction. That ruling did not carry into this session — the owner named cost as one of the five surfaces, so cost findings are in scope here and do not contradict the earlier doc.
- Baseline `94f5760` (2.2.1), working tree already carrying uncommitted rule-corpus edits.

## Strategy

1. Measure the live corpora before forming any opinion, since the subject is a skill whose own artifacts are on disk and can be counted rather than argued about.
2. Fix what is mechanically wrong before designing anything new — a broken measurement tool corrupts every judgment made downstream of it.
3. Delegate each independent repair to its own `aki-maker` with an exclusive file set, and keep judgment in the lead.
4. Treat every number that reaches a durable file as a claim requiring its own re-derivation, not as a byproduct of the exploration that produced it.

## Checklist

- [x] Measured per-seat token spend on a real run of this skill's own repair, using `council_cost.py`
- [x] Traced why that script had been reporting a LEAD-only table with no error
- [x] Counted `isSidechain` occurrences across all 1094 transcripts, split by main-session vs subagent file
- [x] Counted whole-file `Read` calls on a council `chat.md` against `council_read.py` invocations across the transcript corpus
- [x] Measured room sizes (count, median, tail) across all 70 live rooms
- [x] Measured debate-turn distribution across all 70 rooms, and durable output within the zero-debate group
- [x] Audited every agent definition's `model` frontmatter against what `SKILL.md` says about tiers
- [x] Re-derived every number already written into `CHANGELOG.md`, `README.md` and `docs/arch/akiflow.md` during this session
- [x] Regression-checked the `get_declared()` fix against all 70 live rooms by isolating the only 2 that can be affected
- [ ] **Not done:** priced the fixes in currency. Token counts are recorded; per-model prices drift and were deliberately not baked into any artifact.
- [ ] **Not done:** verified that dispatch mode improves anything in practice. It is argued from the shape of 70 existing rooms, not from a dispatch run — no dispatch room existed when this was written.

## Result

### A — `council_cost.py` had been silently reporting nothing since the harness changed layout

Step 6 of the skill is mandatory and calls this script, so every run since the layout change closed on a cost table containing only the LEAD row. The script selected subagent turns by filtering `isSidechain: true` out of the **main-session** transcript. Those turns no longer live there.

**Verification.** Across 1094 transcripts the flag appears 71,839 times and **not once** in a main-session file — the filter could only ever have returned empty. Fixed to read `<session-id>/subagents/agent-*.jsonl`, label from the `meta.json` sidecar, and **exit 1 when the session id or transcript cannot be resolved** rather than print a plausible partial table. Verified live against a room with no stamp (exits 1 with the reason), a session with zero subagents (exits 0 with a LEAD-only table, which is the correct answer there), and this session (four rows, three of them concurrent `aki-maker` seats).

Labels deliberately use `agentType` **plus** `description`. Real rooms spawn nearly every seat as `general-purpose`, so `agentType` alone re-creates the same class of silent merge — proven live: the two concurrent `aki-maker` seats in the run that fixed this would have collapsed into one row.

### B — the lead is the cost, not the roster

| | turns | output | cache-read |
|---|---|---|---|
| LEAD (`claude-opus-5`) | 342 | 452,107 | 41,978,401 |
| three `aki-maker` seats (`claude-sonnet-5`) combined | 185 | 232,502 | 18,306,531 |

The lead held **70% of cache-read and 66% of output** while three workers did every file edit. Two earlier snapshots of the same run read 76% / 72% and 74% / 66%; the run measured on 2026-08-12 read 63% / 65%. The share moves as a run proceeds, so the durable claim is the shape rather than any single figure: across four measurements on two runs the lead holds roughly two-thirds to three-quarters of both. Delegation moved the work but not the money.

The mechanism is that **a read is a subscription, not a purchase.** Every turn re-sends the whole history, so a read of size `S` taken at turn `t` of a `T`-turn run is charged about `S × (T − t)`, not `S`. Pulling a 50k-token room at turn 50 of 200 is ~7.5M cache-read tokens from one call — a fifth of the entire lead spend measured above.

**Corroborating measurement.** The corpus shows this is what actually happens: 110 whole-file `Read` calls on a council `chat.md` against 10 invocations of `council_read.py`, with 47 of the 63 transcripts doing it being subagents. Rooms are large enough for it to matter — median 14 KB, 21 of 70 over 30 KB, largest 201 KB.

The root cause was **not** lead laziness. `council_read.py` had `--index`, `--pinned`, `--stats`, `--agent`, `--from` and `--tail` — every one of which narrows by something the reader must already know. The question a lead actually asks, *"did anyone raise X?"*, had no answer short of reading the file. Added `--grep` (matching lines only, each tagged with its turn) and `--turn <n>`; `--stats` gained a bytes column so a read can be priced before it is made. Verified on the 201 KB room: `--grep 'cache'` returns 2 lines where the alternative was ~50k tokens.

### C — a declared tier and an executing tier can disagree in both directions

`aki-hands` is the retrieval seat the skill describes as the cheap tier; its frontmatter declared `model: sonnet`. Corrected to `haiku`.

`SKILL.md` separately instructed that **every** spawn pass `model` explicitly. That is the wrong mechanism: an omitted `model` takes the agent definition's frontmatter first and inherits the caller's tier only when the definition names none. The rule made the frontmatter dead text and the ritual load-bearing, which is backwards — the definition is the single source of truth. The real residual hazard is narrower and now stated as such: a generic subagent such as `general-purpose` carries no tier of its own, which matters concretely at Step 6 where the cost seat needs `Bash` and is spawned generically.

The same audit surfaced `aki-challenger` declaring `sonnet` while `SKILL.md` called for a strong model. The owner ruled against raising the tier — *"không. tốn kém."* — so the guidance was corrected to match the definition rather than the reverse.

### D — the activation gate's only answer for "no" was "leave the skill"

Work failing condition 2 (≥2 kinds of "correct") was routed to bare workers or to the native `Workflow` tool, surrendering the anchor, the quoted requirements, the `[RULES]` receipts, the durable record and the closure gate along with the debate it genuinely did not need. Those were bundled only because one shape had ever been built.

**Verification.** Of 70 live rooms, **19 posted no debate turn at all**, and 11 of those still did substantive work — checklists of 4 to 16 KB, one room with 14 seat files. 13 more posted between one and five turns. Better than a quarter of all sessions were fan-outs wearing council scaffolding, and `--convene` compounded it by refusing to open any room whose items named no challenger.

Added **dispatch**: same workspace, same three file kinds, same closure gate, with lanes carrying an exclusive `writes:` set in place of items carrying an adversary. The shapes die of different things — a council's failure is a decision nobody attacked, a fan-out's is two workers editing one file, which no amount of judgment prevents and which stays invisible until the second write clobbers the first.

Implementing it surfaced one more instance of the session's dominant defect class. The lane seed declares fields as markdown bullets (`- worker: <agent-type>`), while `get_declared()` anchored its match at line start to fit the block-form fields items use — so a lane's worker was invisible to the ghost-seat check, which printed `SKIP ghost-seats: checklist.md declares no owner/challenger`: the check not running, dressed as the check having nothing to find. The agent implementing dispatch found it by testing rather than assuming, and reported the contradiction between two of its own instructions instead of picking one silently. Fixed by tolerating an optional bullet marker — strictly more permissive, so it can only add roster names, never remove them. Of the 70 live rooms exactly 2 use dash-prefixed declared fields; one now correctly FAILs on four seats that left no trace, and neither room's exit code changes.

**Honest cost of this, recorded so a later reader does not have to rediscover it:** dispatch surrenders the self-approval defense that the challenger exists to provide. Wanting an adversary mid-dispatch is the signal that the shape was chosen wrong, not a reason to bolt one on.

### E — three published measurements did not reproduce, and that is the most important finding here

Numbers were written into `CHANGELOG.md`, `README.md` and `docs/arch/akiflow.md` during the session and re-derived afterwards. Three failed:

| Published | Re-derived | Nature of the error |
|---|---|---|
| "876 occurrences of `isSidechain`" | 71,839 occurrences | Counted files, published as occurrences. The load-bearing half — none in a main-session file — held exactly. |
| "199 whole-file reads against ~34 sliced" | 110 against 10 | Different counting rule than the one described. The corrected ratio is *stronger* than the published one. |
| "14 of 70 rooms did real work with zero debate" | 19 zero-debate, 11 substantive | Conflated with an adjacent figure in the same paragraph — one room holding 14 seat files. |

A fourth class behaved differently and is not an error: the seat-label regex counts (`"You are a"` 305 → 325, `red-team` 41 → 45) drifted because the transcript corpus grows continuously. Those were correct when taken. They are now published with the date they were taken and a note that re-running moves them.

The common cause of the three real failures is that each number was a byproduct of an ad-hoc exploratory one-liner, carried by memory into a durable file, and never re-derived from a command that could be re-run. No rule in the corpus currently requires that a measurement written into a durable artifact carry the means of reproducing it; `agent.B2` requires citing a source of truth, which an ad-hoc shell pipeline nominally satisfies while providing none of the protection.

**This finding is self-implicating and that is why it is recorded rather than quietly patched.** A standards repository whose own rule is "do not speculate, separate verified facts from assumptions" published three unverifiable measurements in a single session, in the same artifacts that argue for verification.

## Decision

**Action — materialized in this change set:**
- `skills/akiflow/scripts/council_cost.py` — subagent scan, sidecar labels, loud failure
- `skills/akiflow/scripts/council_read.py` — `--grep`, `--turn`, bytes in `--stats`, `BrokenPipeError` fix
- `skills/akiflow/scripts/council_open.py`, `council_verify.py` — dispatch mode, lane seed, exclusive-`writes:` gate
- `skills/akiflow/SKILL.md` — shape discriminator ahead of the gate, Step 1b dispatch, corrected tier mechanism, read-as-subscription in Step 3
- `skills/akiflow/references/harness-facts.md` — transcript layout corrected and re-dated
- `claude/agents/aki-hands.md` — `model: haiku`
- `docs/arch/akiflow.md` — dispatch rationale, fourth cost consequence, failure mode 12 rewritten
- `CHANGELOG.md`, `README.md`

**No action, stated deliberately:**
- `aki-challenger` stays on `sonnet`. The owner ruled the stronger tier not worth its cost; the documentation was corrected to match reality instead.
- No currency figures anywhere. Token counts are durable, prices are not.

**Follow-up research / proposed, not done — both need owner approval because they touch files that load into every session on every machine:**
- A measurement-reproducibility clause: a number written into a durable artifact carries the command that re-derives it, or it does not go in. Candidate homes are `agent.B2` (corpus-wide) or this repo's own `CLAUDE.md` § Rule authoring principles (repo-local). The evidence is finding E above, at n=3 in one session.
- `agent.A2` currently states that cost follows round-trip count and says nothing about what a single call *loads*. The `S × (T − t)` subscription arithmetic is the missing half and belongs there, not only in a skill.

**Cross-references:**
- `docs/research/akiflow-drift-diagnosis-aug6.md` — the R1 ANCHOR / R2 JUSTIFICATION laws this session did not revisit. Its explicit ruling that cost is out of scope was superseded by the owner in this session, for this session only.
- `docs/arch/akiflow.md` — current-state design record; holds the conclusions, this doc holds the trail.
