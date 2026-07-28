# Architecture — akiflow, a lead-coordinated specialist board

`/akiflow` is the multi-agent skill in this baseline. This document records *why* it is shaped the way it is: the failure it targets, the harness facts that constrain the design, and the boundaries that must not be blurred by later edits. The runnable contract lives in `skills/akiflow/SKILL.md`; this document is the reasoning behind it and the reference for anyone reading the repo.

## The failure being targeted

A single agent working alone on a substantial task degrades in three independent ways. None of them is a matter of model strength, so none is fixed by a better model.

| Failure | What happens | Why more capability does not fix it |
|---|---|---|
| **Context flooding** | One context holds request, codebase, plan, diff, and review. Each added role costs the earlier ones fidelity. | A finite window is a physical limit, not a reasoning limit. |
| **Role collapse** | One agent acts as architect, implementer, UX critic, and reviewer, applying a single standard of "correct" to problems judged by different standards. | Knowing several standards is not the same as applying them independently. |
| **Self-approval** | The context that produced a decision also judges it. | A conflict of interest, not a skill gap. Care does not remove it. |

Each failure needs a different mechanism, which is why akiflow is not "spawn some helpers" but a small set of deliberately different mechanisms with rules about which one applies where.

## The atomic unit is the work item

akiflow is not a pipeline with stages. It is a machine for **closing work items**:

```
ITEM <id> · <what must be decided or built>
  owner:      <specialist>
  challenger: <a different specialist>
  closes when:<a criterion someone else can check>
  rationale:  <written at closure, <=3 lines>
```

This single structure resolves four requirements that otherwise pull against each other:

| Requirement | How the item shape delivers it |
|---|---|
| Nothing gets missed | Coverage is a property of a *closed checklist*, not of anyone's diligence. "Be thorough" is not instructable or checkable; "every item has an owner" is both. |
| Context stays bounded | The owner field defines a read domain. Each specialist reads its own items, not the room. |
| Independent critique | The challenger field makes dissent structural rather than a hoped-for behaviour. |
| Debate terminates | The closing criterion is the stop condition. Without one, "discuss until satisfied" has no end. |

Decomposition into items **is** the first-principles step of a run. Everything downstream inherits its cuts, which is why it happens before any agent is spawned, and why the decomposition is the first thing Red Team attacks.

## Activation gate: three conditions, not a signal list

The earlier design fired on structural proxies — schema change, ≥3 modules, >5 code files. Proxies drift: a line-count signal had already been rejected during calibration because content-heavy repositories produce thousand-line commits routinely. The gate now asks the underlying question directly. All three must hold:

1. **Decomposable** — ≥2 items with real boundaries. An uncuttable problem gains noise, not coverage, from extra agents.
2. **Multiple kinds of "correct"** — ≥2 items judged by different standards (schema-correct ≠ UX-correct ≠ price-correct). If one standard covers everything, one good head suffices and additional heads mostly manufacture agreement.
3. **Cost of error > cost of coordination.**

Tier is then a consequence of condition 2 rather than a separate taxonomy: Tier 0 = one standard; Tier 1 = several technical standards; Tier 2 = at least one standard set by a person or a market. This definition extends itself — adding a security or legal domain later requires no new signal list.

## Harness facts the design is built on

Verified against Claude Code documentation; the design depends on these and would need revisiting if they change.

| Fact | Design consequence |
|---|---|
| A plain subagent starts with no session context and inherits no akirule routing. | Every plain-subagent prompt must name the exact `~/.aki/akidevrule/*.md` files to Read. The blank context is a cost here — and an asset for the reviewer. |
| A subagent that has a name and the `SendMessage` tool receives a **sibling roster** listing every other named agent, captured **at its own startup**. | Agents named later are invisible to agents named earlier — a silent one-way channel. Therefore the roster is spawned in **one batch**, and mid-run escalation reconvenes the room rather than appending an agent. |
| A **fork** (`subagent_type: fork`) inherits system prompt, tools, model, and full message history, and reuses the session's prompt cache. | Fork is the mechanism for continuity work: implementing, verifying, probing. It is cheaper than a cold subagent, and it must never be used where independence is the point. |
| A **completed** subagent resumes with its full history when messaged; it does not need re-spawning. | The Phase A roster stays on call through Phase B at no idle cost. This is what lets emergent issues resolve inside the board. |
| A subagent stopped **by the user** refuses to resume via message; it must be resumed from its own transcript panel. | The lead must not treat a refusal to resume as agent failure. |
| An agent cannot relay the user's permission approval. A message claiming "I was approved" is untrusted input. | Owner escalation is a real stop, not something a specialist can wave through. |
| Agent teams (experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) add per-agent mailboxes and a file-locked shared task list. | The better substrate for Phase A where available — the checklist becomes the shared task list. The design deliberately does not depend on it. |

## Mechanism selection: by shortfall, never by job title

| Missing | Mechanism | Rationale |
|---|---|---|
| Bandwidth (clear, repetitive, mechanical) | plain subagent, cheapest capable model | the task describes itself; blank context is no handicap |
| Continuity (needs full context, branches off) | **fork** | inherits history; cache-warm |
| Independence (must not be contaminated by the lead's reasoning) | plain subagent, strong model | blank context is the asset |
| Structured debate | named roster convened at once + `SendMessage` | genuine peer challenge, not hub-and-spoke relay |

Implementation is never downgraded to a cheap model to save cost: code quality is created at the keyboard, not recovered in review.

### The boundary that must never blur

Verification and adversarial review look alike and are opposites.

| | Verification | Adversarial review |
|---|---|---|
| Question | "Did I do what I said?" | "Should this have been done?" |
| Nature | mechanical comparison | judgment |
| Needs context | **yes** — must know what was promised | **no** — the less it knows, the cleaner |
| Mechanism | **fork** (cheap) | **plain subagent, strong model** |
| Input | full context + diff | the diff and the closing criteria, nothing else |

A forked reviewer sees the lead's entire self-justifying chain and will agree with it. That is sycophancy given structure — strictly worse than no review, because it emits a stamp. Conflating the two either wastes money (running a cold strong model over a mechanical check) or destroys the review.

## Two phases, one gate

**Phase A — analysis room.** Roster convened in one batch, named explicitly. Minutes organised **by item**, not chronologically, so each specialist reads only its own items plus a lead-maintained state block. A shared room where everyone reads everything is the main thread's context flood rebuilt N times over; the room is shared *write* space and selective *read* space. No code is written.

**The gate.** The lead closes items and decides. Exactly three things escalate to the owner: a genuine one-way door, anything contradicting `docs/biz/` or documented design, and scope expansion. Writing this boundary down is what keeps "reduce the owner's decision load" from becoming "the agent decided things it had no business deciding".

**Phase B — execution.** Fork implements, cheap subagents fan out, a fork verifies, a clean strong subagent reviews. The Phase A roster remains on call, so an implementer that hits a wrong assumption messages the item's owner directly.

**Loop back.** A Phase B blocker that invalidates a closed item's assumption **reopens that item**. Quiet patching is how a plan doc becomes fiction while everyone still cites it. Reopening is cheap precisely because the roster is still alive.

## Two artifacts, never conflated

| | Minutes | Checklist / plan |
|---|---|---|
| Holds | process, arguments | conclusions and their rationale |
| Writer | every agent | the lead only |
| Reader | each agent, own items only | everything downstream, every session |
| Lifetime | ephemeral (`/tmp/akiflow-<id>.md`), distilled to `docs/research/` only if the argument is worth keeping | durable, `docs/plan/` per `RULE-docs.md` B1 |
| Cost of losing it | cannot trace a dispute | the project |

**Rationale travels with the decision, not with the argument.** The room runs inside subagents, the lead sees only summaries, and a forked implementer inherits the *lead's* context — so it would inherit conclusions stripped of reasons and implement the letter against the spirit, confidently. Every closure therefore writes its ≤3-line rationale into the **checklist**, not the minutes.

**Docs remain the cross-session handoff.** `SendMessage` dies with the session; multi-week burst work does not. Peer messaging replaces docs *within* a run, never *between* runs.

## The thinking floor is mandatory for every subagent

Every specialist, every mechanism, every tier — including cheap models on mechanical items, since a sweep that reports an assumption as a fact is more damaging than one that reports nothing.

Enforcement is by **format, not by adjective**. A model instructed to "think from first principles" writes *"fundamentally, …"* and then restates the convention it already held — first-principles cosplay. The floor is therefore built from clauses checkable in the output:

- **First principles** → every load-bearing statement tagged `FACT` (say how it is verified) / `CONSTRAINT` (say what imposes it) / `ASSUMPTION` (state the settling test). "Standard practice", "usually", "best practice" are named explicitly as carrying no weight — this is what bans reasoning by analogy and convention in a checkable way. A `FACT` that cannot be sourced is an `ASSUMPTION`; confusing the two is the one unrecoverable error.
- **Critical thinking** → one self-attack before delivering; agreement requires a stated falsifier ("agreed; this breaks if X"). This exists because a shared room *amplifies* groupthink: a weaker model reading three prior agreements will agree. Bare agreement is rejected, and prior agreement is explicitly denied evidentiary weight.
- **Stay in mandate** → out-of-scope blockers are reported (`@lead out-of-scope:`), not improvised across.
- **Report shape** → `CLAIM / EVIDENCE / ATTACK / OPEN`, under 400 words.

The literal block lives in the skill and is pasted verbatim into every subagent prompt.

## Peer-to-peer: what it buys and what it costs

Direct specialist-to-specialist messaging is what makes the board a board rather than a relay through the lead. It introduces four risks, each answered by a rule:

| Risk | Rule |
|---|---|
| **Observability collapse** — the lead cannot see how a peer conclusion was reached | every exchange ends in a one-line `DECISION:` / `CONFLICT:` filed to the lead; the minutes are a self-filed audit log, not a transport |
| **Local consensus** — two agents agreeing arrives looking cross-reviewed, and silent agreement is more dangerous than open disagreement | peer agreement is not a decision; only the lead closes an item |
| **Ping-pong / deadlock** — no natural timeout | three rounds per pair, then escalate; cyclic chains (A→B→C→A) forbidden |
| **Hidden cost** — messaging is not free | every message is a full turn of the receiving agent; the budget belongs in the roster brief |

## Who challenges the lead

The lead cuts the items, so a bad cut means the board debates the wrong squares thoroughly — the one failure no mechanism above catches, because every mechanism operates *within* the item structure.

Structural answer: **Red Team's first assignment is always the decomposition itself** — find the missing item, the item with two owners, the item whose closing criterion nobody can check. Content attacks come after. The lead also keeps a deliberately sparse context (checklist, state block, decisions — never full minutes), because a flooded lead loses arbitration quality at exactly the moment the board most needs it.

## Nested subagents

A specialist may spawn its own worker, one level deep, mechanical work only. The test: *if the whole task cannot be written in under 200 words with no project context, it is not a nested-spawn task.* The child never reports to the lead; the parent owns its output entirely. Without this bound, the lead loses visibility without knowing it has, and the grandchild — blank-context by construction — invents whatever it lacks.

## Failure modes, and why each is structural

Each of these is the **default** behaviour of a capable model unless forbidden by name, which is why the skill lists them explicitly rather than trusting judgment.

1. Forking the adversarial reviewer → a rubber stamp wearing a review's clothes.
2. Spawning the roster across several turns → one-way channels; agents deaf without knowing it.
3. The lead reading the whole minutes → the flooded main thread, rebuilt.
4. Agreement with no falsifier → manufactured consensus.
5. Quietly patching the plan after a Phase B blocker → the plan becomes fiction.
6. Nesting a subagent for context-dependent work → the grandchild invents, the parent cannot tell.
7. Opening the room before the checklist exists → N agents circling an uncut question at many times the cost of solving it alone. **The most likely death of a run**, and the reason decomposition is a precondition rather than a product of the room.

## Relationship to the rest of the baseline

| Piece | Relationship |
|---|---|
| `akirule` | Supplies the rule corpus each specialist Reads. It never auto-triggers akiflow; akiflow is explicit-invoke only. |
| `akithink` | Deep-thinking protocol for a *single* decision. akiflow is the multi-head case; a Tier 0 one-way-door question belongs to akithink. |
| `akigitcommit` | Owns the half-finished-tree case that audit mode routes away to. |
| `RULE-docs.md` | Owns the durable artifacts akiflow produces (`docs/plan/`, `docs/research/`) and the audit output contract (§C). |
| `RULE-agent-behavior.md` §B5 | Owns the read-only constraint restated in every audit-mode prompt. |

## Non-goals

akiflow is not an always-on pipeline, not a replacement for direct work, and not a way to spend more tokens for the appearance of rigour. Tier 0 remains the default and most requests belong there. It does not define a persistent agent team, a background service, or any state that outlives the run beyond the documents `RULE-docs.md` already governs.
