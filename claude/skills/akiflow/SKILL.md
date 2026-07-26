---
name: akiflow
description: Sized multi-agent delivery pipeline. A strict sizing gate classifies every request into Tier 0 (direct work, the default), Tier 1 (Architect plan + adversarial Reviewer), or Tier 2 (adds business/UX counsel), then spawns only the specialists that tier needs. Stages hand work to each other through docs/ files (never chat context), each subagent is told exactly which akirule files to Read, and model/effort is assigned by the nature of the work (deep judgment vs mechanical fan-out). Explicit invoke only.
---

# akiflow — sized multi-agent delivery pipeline

Invoke with `/akiflow <request>`, or `/akiflow tier=N <request>` to force a tier. This skill turns the session agent into an **orchestrator** that sizes the request first and only then decides whether specialist subagents are worth spawning. The pipeline must return more than it costs: most requests are Tier 0 and never spawn anyone.

Best run with a top-tier session model (the orchestrator does the gating, integration, and final judgment). If the current model is Haiku or Sonnet, print a one-line recommendation to switch — recommendation only, never a block.

## Step 1 — sizing gate (mandatory, never skipped, never asked about)

Classify the request yourself and declare the result in one line before any other output:

```
[akiflow] tier=1 — trigger: schema change (new table + migration)
```

Never ask the user which tier they want. The gate is auditable through this line, not through a dialog.

**Tier 0 — direct (default).** No signal below matches → no subagents. Work normally under akirule, exactly as without this skill. Bug fixes, copy changes, local refactors, questions and discussion all live here.

**Tier 1 — plan + review (Architect, Reviewer).** ANY single signal fires it:
- A new user-visible capability (new feature), or the user frames it as designing something new.
- The change touches a DB schema/migration, a public API shape, or a project-wide shared convention.
- The change spans ≥3 modules / bounded contexts in one move.
- One-way-door per `METHOD-deep-think.md` A1: hard or expensive to reverse.
- *Auxiliary (weak) signal:* more than ~5 **code** files. Count code only — exclude content, data, and locale files. Changed-line counts are NOT a signal at any threshold: content-heavy projects produce thousand-line commits routinely, and a line-count trigger would fire constantly and meaninglessly.

**Tier 2 — full board (adds business/UX counsel).** ANY single signal fires it:
- A new product, app, site, or business module from scratch.
- A monetization, pricing, positioning, or target-audience decision.
- A brand-new user-facing flow: onboarding, landing, checkout/conversion.
- `docs/biz/` is missing where `RULE-docs.md` A3 requires it, or the requested change contradicts it.

**Operating laws of the gate:**
1. **Ambiguity resolves downward.** When unsure between two tiers, take the lower one. Mid-flight escalation is allowed and expected: any stage that uncovers a higher-tier signal stops and escalates (the radar rule, `METHOD-deep-think.md` C1) — declare the new tier with the same one-line format.
2. **User override wins in both directions.** `tier=N` in the invocation forces that tier; "just do it directly" (or equivalent) forces Tier 0.
3. **Only invite agents that have actual work.** Tier 2 does not mean every specialist runs — a pure pricing decision needs business counsel and an Architect, not a UX pass.
4. **A stage that produced no doc did not run.** Each stage's output is a docs/ file (see handoff protocol); no doc means the stage cannot be marked complete.

## Step 2 — agent roster

Subagents do **not** inherit akirule routing. Every subagent prompt MUST name the exact `~/.aki/claudedoc/*.md` files to Read before working — this replaces the router they don't have.

### Architect (Tier 1+) — strong model, high effort

- **Read first:** `RULE-design-core.md`, `RULE-coding.md`, the matching stack rule (`RULE-stack-akiNuxtCf.md` or `RULE-stack-tauri.md`), and `RULE-db-design.md` when a schema is involved.
- **Input:** the request, `docs/biz/` (when it exists), existing `docs/arch/`.
- **Mission:** decide module boundaries, data shapes, and the execution order. MVP-first and balance-obsessed: SOLID/DRY/bounded-context per design-core, but no over-engineering — every abstraction needs its Rule-of-Three evidence, and the first version must be smaller than the imagined final one. State explicit non-goals.
- **Output:** a plan doc in `docs/plan/` per `RULE-docs.md` B1, including acceptance criteria concrete enough for the Reviewer to check the diff against.

### Implementation (Tier 1+)

In the MVP the **orchestrator itself implements** from the plan doc — it has the session context and the strongest model. Spawn coder subagents only for parallelizable mechanical sub-tasks (bulk renames, repetitive call-site sweeps), at a cheaper model tier, each with its rule-injection list (`RULE-coding.md` + stack rule minimum).

### Reviewer (Tier 1+) — strong model, high effort, adversarial

- **Read first:** `METHOD-flow-audit.md`, `RULE-design-core.md` (§C1 definition of done), `RULE-coding.md` (§B).
- **Input:** the diff, the Architect's plan doc, relevant `docs/arch|feat`.
- **Mission:** cross-check code against plan and docs; hunt flow breaks and artificial guards; verify claims per `RULE-coding.md` B3 — anything only checkable at runtime is reported honestly as "unverified", never papered over. The anti-sycophancy rule applies: the review must contain at least one genuine attack attempt, not a rubber stamp.
- **Output:** review report to the orchestrator, plus a doc-sync check (plan moved to `done/`? arch/feat docs updated? CHANGELOG entry present per `RULE-release.md`?).

### Market (Tier 2) — strong model, medium-high effort

- **Read first:** `RULE-biz.md`, `METHOD-deep-think.md` (Module 4, techbiz lens), `RULE-docs.md` (§A3, the `docs/biz/` backbone).
- **Input:** the request, existing `docs/biz/`, whatever real market evidence exists (never invent data — unverifiable claims are labeled as assumptions per `RULE-agent-behavior.md` B2).
- **Mission:** business counsel — audience, positioning, USP, pricing/monetization shape, and the smallest credible market validation before anything is built (`RULE-biz.md` B3). External-facing psychology (why a customer buys or bounces) is this agent's half; in-product psychology belongs to UX-Psych.
- **Output:** create or update `docs/biz/` — business requirements concrete enough for UX-Psych and the Architect to build against.

### UX-Psych (Tier 2) — strong model, medium-high effort

- **Read first:** `METHOD-ux-psych.md`, `RULE-content-write.md`, `RULE-ui-pattern.md` (fixes must land in the design system), `docs/biz/` (the persona it walks as).
- **Input:** Market's `docs/biz/` output (when Market ran), the flow or interface under design/review.
- **Mission:** internal counsel — take the business requirements and shape or judge the user-facing flow through the psychology lenses: cognitive load, defaults, feedback, friction ledger, failure paths, state completeness. Reviews Market's decisions from the user's side; disagreements go back to the orchestrator, not silently overridden.
- **Output:** a UX spec in `docs/feat/` (new flow) or a severity-weighted audit report (existing flow), per `METHOD-ux-psych.md` §C.

## Step 3 — model & effort strategy

Assign by the **nature of the work, never by job title**:

- **Deep judgment** (architecture, adversarial review, business tradeoffs): top-tier model, high effort.
- **Mechanical fan-out** (inventory scans, reference sweeps, stats aggregation, bulk edits): cheapest capable model, low effort — and instruct it to aggregate in-shell rather than pulling raw data into context.
- **Never put implementation on a cheap model to save cost.** Code quality is created at the keyboard, not recovered in review.

## Handoff protocol — docs, not transcript

Every stage ends by writing or updating its doc in the `RULE-docs.md` A2 topology (`biz/`, `feat/`, `arch/`, `plan/`). The next stage reads the doc, never the previous stage's chat output. This is what makes the pipeline survive session boundaries, multi-repo burst workflows, and human collaborators joining between stages — the transcript evaporates, the docs remain.

## Harness adaptation

- **Claude Code:** spawn stages via the subagent mechanism; run independent stages in parallel.
- **Antigravity / AGY (no subagent tool):** run the same stages sequentially in one session, each stage still opening with its rule-injection Reads and closing with its doc. The docs handoff makes single-session emulation equivalent by construction.

## Invocation scope

Explicit-invoke only — akirule never auto-triggers this skill. When ordinary work makes a Tier 1/2 signal obvious, suggest `/akiflow` in a single line (radar-style); do not self-invoke.
