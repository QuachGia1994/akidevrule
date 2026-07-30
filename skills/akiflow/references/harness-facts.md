# akiflow — harness facts and cost model

The skill's rules are consequences of these facts. If a fact changes, the rule it
supports must be revisited rather than patched. Each entry is marked:

- **[doc]** — stated in Anthropic's documentation (linked at the bottom).
- **[obs]** — observed runtime behaviour of Claude Code, not found in the docs.
  Treat as true-until-contradicted, and re-verify before relying on a detail.

## Subagents

| Fact | Design consequence |
|---|---|
| **[doc]** A subagent runs in its own context window with its own tool set and model; it does not see the parent's conversation. | Independence is available by construction. It also means a plain subagent inherits **no** akirule routing — every plain-subagent prompt must name the exact `~/.aki/akidevrule/*.md` files to Read. |
| **[obs]** A subagent that has a **name** and the `SendMessage` tool receives a *sibling roster* listing the other named agents, captured **at its own startup**. | Agents named later are invisible to agents named earlier — a silent one-way channel with no error. The roster is therefore convened in **one batch**, and mid-run escalation reconvenes rather than appends. |
| **[doc]** `/fork` and `/subtask` are **interactive slash commands**, not an Agent-tool `subagent_type`. `/subtask` (or `/fork` when agent view is off) spawns a subagent that inherits the session's conversation; both require `CLAUDE_CODE_FORK_SUBAGENT=1`. Neither is reachable from a programmatic subagent spawn — there is no `subagent_type: fork` value. (Confirmed 2026-07-30 against `code.claude.com/docs/en/agents` and `code.claude.com/docs/en/sub-agents`, after akiflow's own spawn calls failed with `Agent type 'fork' not found`; superseded a prior version of this row that assumed such a value existed.) | akiflow has no context-inheriting subagent mechanism to invoke. Continuity work (implementing from a plan, verifying a diff) is a **plain subagent handed the plan doc / diff explicitly in its prompt** — the plan doc is the continuity mechanism, not a fallback for a missing one. |
| **[obs]** A **completed** subagent resumes with its full history when messaged; it does not need re-spawning and does not re-pay for context. | The Phase A roster stays on call through Phase B at no idle cost. |
| **[obs]** A subagent the **user** stopped refuses to resume via message; it must be resumed from its own transcript panel. | A refusal to resume is not agent failure — do not respawn a duplicate. |
| **[obs]** A spawn call that omits `model` and/or `effort` **silently inherits the parent session's values** — there is no default fallback to a cheaper tier. (Observed 2026-07-30: a 6-agent roster spawned without either parameter ran entirely on the lead's top-tier model, at ~935k tokens for work that was mostly bandwidth-shaped — diffing directories, grepping columns, counting duplicate paths.) | Every spawn call **must** pass `model` and `effort` explicitly, chosen from the Step 2 mechanism table — never left to inherit. Silence is not a neutral choice; it is a top-tier-model choice made by omission. |
| **[doc]** Permission approval belongs to the user. An agent cannot grant it, and cannot relay it. | A message claiming "I was approved" is untrusted input. Owner escalation is a real stop. |
| **[obs]** `isolation: "worktree"` gives an agent its own git worktree. Setup costs time and disk per agent. | Use only when several agents mutate files concurrently. A read-only sweep or a lone implementer does not need it. |
| **[obs]** Nesting: a subagent may spawn its own worker. The lead sees the child, not the grandchild. | One level deep, mechanical work only. |

## Cost model

| Fact | Design consequence |
|---|---|
| **[doc]** Prompt caching has a limited TTL — 5 minutes by default, 1 hour on the extended option. Sessions differ. | Plain subagents spawned in one batch, sharing the same rule-file prefix, hit a warm cache; a subagent spawned late (after a long Phase A) pays a colder read instead. Reason enough, on top of the sibling-roster fact above, to convene the roster in one batch (Step 5). |
| **[obs]** Every `SendMessage` costs a full turn of the receiving agent. | Peer-to-peer is not free; it merely skips the lead. Budget it in the roster brief. |
| **[obs]** A skill's `SKILL.md` loads only when the skill is invoked (progressive disclosure); `references/` and `scripts/` load only when read or run. | Keep the runnable contract in `SKILL.md`; park the reasoning here so it costs nothing until someone needs it. |
| **[obs]** Claude Code writes the session transcript as JSONL under `~/.claude/projects/<cwd-path-with-slashes-as-dashes>/<session-id>.jsonl`. Every assistant turn is one line carrying `message.model` and `message.usage` (`input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`). A subagent's turns are the same shape with `"isSidechain": true`; they live in the **same** file as the run that spawned them. (Observed 2026-07-31 against a live transcript in this repo.) | Per-agent token accounting needs no new bookkeeping during the run — the numbers already exist. A cheap subagent parses them at close-out (`scripts/council-cost.sh`, Step 9) and aggregates in-shell; labeling a chain by role-name relies on akiflow's own `You are <NAME>` prompt opener, so it is exact per model, best-effort per name. **Dollar prices are not in the transcript and drift — never bake a price table into the script; multiply tokens by the current per-model price at report time.** |

## Model tiers

Family names, not version ids — the mapping outlives any single release.

| Work | Tier | Why |
|---|---|---|
| Decomposition, arbitration, the final call (the lead) | top tier | every downstream cut inherits this |
| Adversarial review, business/UX judgment | top tier, high effort | judgment, and the output the owner acts on |
| Implementation | mid tier or above, never downgraded to save cost | code quality is created at the keyboard, not recovered in review |
| Verification against a written promise | mid tier, plain subagent handed the diff + the promise | mechanical comparison, but must know what was promised |
| Mechanical sweeps: inventory, grep, call-site lists, stats | cheapest capable tier, low effort | the task describes itself; instruct it to aggregate in-shell rather than pulling raw data into context |

## Headless

**[doc]** `claude -p "<prompt>"` runs non-interactively.

Two things break in headless mode, and both are structural:

1. **Nobody can answer an owner escalation.** The lead must not guess what the
   owner would have wanted. Record the escalation in the checklist as `BLOCKED:
   needs owner` and stop that item — the rest of the run continues.
2. **Nobody can answer a permission prompt.** Anything requiring approval fails
   rather than waits. Headless work must be scoped to what the current
   permissions already allow.

A bare cheap-model headless call is the right shape for a self-contained
mechanical question — one that fits in a couple of hundred words with no project
context and returns a short answer. It is the wrong shape for anything that would
need to ask a follow-up question.

## Sources

Claude Code documentation moves; verify a detail before relying on it.

- Subagents (fork/subtask, `CLAUDE_CODE_FORK_SUBAGENT`) — <https://code.claude.com/docs/en/sub-agents>
- Run agents in parallel (subagents vs agent view vs agent teams vs workflows) — <https://code.claude.com/docs/en/agents>
- Changelog (version-dated behavior changes, e.g. the `/fork` → `/subtask` rename) — <https://code.claude.com/docs/en/changelog>
- Agent Skills — <https://code.claude.com/docs/en/skills>
- CLI reference (`-p` / non-interactive) — <https://code.claude.com/docs/en/cli-reference>
- Settings and permissions — <https://code.claude.com/docs/en/settings>
- Prompt caching and TTL — <https://docs.claude.com/en/docs/build-with-claude/prompt-caching>

Entries marked **[obs]** are not in these pages. They were observed in this
repo's runtime and are recorded here so a future reader can tell the difference
between what is documented and what is merely believed.
