# Docs index — akidevrule

Master index for this repo's documentation. akidevrule is the source of truth for Aki's reusable Claude Code / Antigravity rule and skill baseline; these docs record its architecture, active plans, and decision history.

Topic folders follow `RULE-docs.A2`. Only the folders that currently hold content are listed.

## `arch/` — architecture & technical design

| Doc | Purpose |
|-----|---------|
| [rule-delivery-architecture.md](arch/rule-delivery-architecture.md) | How one rule source is installed onto a machine and consumed by the two agent families (Claude Code vs Gemini/Antigravity). |
| [akiflow.md](arch/akiflow.md) | Why `/akiflow` is shaped as a lead-coordinated agent council: the two laws the lead owns (anchor, justification), the three single-thread failures it targets, the work item as atomic unit behind an immutable anchor block, modes rather than tiers, the agent layer in `~/.claude/agents/` that replaced the pasted thinking floor, the harness and cost facts the design rests on, the three-file session workspace, the verification-vs-review boundary, and the structural failure modes. |

## `ref/` — stable references & lookup docs

| Doc | Purpose |
|-----|---------|
| [agent-skills-standard.md](ref/agent-skills-standard.md) | Verified: `SKILL.md` is a shared open standard between Claude Code and Antigravity/AGY, zero per-agent transformation — the reason `skills/` moved out of `claude/` to a top-level, agent-neutral folder. |

## `plan/` — active plans

| Doc | Status | Purpose |
|-----|--------|---------|
| [akiflow-reduction-agent-layer.md](plan/akiflow-reduction-agent-layer.md) | ✅ all three batches landed 2026-08-07 | The mandatory `[RULES]` load receipt, a native `claude/agents/` layer of five agent definitions, and the akiflow reduction (435 → 181 lines). Move to `plan/done/` at the next tidy pass. |
| [improve-jun24.md](plan/improve-jun24.md) | ⏳ pending | Keyword-level precision fixes for `akirule/SKILL.md` Tier 2 signal lists. Not yet applied; references the pre-rename `METHOD-techbiz-optimizer.md` and needs revalidation before execution. |

## `plan/done/` — completed plans

| Doc | Purpose |
|-----|---------|
| [antigravity-rule-delivery.md](plan/done/antigravity-rule-delivery.md) | Delivering rules + skills to the Antigravity surfaces (AG Desktop, AG IDE, AGY CLI); replaced the hooks approach. |
| [release-a5-review.md](plan/done/release-a5-review.md) | `RULE-release.md` §A5 — atomic bump+tag+build for Tauri/artifact apps + pre-bump guard. |
| [versioning-principle-rewrite.md](plan/done/versioning-principle-rewrite.md) | Versioning rewrite applied to `RULE-release.md` A4/B1–B3: cold-start reconstruction, severity-driven bump, anti-skip invariant, audit mode. |
| [naming-rule-consolidation.md](plan/done/naming-rule-consolidation.md) | Consolidated naming rules into one callable address (`design.A7` root + domain applications). |
| [akiflow-skill.md](plan/done/akiflow-skill.md) | Original design record for `/akiflow` — sized multi-agent pipeline (3-tier gate, docs-as-handoff, roster grounded in RULE-biz + METHOD-ux-psych), thresholds calibrated against 60 days of real git activity. **Historical:** the skill was later rewritten as a lead-coordinated agent council; current design lives in [arch/akiflow.md](arch/akiflow.md). |
| [density-roster-upgrade.md](plan/done/density-roster-upgrade.md) | Execution record for the 2026-08-03 upgrade: the 11-step edit set across payload/skills/README/CHANGELOG, plus deferred follow-ups (core-floor escalation, GEMINI.md density line, simplifier split). |
| [akiflow-council-rewrite.md](plan/done/akiflow-council-rewrite.md) | Execution record for the `/akiflow` rewrite from specialist board to **agent council**: the six review gaps that triggered it, the nine decisions taken (stated purpose, naming, session workspace, retention-as-script, three artifacts, time-ordered room, steering by judgment, sourced harness facts, cost realism), files touched, and what was and was not verified. |

## `research/` — decision records & exploratory findings

| Doc | Purpose |
|-----|---------|
| [antigravity-rule-discovery-architecture.md](research/antigravity-rule-discovery-architecture.md) | How Antigravity/Gemini natively discovers rule files across its three surfaces; verification-status banner separating confirmed from unconfirmed behavior. |
| [antigravity-claude-skills-native-discovery.md](research/antigravity-claude-skills-native-discovery.md) | Cross-checked whether AG/AGY now reads `~/.claude/skills/` natively (prompted by a local experiment). Two independent sources say no — `~/.gemini/config/skills/` sync stays required. |
| [public-private-abc-restructure.md](research/public-private-abc-restructure.md) | Decision record for the public/private split and the A/B/C group restructure of `payload/`; full item-level breakdown. |
| [versioning-critique-akithink.md](research/versioning-critique-akithink.md) | `/akithink` decision record that critiqued and hardened the versioning rewrite before it was applied. |
| [akithink-akihtmlreport-akihelp.md](research/akithink-akihtmlreport-akihelp.md) | Spec for the akithink / akihtmlreport / akihelp skill expansion. |
| [headless-cli-workers-aug1.md](research/headless-cli-workers-aug1.md) | Measured the headless cost levers of `claude`/`agy`/`kiro-cli` and judged the native `Workflow` tool for akiflow's Phase B. Workflow **rejected** (no agent-to-agent messaging → would sever the Step 8 loop-back; its two unique features turn out to be headless flags); cross-CLI workers adopted instead. Keeps the failed pro-adoption argument on record. |
| [akiflow-compliance-enforcement-aug3.md](research/akiflow-compliance-enforcement-aug3.md) | Evidence from two 2026-08-03 debug sessions that rule failure is enforcement, not content (citation-as-ritual, ghost Red Team, prose-worded git ban → stash disaster; a free-form police seat performed worst) → the reminder-only `akirule-enforcer` seat, the `council-verify.sh` mechanical closure gate, the no-self-attestation floor clause, and the Agent-tool-has-no-effort-parameter correction. |
| [akirule-akiflow-upgrade-aug3.md](research/akirule-akiflow-upgrade-aug3.md) | `/akithink` decision record for the density/MVP-counterweight/roster upgrade: three worst owner pains diagnosed as enforcement-tier failures, not missing rules; deletion-test density lens, Red Team subtraction pass, verifier drift sweep, context modes, proxy-gateway lane, writer role. Records what was rejected (core-floor placement, lint hook, standing drift/simplifier agents) and the assumptions to monitor. |
| [ui-css-minimization-aug4.md](research/ui-css-minimization-aug4.md) | Measured 4 Tailwind v4 projects and found 30,026 lines of bespoke CSS in SFC `<style>` blocks — 3–18× the shared layer — under a rule that calls hand-written CSS "the last resort". Diagnosis: the tier ladder only *packages* repetition and has no rung that removes it; Rule of Three's ≥3 threshold is repo-wide and unobservable inside one editing session; `ui.A2` named a Tailwind v3 mechanism the stack no longer uses; inline `style=` was an unclassified fifth tier. Records three corrections to its own first measurement (pattern layer and tokens do exist), and what was deliberately *not* done — no design-core audit section, no hook, no new penalty card, no new script. |
| [penalty-cards-scythe-aug4.md](research/penalty-cards-scythe-aug4.md) | The owner's severity-restructure proposal researched: renumbering rejected (66 cross-references / 16 files, D3 precedent, reminder-tier fix for an enforcement-tier failure) in favor of §0 penalty cards (`[WRAP]`/`[FLUFF]`/`[YAP]` — one vocabulary across owner corrections, `/akilint`, and the akiflow enforcer) plus the `scythe.sh` deterministic detector with both proposed-algorithm bugs fixed. Records the comment-rot addition to `coding.B4` and the not-re-proposed hook. |
| [proportionality-subtraction-aug6.md](research/proportionality-subtraction-aug6.md) | Five owner painpoints run against the full corpus. CSS sprawl and leaf-patching are fully covered; verbose docs and doc naming have correct rules but no mechanism; **sizing a defense was a real content gap** — every "severity" in the corpus meant impact alone, never multiplied by who can actually reach the state. Adds `METHOD-proportionality.md` and `METHOD-subtraction-audit.md`, plus the finding that a METHOD file alone is not reusable in akiflow without a seat with closure authority. Records what was deliberately not built (a `[FLUFF]` detector, a doc-reduction playbook, a name-quality audit row). |
| [core-floor-promotion-aug6.md](research/core-floor-promotion-aug6.md) | Why the owner kept saying "lại vi phạm akirule": two failure classes under one label. `[WRAP]`/`[YAP]` were violated *with* the rule loaded (compliance); `pattern` was violated because `RULE-coding.md` and `RULE-design-core.md` were labelled "default ON" while routing through a skill the model must first choose to invoke — so they were often never in context at all. Promotes both to `@` imports (four core files), reversing `akirule-akiflow-upgrade-aug3.md` three days early on its own falsifier. Records the accepted context cost, why Antigravity keeps them at `model_decision`, why `RULE-ui-pattern.md` was not promoted, and the still-open compliance class. |
| [akiflow-drift-diagnosis-aug6.md](research/akiflow-drift-diagnosis-aug6.md) | Why two `/akiflow` council sessions on 2026-08-06 answered a question the owner never asked. 24 distinct defects reduce to two roots — the anchor (the owner's words are immutable and are the final test) and justification (every mechanism is OFF until this run earns it). Records the finding the defect list missed: the corpus cannot observe its own delivery, so "rule never loaded" and "rule loaded and ignored" are indistinguishable — and `akirule`'s existing load confirmation is designed to be silent in exactly that case. Kills its own SSoT-consolidation proposal on a zero-drift measurement, reverses the earlier verdict against the enforcer seat (it failed the anchor, not justification), and locks `claude/agents/` over a vendor-neutral layer with the reopen trigger. |
| [zero-trust-audit-aug6.md](research/zero-trust-audit-aug6.md) | A fix-in-place strict-audit METHOD caught in review before commit and rebuilt read-only. Records the conflicts (core `agent.B5`, the broad-rename gate, a skill name used as a path, unconditional `tsc`/`scythe.sh`, a "remember this" clause with no mechanism) and the idea the draft lacked: a finding weighs exactly what the mechanism producing it weighs — exact matches are verdicts, pattern/naming signals stay candidates for judgment. Scope is project-wide or diff-plus-callers; output is findings only plus a one-line coverage statement. |
