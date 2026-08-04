# Penalty cards + scythe — severity-restructure proposal researched, renumber rejected, mechanism shipped

## Start time

2026-08-04.

## Initial purpose

The owner proposed three tasks: (1) restructure `RULE-agent-behavior.md` by severity (Lethal/Destructive/Annoying) so the highest-frequency violations could be called by short codes ("vi phạm A1!" = wrap, "A2!" = verbosity); (2) promote a four-axiom comment philosophy into `RULE-coding.md` and point `docs.B3` at the new density root; (3) build a `/akiaudit` skill with a `scythe.sh` grep script (2-consecutive-comment-lines → wrap error; comment >150 chars → verbosity error). Explicitly framed as a proposal to be critiqued with first-principles + adversarial methods before anything changed. Context: one day after `akirule-akiflow-upgrade-aug3.md` shipped the density lens; the owner's wrap/verbosity pains persist — the aug3 escalation condition invoked early, by the owner.

## Strategy

Read the current corpus (behavior/coding/docs rules, akirule/akiflow skills), measure the address-reference blast radius mechanically, then read the repo's own improvement history (CHANGELOG, `public-private-abc-restructure.md`, `akirule-akiflow-upgrade-aug3.md`, `akiflow-compliance-enforcement-aug3.md`) before judging — the history reversed parts of the first-pass assessment. Deep-think critique (goal chain, steelman, inversion, pre-mortem) on each task; owner ratified the reshaped plan in full.

## Checklist

1. Corpus + skill read; goal excavation of the shout-a-code UX pain.
2. Measured cross-references: `grep -rEo '(agent|coding|docs)\.[ABC][0-9]'` → 66 hits across 16 files.
3. History read; prior decisions located (D3 no-rename precedent, aug3 hook rejection, aug3 enforcement-tier root finding, AKIRULEPOLIC lesson).
4. Design reshaped; owner approved; implemented; scythe verified on fixtures and live corpus; `install.sh` run.

## Result

- **Renumbering is the trap in the proposal.** 66 address cross-references over 16 files break silently; immutable research docs (`docs.B2`) would point at wrong meanings forever; `public-private-abc-restructure.md` D3 already rejected the same class of churn ("chi phí phá tham chiếu > lợi ích"); and bare "A1" is ambiguous by the scheme's own design — every file has an A1. Deeper: aug3's root finding says the wrap/verbosity pains are enforcement-tier failures, so reordering prose is a reminder-tier fix for a mechanism-tier problem. The proposed severity axis also encodes frequency-of-annoyance, not objective harm (it ranked wrap above audit-time git mutation), so it would rot as soon as the scythe kills the wrap pain.
- **The proposal's task 2 was mostly already shipped**: `coding.B4` (created aug3) carries axioms 1/2/4; `docs.B3` already points at root `agent.A4`. Only the comment-rot axiom (3) was genuinely missing.
- **The scythe is the proposal's real value** and lands on the trajectory the repo was already on (prose → mechanism: council-verify.sh, no-self-attestation, read-only by mechanism). Bonus found in history: the enforcer's evidence hands were agy flash, with a recorded gemini fabrication caveat — a grep is the fabrication-free evidence source that seat actually wanted.
- **Two detector bugs in the proposed algorithm, fixed by design**: any-2-consecutive-comments floods false positives (docblocks, headers, directives) → continuation heuristic + exemptions; the 150-char verdict contradicts `agent.C3` (a legit long WHY may not be wrapped → no legal form would exist) → ≥3-line blocks / >200 chars, labeled *(review)*, judgment stays with the reader. Added the class the proposal missed entirely: markdown prose wrap, the owner's highest-frequency pain.

**Verification:** blast radius measured mechanically (step 2). Fixture suite: 7/7 expected findings, 0 false positives after three heuristic fixes (lettered sub-lists, `→`-ended layout lines, multi-paragraph leading headers). Live corpus run caught 8 real wrapped lines in `harness-facts.md` (rejoined in this pass) and 1 legit *(review)* flag in `council-open.sh` (left — judgment call, mid-file usage note). Unverified: whether the card vocabulary reduces hand-corrections — same 2-week observation window as aug3's floor-clause assumption.

**Corroborating links:** `public-private-abc-restructure.md` (D3/D4 address-stability precedent) · `akirule-akiflow-upgrade-aug3.md` (enforcement-tier diagnosis; hook + core-floor rejections; escalation falsifier) · `akiflow-compliance-enforcement-aug3.md` (evidence-not-citation doctrine; gemini fabrication caveat; AKIRULEPOLIC lesson).

## Decision — Action

Owner approved the reshaped package in full ("tất cả duyệt"). Applied 2026-08-04:

- `payload/RULE-agent-behavior.md` — new §0 Penalty cards (`[WRAP]`/`[FLUFF]`/`[YAP]`), all existing addresses untouched.
- `payload/RULE-coding.md` — comment-rot bullet + `[YAP]` card backref in B4.
- `payload/index.md` — manifest rows, groups table, density lens row extended with the mechanical-detection pointer.
- `skills/akiflow/scripts/scythe.sh` — new shared detector; `skills/akilint/SKILL.md` — new user-invocable wrapper (named *lint*, not *audit* — `audit` is a defined corpus term).
- `skills/akiflow/SKILL.md` — enforcer's first hands switched to scythe for the wrap/comment classes; YAML description updated.
- `skills/akiflow/references/harness-facts.md` — the 8 wrap findings rejoined.
- `README.md`, `CHANGELOG.md`, `docs/index.md` updated; `install.sh` run to propagate.

**No action (deliberate):** severity renumbering (rejected, above); PostToolUse hook (owner rejected aug3; the narrow reopening condition — a wrap-only mechanical hook is not covered by the aug3 "content understanding" rejection reason — is recorded here and left to the owner's initiative).

## Cross-references

- `docs/research/akirule-akiflow-upgrade-aug3.md` — the escalation path this fulfills; its "revisit placement" falsifier is what this doc answers (answer: escalate the *mechanism*, not the placement).
- `docs/research/akiflow-compliance-enforcement-aug3.md` — the enforcer seat whose hands this upgrades.
