# Plan — rule-load receipt, a native agent layer, and the akiflow reduction

**Status:** ✅ **all three batches approved and landed, 2026-08-07.** The owner reviewed the full detail and answered *"đồng ý"*, adding one requirement to Batch 2 — that `aki-hands` name the cross-CLI lanes (`agy`, `kiro-cli`, `cl-9rt`) with a pointer to the recorded harness facts so they are not re-probed, and say per lane which context and rule files must be passed. That requirement is implemented in `claude/agents/aki-hands.md` § Substrates.

**Finding record:** [`docs/research/akiflow-drift-diagnosis-aug6.md`](../../research/akiflow-drift-diagnosis-aug6.md) — why two council sessions answered the wrong question, the 2 roots, the measurement that killed one proposed change, and the decisions already locked.

**Baseline:** commit `54a9007`, working tree 16 modified / 7 untracked. The owner declared that tree **disposable** — do not preserve it, do not reconcile it, do not treat a conflict with it as a blocker.

## How to resume this work in a later session

1. Read the research doc above for *why*; read this doc for *what*. Neither requires the original transcripts.
2. Check the batch table below for what is approved and what has already landed.
3. Every batch edits files under `/home/guest/aki/AkiDevRule/` (the **source** repo). Never edit `~/.aki/akidevrule` or `~/.claude/skills` — they are overwritten by `bash install.sh`, which is the last step of every batch.
4. This repo's own `CLAUDE.md` lists the mandatory companion updates (`README.md`, `CHANGELOG.md`, `payload/index.md`, `skills/akihelp/SKILL.md`). They are already written into each batch below; do not treat them as optional cleanup.

## The two laws every change below serves

| Law | Statement |
|---|---|
| **R1 — ANCHOR** | The owner's words are immutable and are the final test: content, the mechanism they named, and the shape of the answer. |
| **R2 — JUSTIFICATION** | Every mechanism is OFF by default and turns on only when this run produces a reason. Being documented is not a reason. |

## Batch status

| Batch | Scope | Depends on | Approved | Landed |
|---|---|---|---|---|
| 1 | Rule-load receipt + no-self-attestation clause | — | ☑ | ☑ |
| 2 | `claude/agents/` — five native agent definitions | 1 | ☑ | ☑ |
| 3 | akiflow reduction: SKILL.md, `council-open.sh`, `council-verify.sh` | 2 | ☑ | ☑ |

**Verification actually run:** the five definitions land in `~/.claude/agents/` and a pre-existing unrelated agent file in that directory survived the install · the new `council-verify.sh` **fails both archived 2026-08-06 sessions** (no anchor block, no quoted REQ fragments, no `[RULES]` receipts, and in the topup session a ghost `lead` seat), while a synthetic well-formed session passes all six checks · `scythe.sh` is clean on every file this work touched.

**Deviation from the plan, stated rather than hidden:** `skills/akiflow/SKILL.md` is **181 lines, not the "<150" this plan specified**. The reduction came from deleting what moved elsewhere, as planned; what remains is content with no other home — the peer-to-peer laws, the workspace contract, the escalation and doctrine write-back rules, the execute-mode mechanism table and the scheduling laws. Cutting further would have meant trimming load-bearing text to hit a number, which `agent.A4` forbids in the same breath as it forbids padding. If 150 is a real constraint rather than a proxy for "remove the duplication", the next removals to consider are the anti-pattern list (10 rows, each already stated as a rule earlier in the file) and the harness-notes block (recoverable from `references/harness-facts.md`).

Batch 1 is independently useful and self-contained: once it lands, it starts producing the diagnostic data that makes the later batches verifiable.

---

## Batch 1 — the rule-load receipt

**Problem it fixes:** an agent that breaks a rule cannot be diagnosed, because "the rule never reached it" and "the rule reached it and was ignored" have the same signature and opposite fixes. A partial mechanism already exists (`skills/akirule/SKILL.md:133-138`) and is designed to be silent in exactly the case that matters.

### The receipt format

```
[RULES] agent,coding,design (core) + docs,ui (router) | missing: none
```

| Element | Rule |
|---|---|
| Names | the topic address — filename minus the `RULE-`/`METHOD-` prefix and `.md`, per the addressing scheme in `payload/index.md`. Reuses existing vocabulary; introduces none. |
| `(core)` | the four `@`-imported files. Always listed, even though the router did not load them — their presence is currently unobservable and they are the most-violated group. |
| `(router)` | files the `akirule` skill loaded this turn. |
| `(brief)` | files a spawning prompt named and the agent read. Workers use this instead of `(router)`; a worker inherits no router. |
| `missing:` | any file that was required and could not be read, else `none`. This is the field the whole mechanism exists for. |
| Nothing at all | `[RULES] none | missing: agent` — the loudest and most important case, currently invisible. |

### Emission rule

| Who | When |
|---|---|
| A worker / subagent | **always**, as the first line of its output — it has exactly one round |
| The session agent | **mandatory on its first response of the session**, and again on any turn where the set changes |

A later turn with no line therefore carries exactly one meaning — unchanged since the last line printed. That is what removes today's three-way ambiguity without printing an identical line on every turn. Note for a future reviewer: if this proves too weak in practice, the stricter variant is "every turn, every agent" and it is a one-line change.

### Edits

| File | Change |
|---|---|
| `payload/RULE-agent-behavior.md` · **A5** | Add the return leg to the existing worker-delegation rule. A5 already says *"A worker inherits nothing — name the exact rule files it must read"*; add that the worker must report back which of them it actually got, in the format above, as the first line of its output. This is one existing rule gaining its missing direction — not a new item. |
| `payload/RULE-agent-behavior.md` · **B2** | Add to "Verification and claims": naming a rule is not complying with it, and a rule address in your output carries zero evidentiary weight — state compliance only as a checkable fact (`read-only: --tools Read,Grep`; `git mutations: none`), never as allegiance. Currently this exists only inside `skills/akiflow/SKILL.md:284`, where only council seats ever see it, though it is true of every agent in every session. |
| `skills/akirule/SKILL.md` · **Load confirmation** (replaces lines 133-138) | Rewrite so the line is mandatory rather than conditional: delete *"Nothing loaded: no output needed"*, delete the prohibition on listing core `@`-imported files, and adopt the unified `[RULES]` format. Keep the Tier 2 full-load variant. State plainly why silence is forbidden: a missing line is indistinguishable from a router that never ran, which is the failure this line exists to detect. |
| `payload/index.md` | The `agent` manifest row gains the receipt in its summary; no group renumbering, no address changes. |
| `README.md` | "What you get" / manifest sections wherever the A5 change makes them stale. |
| `CHANGELOG.md` | Mandatory for any `payload/` or `skills/` change. |

**Do not** add a new rule file, a new penalty card, a new script, or a hook for this. The receipt is self-reported and is therefore a **diagnostic signal, never evidence** — building enforcement on it would recreate the compliance theater this whole effort is removing.

**Verification for this batch:** run `bash install.sh`, then start a session and confirm the first response carries a `[RULES]` line naming the four core files. A session that emits nothing is the batch failing, not the agent.

---

## Batch 2 — `claude/agents/`, five native definitions

**Why this layer exists:** a seat has been convened by job title and then handed rules. The correct order is the inverse — an agent **is** a system prompt plus a rule set, and a name with no distinct filter behind it is a rule demanding a salary. Putting the definition in the vendor's own format makes three properties mechanical that have only ever been prose: read-only enforcement, model tier, and the fact that an undefined seat cannot be convened at all.

**Location decision (locked, with its reopen trigger):** `claude/agents/`, deployed to `~/.claude/agents/`. Not a top-level vendor-neutral `agents/` — `SKILL.md` is an open standard with five implementations, an agent-definition format currently has one, and `CLAUDE.md:16` already defines `claude/` as Claude Code-only runtime assets. Reopens the moment a second CLI publishes an agent format, at which point it is promoted and rendered per vendor exactly as `AG_RULE_MAP` already does for rules. Reasoning and pre-mortem are in the research doc.

### The five files

| File | `tools:` | `model:` | Mandate | Rule manifest in its body |
|---|---|---|---|---|
| `claude/agents/aki-hands.md` | Read, Grep, Glob | sonnet | retrieve facts with `file:line`; **judgment forbidden** — an unsupported inference is the one unrecoverable error | `agent` |
| `claude/agents/aki-judge.md` | Read, Grep, Glob | sonnet | judge the artifact against **exactly one** standard, named at spawn | `agent` + the one standard named at spawn |
| `claude/agents/aki-conduct.md` | Read, Grep, Glob, Bash | sonnet | judge the **process**, not the output; separate LOAD-fail from COMPLY-fail; `scythe.sh` is one of its tools | `agent` + `coding.B4` |
| `claude/agents/aki-challenger.md` | Read, Grep, Glob | sonnet | attack the result; always close with *"what can be cut?"* and *"does this answer the anchored words?"* | `agent` + `flow` + `design.C1` |
| `claude/agents/aki-maker.md` | Read, Edit, Write, Bash | sonnet | turn a decision into a diff; the only agent permitted to write | `agent` + `coding` + `design` + domain |

Every body carries, in this order: the mandate in one sentence · the rule manifest it must read · the receipt duty from Batch 1 · its output contract. Nothing else — the thinking floor is not repeated here, because Batch 1 put its only unique clause into `RULE-agent-behavior.md` and the rest already lives in `METHOD-deep-think.md`, `agent.A4`, `agent.C3` and `coding.B4`.

`model:` is a default, overridable at spawn. It is written into the file specifically so a tier is never chosen by improvisation — the failure that forced the owner to kill four seats mid-session.

**Guard against the obvious regression:** a catalog is not a roster. Five files on disk is the easiest possible slide back into picking seats from a menu. The convening rule is unchanged and must be restated in Batch 3: **a seat is convened only when it traces to a requirement in the anchored text.**

### Edits

| File | Change |
|---|---|
| `claude/agents/aki-{hands,judge,conduct,challenger,maker}.md` | new, five files, frontmatter `name` / `description` / `tools` / `model` |
| `install.sh` | deploy `claude/agents/` → `~/.claude/agents/`, per-file and **without** a blanket directory `--delete` — the same reasoning already documented for `sync_aki_skills`: never touch a user's own agents living in the same directory |
| `README.md` | new layer in the layout and "What you get" sections |
| `skills/akihelp/SKILL.md` | a **new deploy surface** is exactly the mechanism change this repo's `CLAUDE.md:43` says must be reflected in akihelp's steps, not merely in the docs |
| `CHANGELOG.md` | mandatory |

**Verification:** `bash install.sh`, confirm the five files land in `~/.claude/agents/`, and confirm a pre-existing unrelated agent file in that directory survives the install.

---

## Batch 3 — the akiflow reduction

Target: `skills/akiflow/SKILL.md` from 435 lines to under 150, by removing what now lives elsewhere rather than by compressing prose.

| File | Change |
|---|---|
| `skills/akiflow/SKILL.md` | **Delete** Step 4's 55-line thinking floor (lines 237-291) — ~70% duplicated `agent.A4`/`agent.C3`/`coding.B4`/`METHOD-deep-think`, and its one unique clause moved to `agent.B2` in Batch 1. **Delete** the inline seat definitions (now `claude/agents/`). **Delete** the standing-seat mandate ("two standing seats on every Tier 1/2 roster") — it is a roster derived from a tier rather than from a requirement, and it is the direct cause of the over-staffing. **Keep and restructure** around: 3 modes (`discuss` / `audit` / `execute`, discriminated by the single question *what changes outside the room*) × the five agents; the lead owning R1 (anchor) and R2 (justification) as its own job description rather than as corpus-wide law; and the convening rule that every seat must trace to a requirement in the anchored text. |
| `skills/akiflow/scripts/council-open.sh` | **Require the owner's verbatim message as an argument** and refuse to open a session without it; write it as the first, immutable block of `chat.md`. This converts pinning from a Step 0 discipline that both sessions skipped into a mechanism whose absence is impossible. |
| `skills/akiflow/scripts/council-verify.sh` | **Remove** the hard requirement that `akirule-enforcer` posted (`council-verify.sh:52-56`) — that check is what forced a seat to exist in a session with nothing to enforce, and it was gamed rather than questioned. **Keep** the ghost-seat check. **Add** three: the anchor block exists and is non-empty · every `REQ-n` line contains a quoted fragment that appears in the anchor block · every agent that posted a turn also emitted a `[RULES]` line. |
| `skills/akiflow/scripts/scythe.sh` | **No content change.** Its position changes only in the documentation: a tool belonging to `aki-conduct`, run at the end of a round and only when the run wrote durable files. It is never a seat and never a gate condition. When it fires, the thing to fix is the brief that permitted the error. |
| `docs/arch/akiflow.md` | current-state design doc; must be rewritten to match, per `docs.A2` (arch holds current state only) |
| `docs/index.md` · `README.md` · `CHANGELOG.md` | mandatory syncs |

**Verification:** re-run `council-verify.sh` against both archived sessions from 2026-08-06. Both must now **fail** — the corpus-review session for having no anchor block, the topup session for REQ lines that quote nothing in the owner's actual message. A gate that passes them has not been fixed.

---

## Deliberately not doing

| Not done | Why |
|---|---|
| Consolidating the four descriptions of when a rule loads into one manifest | measured: zero drift across 18 files × 4 sources, ever. Machinery against a failure that has never happened is the redundant guard this work is removing. Reopens on the first observed drift. |
| A new rule file, penalty card, script or hook for the receipt | the receipt extends one existing rule (`agent.A5`) and fixes one existing mechanism (`akirule` load confirmation). Adding a fifth artifact would fail R2 on its own terms. |
| Enforcement built on the receipt | it is self-reported and can be wrong. Cross-check the agent definition's declared manifest against the emitted line and treat a mismatch as a finding; do not gate on the line's content. |
| Reconciling or evaluating the 16-modified working tree | the owner declared it disposable, and `docs.C1` excludes an unstable baseline from a docs-vs-reality audit. |
| Verifying `agy` agent-definition support | not required by any decision here; the location decision was made so that the answer does not matter either way. |
| Anything about token cost | the owner ruled cost is efficiency, not a design criterion. It must not appear in a gate or justify dropping a legitimate filter. |
