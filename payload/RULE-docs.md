# Core Docs Rules

<!-- Address map: docs.A1-3 · docs.B1-3 -->

## Goals
Docs should be readable for both humans and LLMs.

## A. Index & Structure

### A1. Index
- `docs/index.md` is the master index
- Update it when docs or code changes affect discoverability
- Index entries should be short and descriptive

### A2. Topic folders
Use these short, stable topic folders:

- `docs/biz/` — business backbone: identity, USP, positioning, monetization (MANDATORY for any project with a business dimension)
- `docs/feat/` — features, systems, behaviors
- `docs/arch/` — architecture, structure, technical design
- `docs/plan/` — plans and execution notes
- `docs/ref/` — stable references, setup notes, lookup docs
- `docs/research/` — exploratory, comparative, or time-bound findings

Do not create new top-level doc topics unless the existing set clearly fails.

`biz/`, `feat/`, and `arch/` hold only current/target state — never accumulate history or superseded reasoning (`research/` is where that lives, see B2). Threshold: a rationale that fits in one sentence may stay inline (e.g. `(chose D1 over Postgres — serverless-native, no extra infra)`); a rationale that needs its own strategy, comparison, or verification to be trustworthy belongs in `research/` instead, with the doc here holding only the conclusion and a link.

Filenames across all `docs/*` never lead with a date — the content-identifying name comes first: concise, precise, and unique to that file's own content (short preferred). Record creation/modification dates in the doc's own metadata, not the filename. A compact date suffix (abbreviated month + day, no year, no separator — e.g. `jun24`, `jul27`) may be appended at the very end as a lightweight, optional disambiguator (existing example: `docs/plan/improve-jun24.md`) — separate from the domain-specific supersede-chain naming already defined for `plan/` (B1, version-increment) and `research/` (B2, ADR-style numeric suffix).

### A3. Business backbone — `docs/biz/`
- For any project with a business dimension, `docs/biz/` is REQUIRED and is the spine.
- All `arch/`, `feat/`, and `plan/` docs that touch product direction or money must reference it.
- When code intent and a `biz/` doc disagree, the `biz/` doc wins — reconcile or escalate.

## B. Lifecycle & Sync

### B1. Plan lifecycle & Filename Rules
- Active plans live in `docs/plan/` (or `plan/`)
- Completed plans move to `docs/plan/done/`
- Use `done`, not `archived`, for completed plans
- **Filenames**: see A2 for the repo-wide no-leading-date rule and the optional compact date suffix. Plan docs additionally use version-increment naming when execution can't wait for the plan (e.g. `v2-feature-name.md` or `v1.1-update.md`).
- **Prioritize Creating Plans (`docs/plan/`)**: Always prioritize creating a plan document in `docs/plan/` (or `plan/`) for any code/architectural changes.

### B2. Research doc structure (`docs/research/`)

A research doc is an **immutable event record** — a snapshot of reasoning at the time it was written — never rewritten later (the current-state vs. history split is defined in A2). When its conclusion needs revisiting (recorded context no longer holds), create a **new** research doc and add a `Status: superseded by <path>` line at the top of the old one — never edit the old doc's body. Name the chain with a sequential numeric suffix, ADR-style: `db-engine-choice.md` → `db-engine-choice-2.md` → `db-engine-choice-3.md`, each `superseded by` pointing only at its immediate successor so the chain can be walked backward. Anything outside research that links to it (`arch/feat/biz`) points at the latest number and gets updated each time the chain grows — that edit is allowed because those docs hold current state, not history.

Required fields, in order:
1. **Start time** — when the research began
2. **Initial purpose** — the question/goal, plus the context/constraints at the time (needed later to judge whether the research still holds)
3. **Strategy** — the approach taken
4. **Checklist** — the steps executed
5. **Result** — the finding/conclusion itself, plus:
   - **Verification** — the evidence/method that hardens the result (data, test, cross-check against another case). If not verified, say so explicitly — silence reads as certainty when it isn't.
   - **Corroborating links** — links to the evidence/cases the result rests on or conflicts with (not just a verified/unverified flag)
6. **Decision** — the resolution reached, one of:
   - **Action** — link to the artifact(s) where it materialized (`arch/`, `plan/`, `feat/`, `biz/`, `ref/`, or code/commit); 0 or many. Landing in `ref/` always means a **new** clean lookup doc, never the research doc itself relocated or rewritten into ref format — `ref/` is a distilled answer, research is the narrative trail behind it.
   - **No action** — state why explicitly, so it reads as a deliberate stop, not an abandoned doc
   - **Follow-up research** — link to the new research doc opened by this result
   - **Rejected/closed** — an option eliminated with no replacement; no link needed
   - **Cross-references** — list any other existing docs affected by this decision, beyond the artifact(s) it materialized into

### B3. Documentation behavior
- Keep docs synchronized with code. Code does not auto-generate docs unless complex/requested; when editing code derived from `feat|arch` docs, proactively sync the doc or comment the reference path.
- Comments should not restate what a doc already explains in detail — when the rationale/behavior is complex, or a doc already covers it precisely, comment a reference to that doc (its specific section/heading, not just the whole file, when only part of it applies) instead of duplicating the explanation inline. Keeps the doc as the single source of truth and stops the comment from silently drifting out of sync with it.
- Prefer one clear canonical doc over multiple overlapping docs
- Use Markdown
- Prefer Mermaid when the subject is complex enough that plain text is harder to follow — flows, architecture, state transitions, or pipelines
- README should stay focused on setup and entry-level usage unless the project explicitly wants more
