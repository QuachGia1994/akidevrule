# Docs index — akidevrule

Master index for this repo's documentation. akidevrule is the source of truth for Aki's reusable Claude Code / Antigravity rule and skill baseline; these docs record its architecture, active plans, and decision history.

Topic folders follow `RULE-docs.A2`. Only the folders that currently hold content are listed.

## `arch/` — architecture & technical design

| Doc | Purpose |
|-----|---------|
| [rule-delivery-architecture.md](arch/rule-delivery-architecture.md) | How one rule source is installed onto a machine and consumed by the two agent families (Claude Code vs Gemini/Antigravity). |
| [akiflow.md](arch/akiflow.md) | Why `/akiflow` is shaped as a lead-coordinated agent council: the purpose every rule serves (decide without the owner), the three single-thread failures it targets, the work item as atomic unit, the harness and cost facts the design rests on, the three-file session workspace and its self-pruning, steering as judgment rather than a round counter, the verification-vs-review boundary, and the nine structural failure modes. |

## `ref/` — stable references & lookup docs

| Doc | Purpose |
|-----|---------|
| [agent-skills-standard.md](ref/agent-skills-standard.md) | Verified: `SKILL.md` is a shared open standard between Claude Code and Antigravity/AGY, zero per-agent transformation — the reason `skills/` moved out of `claude/` to a top-level, agent-neutral folder. |

## `plan/` — active plans

| Doc | Status | Purpose |
|-----|--------|---------|
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
| [akirule-akiflow-upgrade-aug3.md](research/akirule-akiflow-upgrade-aug3.md) | `/akithink` decision record for the density/MVP-counterweight/roster upgrade: three worst owner pains diagnosed as enforcement-tier failures, not missing rules; deletion-test density lens, Red Team subtraction pass, verifier drift sweep, context modes, proxy-gateway lane, writer role. Records what was rejected (core-floor placement, lint hook, standing drift/simplifier agents) and the assumptions to monitor. |
