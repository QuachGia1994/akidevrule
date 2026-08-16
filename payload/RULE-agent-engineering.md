# Agent Engineering & Skill Workflow Rules

<!-- Address map: agent-eng.A1-5 · agent-eng.B1-6 · agent-eng.C1-4 -->

**Tier: Contextual.** Load when the task concerns agent behavior, Agent Skills, subagents, workflow orchestration, skill authoring, TDD, systematic debugging, agent handoffs, or agentic security testing.

## A. Skill selection & workflow order

### A1. Check skills before action
Before exploring, editing, or asking a clarifying question, identify whether an installed skill applies. If a relevant process skill exists, use it before an implementation skill. Do not invoke skills merely because their names exist; the task must match their trigger.

### A2. Process before implementation
For new behavior, creative implementation, or ambiguous design work, resolve intent, constraints, acceptance criteria, and the smallest viable design before implementation. The design may be brief for a reversible change. Do not turn this into mandatory ceremony where the project already has a stronger workflow or the task is a mechanical, non-behavioral change.

### A3. Specialize context, not agents by title
Give an agent only the domain, files, constraints, and success criteria it needs. Prefer a small number of specialized skills over a large generic prompt. A skill should add domain technique, examples, validation methods, or context-specific edge cases rather than restating universal rules.

### A4. Progressive disclosure
Keep frequently loaded skill instructions small. Put detailed procedures, examples, scripts, and references behind the skill's `SKILL.md` using `references/` or `scripts/`; do not force-load unrelated material. A skill description is a trigger, not a duplicate of its process.

### A5. Minimum sufficient implementation ladder
After understanding the real flow, choose the first rung that satisfies the requirement: (1) do not build it if YAGNI permits; (2) reuse an existing project capability; (3) use the standard library; (4) use the native platform capability; (5) use an already-installed dependency; (6) implement the minimum missing behavior. Do not reduce validation, security, error handling, accessibility, or data-loss protection merely to make the diff smaller.

## B. Engineering feedback loops

### B1. Align vocabulary before building
When requirements or domain language are fuzzy, establish a shared vocabulary and challenge overloaded terms before changing the model. Store durable terminology in the project's existing glossary or SSoT; store only consequential, hard-to-reverse decisions as ADR/research records.

### B2. TDD for behavior changes
For features, bug fixes, refactors that change behavior, and other testable changes, prefer red → green → refactor: write the smallest behavior-level failing test, watch it fail for the intended reason, implement the minimum change, then refactor. Tests must protect observable behavior, not merely source text or implementation details. Exceptions require a project-specific reason, such as generated or throwaway code.

### B3. Root cause before fixes
For bugs, test failures, regressions, and unexpected behavior, investigate before proposing a fix: read the error, reproduce or characterize the failure, inspect recent changes, trace data/control flow, compare against a working example, then form and test one hypothesis at a time. Fix the root cause, not the symptom. After three failed fix attempts, stop and reassess the architecture instead of stacking a fourth patch.

### B4. One variable per diagnostic experiment
A debugging change should be the smallest experiment that distinguishes the current hypothesis from alternatives. Do not bundle unrelated fixes, refactors, or cleanup into a diagnostic step. If the hypothesis fails, return to investigation with the new evidence.

### B5. Independent review axes
Before merge or release of substantial work, review from at least two independent questions when the project permits it: **spec** — does the change implement the requested behavior? **standards** — does it fit the repository's architecture, coding rules, security, and maintainability baseline? Do not give the reviewer the lead's reasoning when that reasoning could bias the verdict; provide the fixed point, diff, requirements, and review criteria instead.

### B6. Verification before completion
Completion requires evidence from the narrowest verification tier that settles the risk: static inspection, focused test, broader regression, or runtime/external verification as appropriate. A passing test that never exercised the intended behavior is not evidence. For external integrations, verify the external state rather than only the local configuration or command that would change it.

## C. Agent orchestration & security

### C1. Context isolation
Subagents receive only the context required for their task. Handoffs must state the target, scope, relevant rules, artifacts, acceptance criteria, and required output. Do not pass the entire lead conversation when a smaller artifact or diff is sufficient. A reviewer should receive the work product and criteria, not the reasoning that produced it.

### C2. Parallelize independent mechanical work
Independent retrieval, inventory, scanning, and other judgment-free work may run in parallel when the harness supports it. Keep judgment, prioritization, architecture decisions, and final classification with the stronger coordinating context. Never parallelize two writers over the same mutable surface without an explicit isolation mechanism.

### C3. Security findings require validation
Security-oriented skills should distinguish discovery from confirmation. A candidate finding is not a vulnerability verdict until its reachability, trust boundary, impact, and reproduction path are established. Prefer reproducible evidence or a safe proof-of-concept over source-pattern presence alone, and explicitly account for false positives, configuration/version dependence, and edge cases. Do not weaken security, error handling, data-loss protection, or accessibility merely to reduce code.

### C4. Skill quality is testable
When creating or materially changing a skill, test the skill itself under representative pressure: establish the failure mode it is meant to prevent, exercise the skill against that scenario, verify the intended behavior, then close obvious rationalization or bypass paths. Validate frontmatter, referenced files, and progressive-disclosure boundaries mechanically where tooling exists. A skill that merely describes good behavior without resisting the target failure is incomplete.

## Sources

This rule distills recurring engineering mechanisms from:
- https://github.com/mattpocock/skills — grilling/shared vocabulary, TDD, systematic diagnosis, deep-module design, independent spec/standards review, composable skills.
- https://github.com/obra/superpowers — process-before-implementation, brainstorming gates, TDD, systematic debugging, context-isolated review, verification-before-completion, and skill testing.
- https://github.com/DietrichGebert/ponytail — understand the flow first, then apply the smallest sufficient rung: delete/YAGNI → reuse → stdlib → native platform → installed dependency → minimal implementation, while never cutting validation, security, error handling, or accessibility.
- https://github.com/usestrix/strix — specialized skill injection, domain-specific security techniques, practical examples, validation against false positives, context/version edge cases, and evidence-backed vulnerability confirmation.
