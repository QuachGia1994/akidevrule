# Headless CLI workers vs. the native Workflow tool — how akiflow should buy bandwidth

**Start time:** 2026-08-01

## Initial purpose

akiflow buys extra reasoning bandwidth by spawning Claude Code subagents. Everything it spends is therefore charged to one vendor, on one quota, at one CLI's capabilities. Three pieces of new context arrived at once and put that assumption in question:

1. `agy` (Antigravity CLI) ships `/teamwork-preview`, a built-in fixed-roster agent council.
2. Claude Code ships a native `Workflow` tool (`/workflows`) for deterministic multi-agent orchestration.
3. A Claude subagent can invoke *other* CLIs headlessly (`agy -p`, and per the owner `kiro-cli chat --no-interactive`), reaching cheap, fast models on someone else's quota.

**Question:** should akiflow's Phase B (execution/verification) move onto the native `Workflow` tool, onto headless cross-CLI workers, both, or neither?

**Context at the time — the constraints that make this answer expire:** Claude Code 2.1.220; `agy` 1.1.9; `kiro-cli` not installed on this machine; akiflow at 18 anti-patterns with Phase A (analysis, `SendMessage` roster) and Phase B (execution) separated by a decision gate, and a Step 8 loop-back that lets a failed verification reopen a work item back into Phase A. This repo distributes skills to five CLIs, not only Claude Code.

## Strategy

Verify by direct execution and binary inspection rather than by documentation, because every relevant surface here is either undocumented or version-bound. Specifically: run each CLI's `--help` and live calls; read the `Workflow` tool contract for what it structurally *cannot* do; then judge adoption against akiflow's existing invariants rather than against the features' attractiveness.

## Checklist

1. Read the `Workflow` tool contract — capabilities, and the boundaries it does not cross.
2. Inventory which CLIs are actually installed here (`agy`, `claude`, `kiro`, `codex`, `grok`, `gemini`).
3. Run `claude --help` and `agy --help` in full; extract every flag that changes cost, scope, or output shape.
4. Run live headless calls and measure: wall time, token usage, failure modes.
5. Test `claude --bare` specifically, as the largest advertised input-token cut.
6. List `agy models` for cross-vendor model availability.
7. Judge each candidate mechanism against akiflow's Step 8 loop-back and against the repo's cross-CLI distribution goal.

## Result

### R1 — The Workflow tool cannot host anything that can reopen a work item

Workflow agents have no `SendMessage`. A workflow therefore cannot reach the live Phase A roster. Putting Phase B inside a workflow would sever Step 8's loop-back: a verification failure would have nowhere to send the item back to. This is structural, not a configuration gap.

**Verification:** read directly from the `Workflow` tool contract, which lists the agent capabilities available inside a script; `SendMessage` is absent, and the contract describes subagent returns as final text/structured values, not conversations.

### R2 — Workflow's two genuinely unique features are both available as headless flags

The only Workflow capabilities that akiflow lacks and would benefit from were a hard preventive spend cap and enforced structured output. Both exist on the CLI:

| Want | Workflow | Also available headless |
|---|---|---|
| Hard budget cap that throws | `budget.remaining()` | `claude --max-budget-usd` |
| Enforced output shape | `schema` option | `claude --json-schema`, `agy --json-schema` |
| Crash resume | `resumeFromRunId` + `journal.jsonl` | *no headless equivalent* — genuinely Workflow-only |

**Verification:** `claude --help` and `agy --help`, read 2026-08-01. Crash resume has no equivalent and remains a real, unreplaced loss.

### R3 — Adoption cost is structurally worse than the feature gain

- Workflow is Claude Code-only; this repo ships skills to five CLIs.
- Workflow cannot be self-invoked — the owner must explicitly opt in per task. A skill branch that depends on it is dormant by default.
- A named workflow wants a new deploy surface (`.claude/workflows/`); a script passed by `scriptPath` avoids that, but the branch still has to be maintained and kept true.

**Verification:** opt-in gating is stated in the tool contract; the deploy-surface consequence follows from `install.sh`'s current targets.

### R4 — Cross-CLI headless workers deliver the same bandwidth with none of that cost

Measured live, 2026-08-01:

- `agy --model gemini-3.6-flash-low --mode plan --output-format json -p "<prompt>"` → 2.5s for a trivial call, 8.2s wall / 3.4s model on a real read-only repo sweep. Fixed overhead ~20–26k input tokens per call (agy's system prompt plus `~/.gemini/GEMINI.md`); one repeat call in the same conversation showed `cache_read_tokens: 32621`, which was initially read as "repeat calls hit a warm cache" — **R10 below overturns that reading**, so this line stands only as the observation, not the conclusion drawn from it.
- No permission prompt was raised, contradicting an earlier assumption in this investigation that `~/.claude/settings.json` would need a `Bash(agy *)` entry. **That assumption was wrong and is retracted.**
- `--mode plan` enforces read-only by mechanism; `~/.gemini/GEMINI.md` carries the akirule behavior floor into every call for free.
- Flag order is load-bearing: `-p` takes the prompt as its value, so it must come **last**. Violating this returns a confident, unrelated answer with **no error** — hit during this research.

**Verification:** live runs, output JSON captured. The flag-order trap was reproduced.

### R5 — Which vendor pays is a separate axis from which model reasons

`agy models` (2026-08-01) includes `claude-sonnet-4-6` and `claude-opus-4-6-thinking` alongside the Gemini and `gpt-oss-120b` tiers. A Claude-family model is reachable on the Antigravity quota. akiflow's Step 2 mechanism table previously assumed model tier and quota were the same choice.

### R6 — `claude --bare` is the largest Claude-side cut and is unusable on this machine

`--bare` skips hooks, LSP, plugin sync, attribution, auto-memory, prefetches, keychain reads, and CLAUDE.md auto-discovery — but auth becomes strictly `ANTHROPIC_API_KEY` or `apiKeyHelper`; OAuth is never read.

**Verification:** live call returned `is_error: true`, `terminal_reason: "api_error"`, zero tokens on this OAuth-only machine. Confirmed unusable here without a separate API key.

### R7 — `--tools` is the Claude-side equivalent of `--mode plan`

`claude --tools "Read,Grep"` restricts the session to named built-in tools (`""` disables all). This is read-only enforced by mechanism rather than by prompt wording — the counterpart akiflow's Claude-side sweeps were missing.

### R8 — Only two of the five target CLIs are installed here

`agy` and `claude` are present. `kiro`, `codex`, `grok`, `gemini` are not; their `~/.kiro/skills`-style directories exist only because `install.sh` creates them. The multi-CLI worker idea is currently realizable with two CLIs, not five.

### R9 — Kiro CLI capabilities, owner-supplied and unverified

Recorded in `skills/akiflow/references/harness-facts.md` under an explicit `[owner]` marker: `chat --no-interactive`, `--trust-tools=` for mechanism-enforced scope, `--require-mcp-startup` with exit code 3, a model table with cost multipliers down to ×0.05 (`qwen3-coder-next`, 256k context), built-in `kiro_planner`/`kiro_help` subagents, `--agent-engine v1|v2|v3`, and `kiro-cli acp` exposing Kiro as an Agent Client Protocol server.

**Verification: none.** Not installed here, not checkable here. If accurate, Kiro is both the cheapest bandwidth tier in the stack and the only one exposing a machine protocol rather than a text CLI — which is exactly why it must be verified before a rule leans on it.

### R10 — Both CLIs offer a stateful worker; only one is usable

Prompted by the owner pointing out that `--conversation` / `--session-id` existed and had not been investigated. They were right, and the result changed the design.

Controlled 3-turn test: store a token, ask for it back, send a trivial third turn. **Both recalled the token correctly**, so both functionally resume. The economics diverge completely:

| | `agy --conversation <id>` | `claude -p --session-id <uuid>` |
|---|---|---|
| Turn 1 | 26.5k input, 2.6s | $0.0358 (16.9k cache-create, 17.5k cache-read) |
| Turn 2 | 53.6k input, `cache_read_tokens: 0`, 8.8s | **$0.0043** (34.4k cache-read, 219 new) |
| Turn 3, trivial prompt | 56.4k input, 24.5k cache-read, **57.6s** | $0.0038 (34.6k cache-read, 90 new) |
| Scope | id resolves globally | **cwd-scoped**; other directory → `No conversation found`, exit 5 |

**Verification:** live runs, JSON captured for each turn. This also **corrects** an earlier `[obs]` in `harness-facts.md` that read one `cache_read_tokens: 32621` observation as evidence agy repeat calls hit a warm cache — the controlled test shows the cache is intermittent and the latency curve, not the cache, is the binding constraint.

**Consequences:** `claude -p --session-id` is the persistent-worker mechanism akiflow lacked — cheap after turn 1, flat thereafter, and surviving between top-level sessions in a way a fork never does. Its cwd-scoping is a safety property. agy stays valuable but strictly one-shot: fast, wide-context discovery, never a conversation.

### R11 — The counter-argument for adopting Workflow, stated at its strongest, and why it still loses

Honest steelman: on a large mechanical sweep — say 200 files needing the same transform plus verification — a workflow holds the loop in JavaScript, *outside any model's context*. The lead's context does not grow with the item count. akiflow's Agent-tool fan-out cannot do this; results accumulate in the lead.

Why it loses anyway: that shape is not a council. It needs no roster, no arbitration, no Phase A. The owner can invoke `Workflow` directly for it, and akiflow does not need to own the capability to route toward it. Buying a permanently-dormant, single-CLI branch to cover a case that is better served by *not opening a council* is a bad trade.

**This is recorded because the research tried to justify adoption and failed to.** The steelman is preserved so a future reader does not mistake the rejection for a lack of investigation, and can re-open it if the constraints change — specifically if crash-resume (R2) ever becomes load-bearing, or if Workflow gains agent-to-agent messaging (R1).

## Decision

**Rejected/closed — the native `Workflow` tool is not adopted by akiflow.** No replacement branch; the council keeps its existing mechanisms.

**Action — cross-CLI headless workers are adopted** as a Step 2 mechanism, with the retrieval-only judgment ban attached:
- `skills/akiflow/SKILL.md` — Step 2 mechanism row, Step 9 cross-CLI spend note, anti-patterns #16–18.
- `skills/akiflow/references/harness-facts.md` — § Cross-CLI worker, § Headless (per-CLI cost levers), § Antigravity / AGY, `[owner]` marker introduced for R9.
- `docs/arch/akiflow.md` — § Convergent validation, § A second axis: which vendor pays.

**Action — four Workflow design lessons adopted as doctrine without the tool**, because they cost nothing and are portable to every CLI: do not make the whole roster wait on the slowest member when the next step does not need everyone's result; a truncated scope must be stated, never silently applied; unknown-size discovery loops until two consecutive rounds find nothing new rather than stopping at a fixed count; and adversarial verification assigns each verifier a distinct lens instead of asking several agents the same question.

**No action — `claude --bare`** (R6): unusable on the owner's OAuth-only setup, so no rule may depend on it. Recorded rather than adopted.

**No action — Kiro integration** (R9): unverified. The facts are filed under `[owner]`; adoption waits on a machine that has it installed.

**Action — stateful-worker findings applied** (R10): `SKILL.md` Step 2 persistent-worker and one-shot-discovery rows; `RULE-agent-behavior.md` A5; `harness-facts.md` § Stateful workers.

**Follow-up needed — verify Kiro CLI** on a machine where it exists, then decide whether the ×0.05 tier and the ACP server change the Step 2 mechanism table.

### Cross-references

- `skills/akiflow/SKILL.md` — the runnable contract these decisions modify
- `skills/akiflow/references/harness-facts.md` — the fact rows this doc is the narrative for
- `docs/arch/akiflow.md` — design reasoning, including the convergent-validation finding from `agy`'s built-in council
- `skills/akiflow/scripts/council-cost.sh` — deliberately **not** extended to capture agy's `usage`; no convention for recording those numbers exists in this repo yet, so the gap is documented in Step 9 instead of guessed at
