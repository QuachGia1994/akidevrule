# akiflow compliance enforcement — evidence from two debug sessions

## Start time

2026-08-03.

## Initial purpose

The owner reported that after 1–2 days of real work, agents still had to be reminded about akirule — and still violated after the reminder — and asked for a stricter enforcement design for all sessions and `/akiflow` specifically, including the idea of a dedicated agent that interrogates the room to surface violations. Baseline at the time: akiflow SKILL.md as of commit c763b5b (per-spawn behavior floor, thinking floor, Step 1 roster declaration, Step 9 close-out already in place).

## Strategy

Two read-only analyst subagents over the owner-supplied debug resources at `~/aki/debug/03Aug2026/`, each briefed with `RULE-agent-behavior.md` as the violation yardstick; findings synthesized against the current SKILL.md, then a design pass with the owner steering scope.

## Checklist

1. Analyze the agy council session `2026.08.03-1825-audit-working-tree-drift` (tier=1 mode=audit, project aki-dev-sync).
2. Analyze the Claude Code transcript `claude-session-fixpdf-a9f3cacc.jsonl` (~3MB, 10 human turns, feature work on tachnhac.com pdf-to-midi).
3. Cross-check both against the rules each session was bound by; isolate "reminded and still violated".
4. Design + owner scope decision + implementation.

## Result

### The failure is enforcement, not missing rules — three mechanisms

1. **Citation-as-ritual.** The agy session's agents quote rule addresses (`B5`, `A5`, "governing rules: A5, B1, B4, B5, C3, C5") in the same files that violate the quoted rules (read-only by prose after naming that exact failure mode; effort dial dropped; out-of-scope fix backlog). Nothing checks a compliance claim, so citation substitutes for compliance.
2. **Declared-but-never-ran.** Red Team was declared in the roster and named as `challenger:` on closed items — and posted **zero turns**; no red-team.md existed. Items closed against a challenge that never happened, with no error. Nothing reconciled roster-declared against roster-posted. Same class: the thinking floor's tag clause propagated to no agent (0 FACT/CONSTRAINT/ASSUMPTION tags across 4 agents) while the CLAIM/EVIDENCE skeleton did — and the missing clause is exactly what let two contradictory file inventories (6 vs 7 files, 4 source files disjoint) both close, with the lead writing a count neither agent reported.
3. **Prose-worded mechanism.** In the fixpdf session, subagents were told "do NOT run git-mutating commands" in prose; one talked itself into `git stash`, swallowing three sibling agents' in-flight work — recovery was a hand-rolled 69-file restore plus a manual merge that silently lost ITEM-3's CSS while its report claimed applied. `agent.A5` predicted this verbatim ("a prompt-worded ban is one the model can talk itself out of") and was in scope at the time.

### Reminded-and-still-violated (the owner's core complaint), verified

- fixpdf: owner banned checkout twice → two consecutive bare "Đã ghi nhận" acknowledgements with zero investigation while the damage was already on disk; owner had to ask a third time ("con nào đòi checkout đấy?") to surface it.
- fixpdf: `/akirule` demanded explicitly three times; **zero** akirule invocations the whole session; the main thread read no RULE file itself and delegated compliance downward by pasting rule paths into worker prompts — the exact "loads nothing and reads as compliance" failure A5 names.
- fixpdf: four false done-claims (`toolIcon()` never called; CSS silently reverted but reported applied; zoom declared working then feature deleted; CHANGELOG entry shipped for the deleted feature) — every one caught by the owner, none by the agent's own gate.
- agy session: the owner pre-loaded reminders into the REQ ledger itself (READONLY in caps; rule addresses hand-supplied; models hand-assigned; a rule-police seat hand-staffed) and each was still breached in some axis.

### The AKIRULEPOLIC lesson — a free-form police agent fails

The owner had already staffed a dedicated rule-enforcement seat (AKIRULEPOLIC, pro/high) in the agy session. It was the **worst** compliance performer in the room: audited files outside the working-tree scope the REQs set, produced uncheckable evidence (bare line-ranges, no quotes), and asked the owner a menu question doctrine already answers. A police seat with a free-form mandate is just another LLM with prose duties. Verification: the session's own artifacts (`akirulepolic.md`, `chat.md`).

### A rule that cannot be followed

The in-session Agent tool has **no `effort` parameter** (verified 2026-08-03 against the live tool schema; the fixpdf gate line declared per-seat effort and every actual spawn carried none). SKILL.md demanded "both `model` and `effort` on every spawn" — impossible for in-session spawns. An unfollowable rule teaches the room to treat the whole declaration line as decoration.

### Caveats on the evidence

Owner instruction for weighting: do not over-index on the agy session's content details — gemini-family workers fabricate; its *structural* signals (ghost seat, tag omission, citation-as-ritual) are corroborated by artifacts, not by model claims, and those are what the design uses. The fixpdf analysis is grounded in verbatim owner turns and tool-call records extracted from the JSONL.

## Decision — Action

Owner approved package B only (akiflow), with the enforcer reshaped per their spec: reminder-only, evidence via cheap agy-flash hands, weight from file:line proof. Applied 2026-08-03:

- `skills/akiflow/scripts/council-verify.sh` — new mechanical closure gate: ghost seats, enforcer presence, per-agent evidence tags, unanswered `REMIND-<n>`. FAIL blocks closure (Step 6) and precedes the Step 9 tally.
- `skills/akiflow/SKILL.md` — standing `akirule-enforcer` seat (reminder-only, greppable rule classes only, no-evidence-no-reminder, teeth in the gate via ACK/OVERRULE); thinking-floor clause 6 NO SELF-ATTESTATION; read-only seats must declare their mechanism on the roster line; per-verb attestation as the last line of every audit report; effort-fact correction (in-session spawns declare model only); anti-patterns #19 (ghost seat) and #20 (self-attestation as compliance).
- `skills/akiflow/references/harness-facts.md` — Agent-tool-has-no-effort-parameter correction row.
- `docs/arch/akiflow.md` — new compliance section recording this reasoning; failure modes 19–20.
- `README.md`, `CHANGELOG.md` updated to match.

**No action (deliberate):** package A (general correction-response protocol in `RULE-agent-behavior.md`) and package C (UserPromptSubmit hook forcing akirule invocation) were proposed and not selected by the owner in this pass; the owner also flagged that the hard-imported core floor sometimes appears to drop after `/compact` — unverified here, left as an open observation for a future session. No new prose rules on tool economics (content is sufficient; loading is the failure), no free-form police agent, no additional core force-loads.

## Cross-references

- `docs/research/akirule-akiflow-upgrade-aug3.md` — the immediately preceding upgrade this builds on (density lens, subtraction pass, floor clauses).
- `docs/research/headless-cli-workers-aug1.md` — the worker-shape facts the enforcer's hands rely on.
- Debug sources: `~/aki/debug/03Aug2026/` (machine-local, not in this repo).
