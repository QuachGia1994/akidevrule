# Plan — /akiflow sized multi-agent pipeline (MVP)

Created: 2026-07-27 · Status: done (executed same day)

## Goal chain

Immediate: a skill that orchestrates specialist subagents (Architect → implement → Reviewer, later Market/UX) with a strict sizing gate. Intermediate: one shared multi-agent workflow across Claude/AG/AGY, usable by future collaborators. Ultimate: akidevrule + akidevsync + dev.akitao.com form the **akidevflow** ecosystem — a packaged, publishable body of AI-agent operating experience.

## Key design decisions

1. **Sizing gate over always-on pipeline.** Tier 0 (direct, default) / Tier 1 (Architect + Reviewer) / Tier 2 (adds business/UX counsel). Signals are structural (schema, public API, ≥3 modules, one-way-door, new feature) — **line-count signals rejected**: calibrated against 60 days of real git activity (839 commits, 21 repos, ~1.1k avg changed lines/commit on content-heavy sites), any line threshold would fire constantly. Ambiguity resolves downward; mid-flight escalation via the deep-think radar rule; user override wins both ways; one-line auditable tier declaration, never a dialog.
2. **Docs are the handoff medium, not transcript.** Each stage closes by writing its doc in the `RULE-docs.md` A2 topology; the next stage reads docs. Chosen because the real workflow is multi-repo burst work (e.g. 96 commits in 10 days then weeks away) — chat context dies between bursts, docs survive. Also makes AG/AGY single-session emulation equivalent by construction.
3. **Roster grounded in corpus files, not persona prompts.** Architect + Reviewer (Tier 1) stand on the existing coding/design/flow files. Market + UX-Psych (Tier 2) were activated in the same pass by writing their foundations first — `RULE-biz.md` (business decision content; process stays in METHOD-deep-think Module 4) and `METHOD-ux-psych.md` (behavior lenses + walkthrough protocol). Division of labor: Market owns external psychology (why a customer buys), UX-Psych owns internal psychology (how the user experiences the flow) and reviews Market's decisions from the user's side.
4. **One SKILL.md, no adapter layer.** install.sh already deploys every `claude/skills/*/` to Claude (`~/.claude/skills`), AG desktop/IDE and AGY (`~/.gemini/config/skills` + skills.json) — a single file is already the cross-harness SSoT. A `payload/AGENT-*.md` extraction is deliberately deferred until a third consumer shape actually appears.
5. **Model/effort by nature of work, not job title**: judgment (architect/review) on top tier + high effort; mechanical fan-out on cheap models with in-shell aggregation; implementation never downgraded to save cost.
6. **Rule injection is explicit**: subagents don't inherit akirule routing, so every subagent prompt lists the exact `~/.aki/claudedoc/*.md` files to Read.

## Scope

- In: `claude/skills/akiflow/SKILL.md`, `payload/RULE-biz.md`, `payload/METHOD-ux-psych.md`, akirule Tier 2 routing + install.sh AG_RULE_MAP for both, index.md manifest, README skills/rules sections, CHANGELOG entries, this plan.
- Out (deferred): `payload/AGENT-*.md` extraction (wait for a third consumer shape); any auto-trigger of `/akiflow` from akirule; dev.akitao.com ecosystem story.

## Acceptance

- `/akiflow` deploys to all three harnesses via `install.sh` with no installer change.
- Skill enforces: one-line tier declaration, downward ambiguity, doc-per-stage, explicit rule-injection lists.
- README/CHANGELOG consistent with the new skill count.
