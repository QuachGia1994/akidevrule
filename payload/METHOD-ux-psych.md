# Aki Method — UX Psychology Audit

<!-- Address map: ux.A1-6 · ux.B1-5 · ux.C1-4 -->

**Tier: Analytical.** Load when evaluating an interface, flow, or interaction design through the lens of user behavior and psychology — a UX review, a new user-facing flow, an onboarding/conversion design, or "why don't users do X". This METHOD owns *how users think and behave*; visual-system enforcement (tokens, class taxonomy, variants) stays in `RULE-ui-pattern.md`, and persuasion/messaging structure stays in `RULE-biz.md` §C.

## A. Lenses — how a real user actually experiences the interface

### A1. Cognitive load is the primary budget
Every element, choice, and word spends the user's attention. Audit each screen for what can be removed, deferred, or defaulted before anything is added. The question is never "does this feature fit?" but "what does it cost the user to ignore it?"

### A2. Recognition over recall
Users recognize; they do not memorize. Anything the user must remember across steps (a code, a filename, which mode they are in) is a defect — show state, carry values forward, label the current mode visibly.

### A3. Feedback and perceived status
Every action gets an immediate, proportionate response: press → visible change, wait → progress signal, done → confirmation, failed → what happened and what to do next. Perceived speed (instant acknowledgment, skeleton, optimistic UI) matters as much as actual speed — see the Tauri never-block-the-UI rule for the runtime side of the same law.

### A4. Defaults and choice architecture
The default path is the design — most users never leave it. Every choice presented must earn its place (more options = slower decisions and more abandonment); prefer a good default plus an escape hatch over an upfront question. Never exploit defaults against the user's interest (`RULE-biz.md` C3 applies).

### A5. Physical and interaction cost
Frequent targets are big and close; destructive targets are separated and deliberate. Count real motor cost per core task: clicks, cursor travel, keyboard↔mouse switches, precision demands. On hover-revealed UI, remember the hover-bridge rule (`RULE-ui-pattern.md` B5).

### A6. Mental-model match and trust
The interface's concepts and vocabulary must match how the primary audience (from `docs/biz/`) already thinks — not the implementation's internal model. Trust is built by consistency (same term, same behavior everywhere) and honesty (errors admitted plainly); it is destroyed by surprise.

## B. Walkthrough protocol — run in order

### B1. Walk as the persona, not as the builder
Take the primary audience from `docs/biz/` and traverse the real flow start-to-end at their knowledge level — no insider shortcuts, no "they'll figure it out". Note every point where you needed builder knowledge to proceed.

### B2. First-run and empty states
Audit the very first experience separately: what does the user see before any data exists? An empty state must explain what is missing and the one action that fixes it (`RULE-content-write.md` B1). First impressions are formed in seconds and rarely revised.

### B3. Friction ledger
Count, per core task: steps, decisions, waits, context switches, and things to remember. Record the numbers — friction is measured, not felt. Then ask which entries the flow's *shape* could eliminate (defer to `METHOD-audit-flow.md` when the answer is "reshape the flow, not the screen").

### B4. Error, failure, and dead ends
Walk every failure path: wrong input, denied permission, offline, stale data. Each must state the problem in user language and offer a next action. A dead end (error with no exit) is always a severe finding.

### B5. State completeness
Every view is checked in all its states: loading, empty, partial, full, error, success. A view designed only for the happy full-data state is half-designed.

## C. Output & decision

### C1. Findings weighted by severity
Report findings per `METHOD-deep-think.md` B5: trivial → name and move on; material → state with its fix; severe (blocks the core task, breaks trust, dead end) → raise immediately, may override the planned scope. Never pad a report with cosmetic nits at equal rank to task-blocking defects.

### C2. Fixes route through the design system
Every recommended fix lands in the existing token/pattern/variant system (`RULE-ui-pattern.md`) — a UX fix that ships as ad-hoc CSS creates the next audit's findings.

### C3. Respect the floor
No recommendation may trade user trust for a metric: no dark patterns, no anxiety-manufacturing, no attention traps (`RULE-biz.md` C3 is the shared absolute floor).

### C4. Validate with behavior, not opinion
For each material change, name the smallest observable behavioral signal that would confirm it worked (task completion, drop-off point moved, support questions gone) — not "it looks cleaner". If no signal is observable, say so explicitly.

## One-line reminder

Design for the user's attention budget and existing mental model — measure friction, and never buy a metric with their trust.
