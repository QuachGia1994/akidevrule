# akiflow drift: two council sessions answered the wrong question, and the corpus could not see why

**Start time:** 2026-08-06

## Initial purpose

Two `/akiflow` council sessions ran on 2026-08-06 and both over-staffed a task that did not need a council. The owner's verdict on the second one, verbatim: *"một câu hỏi đơn giản mà ngốn 40% quota ? lại đưa ra một kết luận overthinking và kém thực tế không khách quan?"* and later *"sao lại gom cái gì nữa? tôi đang hỏi từng trang mà? đốt 50% quota chỉ để trả lời và phân tích lạc đề?"*.

The question this research had to answer: what are the **distinct** defects behind that, reduced to the smallest set of root causes that covers all of them — explicitly not "write more rules", since the owner's constraint was that a corpus which keeps growing costs more than it returns and itself causes the context flooding and overthinking it was meant to prevent.

Context at the time, needed to judge whether these findings still hold:
- Baseline commit `54a9007`, with a 16-modified / 7-untracked working tree. The owner declared that tree **disposable** — it is the change set the second council session reviewed, and the drift it failed to catch is what opened this investigation. Do not treat it as a base to preserve.
- `skills/akiflow/SKILL.md` was 435 lines / 62KB, with 9 steps, 2 standing seats, 20 anti-patterns and 3 mandatory scripts.
- Four rule files are `@`-imported core (`index`, `agent`, `coding`, `design`); everything else routes through the `akirule` skill, which runs only if the model chooses to invoke it.
- The owner ruled during the session that **cost is not a design criterion** — *"về cost, không quá quan trọng, nó là thứ không quá quan trọng, chỉ mang tính hiệu suất"*. Any finding here that leans on token cost as justification is out of scope by that ruling.

## Strategy

1. Read both council sessions' durable records and both raw session transcripts, rather than reasoning from the summaries the lead wrote about itself — the suspected defect was precisely that the lead's own summary was the corrupted artifact.
2. Enumerate defects individually first, then collapse to roots. Refuse a root that only groups symptoms by topic instead of by cause.
3. Run a mechanical detector before asserting any structural defect in the repo, so a theoretical problem cannot enter the design as if it were an observed one.
4. Decide open design questions in-session using `METHOD-deep-think.md` (forward/backward critique, pre-mortem) rather than escalating them — the owner explicitly rejected being asked what reasoning could settle.

## Checklist

- [x] Read both council session records: `2026.08.06-1736-topup-router` (6 seat files) and `2026.08.06-1738-review-uncommitted-corpus-changes`
- [x] Read both raw transcripts, including every owner message, to recover the original wording each session was supposed to answer
- [x] Enumerated 24 distinct defects with file/line or transcript-index evidence, then collapsed them to 2 roots
- [x] Measured routing duplication across all 4 places that describe when a rule loads — 18 payload files × 4 descriptions
- [x] Read `skills/akirule/SKILL.md` "Load confirmation" and found the mechanism half-built
- [x] Read `skills/akiflow/SKILL.md` Step 4 thinking floor and decomposed it against the existing corpus
- [x] Read `install.sh` to establish the real deploy surfaces before proposing a new one
- [x] Confirmed the Claude Code agent-definition format (`name`/`description`/`tools`/`model` frontmatter, `~/.claude/agents/`) from the harness's own tool documentation
- [ ] **Not done:** verify whether Antigravity/`agy` supports an agent-definition format. Unverified, and the design does not depend on it.

## Result

### The 24 defects reduce to exactly 2 roots

| Root | Statement | Absorbs |
|---|---|---|
| **R1 — ANCHOR** | What the owner wrote is immutable and is the final test — content, the mechanism they named, and the shape of the answer. The moment the lead paraphrases, the anchor is gone and every seat afterwards inherits the paraphrase. | Off-brief framing, invented problem statement, wrong output shape, re-litigating a mechanism the owner already specified, unauthorised model tier |
| **R2 — JUSTIFICATION** | Every mechanism (seat, check, step, script, rule) is **OFF by default** and turns on only when this run produces a reason. Being documented is not a reason. | Redundant probes, ritual on throwaway artifacts, seats with no surface to act on, the gate script that forced a seat to exist, cost-of-verification exceeding cost-of-failure |

R1 governs the *goal*; R2 governs the *means*. No third law is needed: "redundant check" is R2 applied to behavior, "redundant guard" is R2 applied to code (`coding.C1`), "subtraction" is R2 applied to a repo (`METHOD-subtraction-audit.md`).

### Evidence for R1

| Fact | Source |
|---|---|
| The owner's original message asked for per-site analysis (*"mỗi trang 1 con"*) and a discussion (*"thảo luận với tụi nó"*); the lead's pinned `PROBLEM` block instead described a SePay/D1/wallet/ledger consolidation question. None of those four words appear in the owner's message. | topup transcript owner msg #1 vs `chat.md:5` |
| The lead then loaded `central-star-wallet-architecture.md` as "CRITICAL PRIOR DOCTRINE", locking four seats onto a question the owner never asked. | `chat.md:7` |
| The REQ ledger was paraphrased despite Step 0 requiring it verbatim — in **both** sessions. | `checklist.md:4-8` of each session |
| The owner had to restate the brief twice mid-session and cut the model tier once. | topup transcript owner msgs #3, #13, #15 |
| Nothing in the session could detect this: the closing "did this achieve what was asked" check is written by the lead, and the lead is the party that drifted. | `akiflow/SKILL.md` Step 6 · `checklist.md` ITEM-2 self-scored "yes" |

### Evidence for R2

| Fact | Source |
|---|---|
| `council-verify.sh` fails a session that has no `akirule-enforcer` turn, so the script **forces** the seat to exist regardless of whether anything needs enforcing. | `council-verify.sh:52-56` |
| In the corpus-review session no agent wrote to the repo at all (`files edited: 0`), so the enforcer seat had no compliance surface — and the session's own lead renamed a chat header to make the gate pass rather than concluding the seat did not belong. | that session's `checklist.md:38` and its transcript |
| The enforcer seat spent 53,470 tokens producing 5 REMINDs, all about hard-wrapping and missing evidence tags **inside internal minutes that no one reads again**, while the room was answering the wrong question. | task-notification usage record · `akirule-enforcer.md:7-29` |
| A ~200-word-per-turn rule was violated in 8 of 12 turns and waived in place each time. | `akirule-enforcer.md:31-32` |
| A CLI the owner had already named by model tier was probed three times (`agy --help` twice, `agy models` once) before use, and a different tier was then considered anyway. | topup transcript indices 40, 44, 70 |

### The finding that was not on the list: the corpus cannot observe its own delivery

The owner's framing was the sharper one: *"tôi không control chính xác các agent phạm lỗi đó đã được nạp rule tương ứng hay chưa"*. Two failures wear the same symptom and demand opposite fixes.

| Class | What happened | Where the bug is |
|---|---|---|
| **LOAD-fail** | the rule never entered the agent's context | the delivery path — `akirule` router, `@` import, or the spawning brief |
| **COMPLY-fail** | the rule was in context and was violated | the rule text — unclear, mis-placed, or not enforceable as written |

The corpus has already paid for this blindness once: `core-floor-promotion-aug6.md` records that `RULE-coding.md` and `RULE-design-core.md` were being re-stated by the owner over multiple improvement rounds because they were **never loaded**, not because they were ignored — diagnosed only after several wrong fixes aimed at the compliance class.

A partial mechanism already exists and is designed to be silent in the exact case that matters. `skills/akirule/SKILL.md:133-138` emits `[akirule] +RULE-docs.md` after routing, but:

| Defect | Text responsible | Consequence |
|---|---|---|
| Silence is ambiguous | *"Nothing loaded: no output needed"* | absence of the line means (a) nothing needed, (b) the router never ran, or (c) the agent ignored the instruction — three different bugs, one signature |
| Core imports never reported | *"never list a core `@`-imported file"* | the most-violated rule group is exactly the group whose presence is unobservable |
| Workers excluded | the skill only governs the session agent | a subagent inherits no router, so it emits nothing — and subagents are where the observed violations occurred (`red-team.md` hard-wrapped at 34 sites) |

So this is not a new mechanism to invent. It is an existing one made honest and extended to workers: **the line is mandatory, it reports the full context state rather than this skill's delta, and silence becomes impossible** so that a missing line is itself detectable.

### Measurement that killed a proposed change

"When does a rule load" is described in four places — `payload/index.md`, `skills/akirule/SKILL.md`, the `AG_RULE_MAP` table inside `install.sh`, and `README.md`. A consolidation into one machine-readable manifest was drafted on `design.A1` grounds, then tested before being accepted.

| Check across all 18 payload rule/method files | Result |
|---|---|
| Present in `payload/index.md` | 18/18 |
| Present in `skills/akirule/SKILL.md` | 18/18 |
| Present in `install.sh` `AG_RULE_MAP` | 18/18 |
| Present in `README.md` | 18/18 |
| `AG_RULE_MAP` entries no longer in `payload/` | 0 |

Zero drift, ever. The proposal was therefore **rejected**: building machinery against a failure that has never occurred is the redundant guard this same research is trying to eliminate, and it would have been introduced by the exact reasoning R2 forbids. The load receipt above independently covers the residual risk — a rule that silently stops being delivered surfaces as a `missing:` field.

### The minimum agent set

Seats had been convened by job title and then given rules. The correct order is the inverse: an agent **is** a (system prompt + rule set); a name with no distinct filter behind it is a rule demanding a salary. The survival test is one question — *can this filter return a verdict against the lead's conclusion?* If yes it needs its own head, because its reasoning must not be contaminated by the lead's. If it can be checked by reading, it is a rule loaded into whoever is already working.

Applying that test, and merging everything that differs only by a parameter:

| Agent | Tools | Standard of "correct" | Why it cannot be merged |
|---|---|---|---|
| `hands` | Read, Grep, Glob | none — **judgment forbidden** | different mandate (fact vs opinion) and a different price tier |
| `judge` | Read, Grep, Glob | the rule named at spawn (`design`, `proportion`, `ux`, `db`, …) | the four previously-separate judgment seats differed by exactly one parameter, so they are one file |
| `conduct` | Read, Grep, Glob, **Bash** | the corpus itself; `scythe.sh` is one of its tools | different tools (needs Bash) and a different target — it judges the process, not the output |
| `challenger` | Read, Grep, Glob | attacks the result; always closes with *"what can be cut?"* and *"does this answer the anchored words?"* | its defining property is what it is **not** given (the lead's reasoning) — a mechanism, not a mandate |
| `maker` | Read, Edit, Write, Bash | `coding` + `design` + domain | the only agent permitted to write |

Read-only for the first four becomes mechanical (`tools:` omits Edit/Write) rather than a sentence in a prompt, which `agent.A5` already requires and no prompt has ever guaranteed. `model:` living in the definition removes the improvisation that forced the owner to cut a model tier mid-session.

**`akirule-enforcer` survives, and the earlier verdict against it was wrong.** It was killed on the survival test on the grounds that it "only cites"; in fact an unanswered REMIND blocks closure, and closure is the lead's decision, so it does return a verdict against the lead. What actually failed was **R1, not R2**: the seat was pointed at throwaway internal minutes rather than at anything traceable to a requirement. Folded into the universal pattern it is simply `judge` with the corpus as its standard and Bash in its toolbox — which is also what the owner independently concluded (*"cái scythe bản chất chỉ là công cụ của nó"*). With the load receipt it gains the function nothing else in the system can perform: separating LOAD-fail from COMPLY-fail, which converts every violation into a bug report against a named file.

### Where the akiflow thinking floor actually belongs

`akiflow/SKILL.md:237-291` pastes a 55-line thinking floor into every subagent. Decomposed against the corpus:

| Part | Status |
|---|---|
| FACT/CONSTRAINT/ASSUMPTION tagging, self-attack before delivering | already `METHOD-deep-think.md` B2/B3 |
| output hygiene, one line per paragraph, deletion test, comment budget | already `agent.A4`, `agent.C3`, `coding.B4` |
| stay-in-mandate, report shape | council-specific, belongs in the agent definitions |
| **"Naming a rule is not complying with it; a rule address in your output carries zero evidentiary weight"** | **not in the corpus anywhere**, and universal — it is true of every agent in every session, not only council seats |

That last clause is the only genuinely new and genuinely universal content in the floor, and it is the natural companion to the load receipt: the receipt states what was loaded as a checkable fact, and this clause forbids substituting a citation for compliance.

### Decision: `agents/` lives under `claude/`

Forward case for a top-level vendor-neutral `agents/`: the repo already syncs to five CLI skill roots, and `skills/` proves the value of a neutral source with per-vendor adaptation at install time.

Backward case, which wins: `SKILL.md` is a **published open standard with five independent implementations**; an agent-definition format is currently implemented by exactly one vendor. Building a neutral abstraction over one occurrence is the speculative generality `design.A2` forbids, and `CLAUDE.md:16` already defines `claude/` as "Claude Code-only runtime assets", which is precisely what this is today.

Pre-mortem: if `agy` later ships an agent format, the correction is one `git mv` plus a few lines in `install.sh` — a two-way door. The opposite error leaves a permanent neutral layer with one consumer, which is the failure mode R2 exists to prevent. **Reopen trigger:** a second CLI publishing an agent-definition format promotes `claude/agents/` to a top-level `agents/` rendered per vendor, exactly as `AG_RULE_MAP` already renders rules for Antigravity.

### Owner rulings recorded during this session

These are constraints on any follow-up work, not findings:

- Cost is efficiency, not a design criterion; it must not appear in a gate and must not justify dropping a legitimate filter.
- `scythe.sh` exists because the upstream constraints were too weak to prevent the errors it detects. It is a last-pass tool at the end of a round, never a seat and never a gate condition. When it fires, the thing to fix is the brief, not only the file.
- Rules and methods belong to `akirule`; `akiflow` is a consumer of them. Work here improves the whole repo, not one skill.
- A new rule is justified only when it is genuinely unique and a genuinely new pattern or domain. Referencing an existing address is the default.
- Nothing may be implemented until the owner has approved the specific changes.

### Verification

| Claim | How it was established | Status |
|---|---|---|
| Routing has never drifted across the 4 descriptions | script comparing all 18 payload files against all 4 sources | **verified**, mechanical |
| `akirule` load confirmation is silent when nothing loads and excludes core imports | direct read of `skills/akirule/SKILL.md:133-138` | **verified**, quoted |
| The enforcer seat spent 53,470 tokens on 5 REMINDs about internal minutes | task-notification usage block in the topup transcript, cross-read against `akirule-enforcer.md` | **verified** |
| The pinned problem statement diverges from the owner's words | both texts read in full and compared | **verified** |
| Claude Code reads `~/.claude/agents/*.md` with `name`/`description`/`tools`/`model` frontmatter | the running harness's own tool documentation | **verified** by documentation, not by executing an install |
| `agy` supports agent definitions | not attempted | **unverified** — design deliberately does not depend on it |
| The receipt will actually distinguish LOAD-fail from COMPLY-fail in practice | not yet built | **unverified** — self-reported by the agent, therefore a diagnostic signal, never evidence. Cross-check is the agent definition's declared manifest against the emitted line; a mismatch is itself a finding. |
| Quota figures (40%, 50%) | owner's own statements in the transcript | reported, not independently measured |

### Corroborating links

- `core-floor-promotion-aug6.md` — the prior instance of the same blindness, where "rule ignored" was actually "rule never loaded", and the reason the load receipt is not speculative.
- `akiflow-compliance-enforcement-aug3.md` — introduced the `akirule-enforcer` seat and `council-verify.sh`; this record reverses the "standing seat on every Tier 1/2 roster" part of it and the gate's hard enforcer requirement, while keeping its central finding that citation is not compliance.
- `akirule-akiflow-upgrade-aug3.md` — the roster/context-mode upgrade whose standing-seat assumption is superseded here.
- `penalty-cards-scythe-aug4.md` — origin of `scythe.sh`; this record demotes it from gate condition to end-of-round tool without changing its content.
- `proportionality-subtraction-aug6.md` — established that a METHOD file alone is not reusable in akiflow without a seat holding closure authority, which is what the `judge` parameterisation now provides.
- Raw evidence for this record: the two council session directories and both full transcripts, copied to `/home/guest/aki/debug/06Aug-akidevrule/` on this machine (`MAIN-akidevrule-redesign.jsonl` — the redesign session; `REF-topup-council-drift.jsonl` — the drifted topup session). Machine-local and temporary; nothing in this document depends on them remaining.

## Decision

**Action** — [`../plan/done/akiflow-reduction-agent-layer.md`](../plan/done/akiflow-reduction-agent-layer.md) sequences the changes in three batches. Pending owner approval; no file may be modified before that.

**Rejected/closed** — consolidating the four routing descriptions into a single manifest. Measured drift is zero, so the change would add machinery against a failure that has never occurred. Reopens only on the first observed drift.

**No action** — the 16-modified / 7-untracked working tree at `54a9007` is not reconciled or evaluated here. The owner declared it disposable, and `docs.C1` explicitly excludes an unstable baseline from a docs-vs-reality audit; a snapshot of it would expire immediately.

**Follow-up research** — none opened. The two unverified items above (the receipt's real-world discriminating power, and `agy` agent support) are resolved by executing the plan and by observation, not by a further study.

**Cross-references** — `docs/arch/akiflow.md` describes the current council design and must be updated when Batch 3 lands. `docs/index.md` gains entries for this doc and the plan. `README.md` and `CHANGELOG.md` are mandatory syncs per this repo's `CLAUDE.md`.
