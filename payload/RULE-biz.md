# Business & Market Rules

<!-- Address map: biz.A1-4 · biz.B1-4 · biz.C1-4 -->

**Tier: Contextual.** Load on any market-facing decision: positioning, audience, pricing, monetization, product messaging, or evaluating an idea's commercial shape. This file owns the **content** of business decisions; the decision **process** (value/cost/validation questioning) stays in `METHOD-deep-think.md` Module 4 — apply both together, do not duplicate either.

## A. Positioning & audience

### A1. One primary audience per product
Every product names exactly one primary audience and the job it hires the product for, in one sentence. "Everyone who…" is not an audience. Secondary audiences may exist, but every tradeoff resolves in favor of the primary one — a product optimized for two masters serves neither.

### A2. USP must be falsifiable
State the unique selling proposition as a claim that could be proven wrong ("imports a full set in one pass, competitors need per-file steps"), never as an adjective pile ("powerful, easy, modern"). If no falsifiable difference exists yet, say so in `docs/biz/` — an honest "no moat yet" beats a decorative one.

### A3. `docs/biz/` is the single source of truth
Positioning, audience, USP, and monetization live in `docs/biz/` (mandated by `RULE-docs.md` A3). Every market-facing decision cites it; when a proposed change contradicts it, surface the conflict — reconcile or escalate, never silently override (same discipline as code vs `biz/` docs).

### A4. Niche first, expand from a beachhead
Enter through the narrowest audience segment that can be won convincingly, then expand from proof — never launch broad on speculation. A small segment that actively uses and recommends the product outranks a large segment that shrugs.

## B. Offer & pricing

### B1. Price by value delivered, not cost incurred
Anchor price to the outcome the primary audience gets (time saved, revenue enabled, risk removed), not to build effort or infra cost. Cost sets the floor; value sets the number.

### B2. Few tiers, obvious differences
Offer the smallest tier count that covers real usage patterns (often one, rarely more than three). Each tier's difference must be explainable in one line without a comparison table. A tier that exists "to make the middle one look good" is acceptable decoy design; a tier nobody can explain is not.

### B3. Validate before building
Before any monetized capability is built, define the smallest credible market test (waitlist, pre-order, manual concierge version, one landing page) and the observable result that would justify or kill the build — run it through `METHOD-deep-think.md` Module 4's validation questions. Building first and hoping is the failure mode this rule exists to stop.

### B4. Revenue path stated from day one
`docs/biz/` states how the product ever produces value back — even when the honest answer is "none: personal tool / portfolio / ecosystem support". An explicit "none" is a valid, stable answer; an implicit one silently distorts later decisions toward unjustified scope.

## C. Messaging & customer psychology

### C1. Benefit first, proof over adjectives
Lead every market-facing message with what the user gets, then prove it (number, demo, concrete mechanism) — never stack unproven adjectives. Writing mechanics (tone, length, i18n) belong to `RULE-content-write.md`; this rule owns the persuasion structure.

### C2. Handle anxiety at the decision point
Every conversion point (signup, purchase, install, permission grant) names its dominant user anxiety — price? lock-in? data safety? looking stupid? — and answers it right there, not on a distant FAQ page. Unanswered anxiety, not lack of desire, is the default reason a convinced user still bounces.

### C3. No dark patterns (ABSOLUTE)
Never ship confirm-shaming, hidden costs, forced continuity traps, disguised ads, or friction deliberately added to prevent leaving (cancel/unsubscribe/export must be as easy as their opposite). Short-term conversion bought with user resentment is a brand debt that compounds; this floor is not negotiable for any conversion goal.

### C4. One story across all surfaces
The positioning sentence from `docs/biz/` is the same story on the landing page, README, release notes, and in-product copy — reworded per channel, never contradicted. Semantic stability of the terms themselves is owned by `RULE-content-write.md` A3.

## One-line reminder

Know exactly who the product is for and why they would pick it — before polishing anything else.
