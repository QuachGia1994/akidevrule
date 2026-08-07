# CSS/pattern rot: why a loaded rule produced 30k lines of bespoke CSS

**Start time:** 2026-08-04

## Initial purpose

The owner reported that most of their code carries heavy CSS sprawl despite `akirule` being active, estimated over 50% of it removable, and asked which rule covers this or whether the corpus has a gap. Mid-session the goal was sharpened to a target: *"tối giản css về base component dùng sẵn của tailwind, tối giản cực đoan lượng code css đến cực hạn đến không thể nào tối giản hơn được nữa."*

Context at the time — the constraints that make this record judgeable later:

- `RULE-ui-pattern.md` already auto-loads on **any** `.vue`/`.css` touch (`skills/akirule/SKILL.md`: "A file extension alone is a sufficient signal"), and `RULE-design-core.md` is default ON for any structural work. Both were in context while the sprawl was being written. Routing was therefore never a candidate explanation.
- A `PostToolUse` lint hook was rejected by the owner twice (2026-08-03 "density is content understanding"; 2026-08-04 recorded as not-re-proposed, reopenable at the owner's initiative only). Any fix here had to work without one.
- The corpus's own aug3 finding applied directly: *"reordering prose is a reminder-tier fix for an enforcement-tier failure."* Adding more rule text was the thing that had already failed.
- The four measured projects all run **Tailwind v4.3.3**, which is CSS-first (`@theme`), not `tailwind.config`-first.

## Strategy

1. Measure four real projects rather than reason from the rule text, since the rule text was known to be loaded and known to be violated.
2. Locate the defect as a *structural* property of the rule — something that makes the correct behavior unreachable — rather than as missing content.
3. Fix in place at existing addresses only. Renumbering was rejected in `public-private-abc-restructure.md` and again in `penalty-cards-scythe-aug4.md` (66 cross-references across 16 files); that precedent binds here.
4. Subtract before shipping: every proposed change had to survive "does this need to exist at all", since `RULE-ui-pattern.md` is re-read on every UI session and its length is a recurring cost.

## Checklist

- [x] Measured 4 Nuxt projects with a cheap read-only worker (delegated per `agent.A5`): tachnhac.com, akitao.com, kinhdich.akinet.me, tuvi.akinet.me
- [x] Re-verified three findings that would have changed the conclusion if wrong (pattern-layer existence, token mechanism, framework identity)
- [x] Measured the shared-vs-scattered CSS ratio, which is what actually exposed the defect
- [x] Traced each finding to a specific rule sentence
- [x] Applied fixes at `ui.A1`, `ui.A2`, `ui.B4`, `ui.C1`, `design.B3`, plus the Map section of `RULE-ui-pattern.md`
- [x] Synced `payload/index.md` (manifest row + new Cross-cutting lens row), `skills/akirule/SKILL.md` (minimization keywords), `README.md`, `CHANGELOG.md`

## Result

### The headline: the mandatory order is inverted, and nothing in the rule could see it

`ui.A1` states *"Hand-written CSS is the last resort, never the first reflex."* Measured, it is the **dominant** layer in all four projects.

| Project | Shared stylesheet (`assets/css`) | CSS inside SFC `<style>` blocks | Inversion | Selectors defined ≥2× |
|---|---|---|---|---|
| tachnhac.com | 1,180 lines | **6,749** | 5.7× | 13 / 1,246 |
| akitao.com | 477 | **8,466** | **17.7×** | **117 / 274 (43%)** |
| kinhdich.akinet.me | 1,780 | **10,264** | 5.8× | 66 / 1,261 |
| tuvi.akinet.me | 1,665 | **4,547** | 2.7× | 21 / 625 |

**30,026 lines of hand-written CSS** sit in component `<style>` blocks across four Tailwind v4 projects that already have `@theme` tokens and a shared pattern layer.

The reason this survived a loaded rule: inversion is an **aggregate** property. Every check the rule offered was per-file, and no individual file looks unreasonable. A rule whose violation is invisible at the granularity it is enforced at cannot be enforced.

### Supporting measurements

| Metric | tachnhac | akitao | kinhdich | tuvi |
|---|---|---|---|---|
| `.vue` files | 85 | 96 | 88 | 72 |
| Distinct class strings repeating ≥3× | 46 | 215 | 70 | 95 |
| Total occurrences in those | 254 | 2,447 | 300 | 445 |
| Arbitrary-value class usages | 19 | 140 | 89 | 195 |
| Hardcoded hex/rgb outside token files | 163 | 2,507 | 444 | 494 |
| Static inline `style=` | 80 | 870 | 65 | 38 |
| Distinct raw `font-size` values | 74 | 27 | 63 | 96 |
| `@theme` files | 1 | 2 | 4 | 1 |
| `components/base/` count | 0 | 0 | 0 | 0 |
| Total components | 38 | 15 | 30 | 29 |

Worst repeated strings: akitao `uk-card` 192× · `text-white` 149× · `uk-card-badge` 144× · `text-white hover:underline` 128× · `text-sm leading-relaxed` 116×. tuvi `mb-4` 46×. kinhdich `detail-label` 36×.

### Verification — including three corrections to this session's own first pass

The first measurement round reported "0 tier-2 infrastructure, 0 design tokens" and that conclusion was **wrong**. It is recorded here because the error is instructive: it came from measuring a mechanism instead of a capability.

| First claim | Corrected finding | How verified |
|---|---|---|
| No pattern-class layer exists (`@apply` files = 0) | Pattern classes exist and are substantial — `.section-container`, `.section-kicker`, `.detail-label` live in `app/assets/css/main.css` and `admin-shared.css`, written as **plain CSS**. Under Tailwind v4 that is normal and valid; `@apply` is not required for Tier 2. | `grep -rnE '\.(section-container\|detail-label\|section-kicker\|admin-muted)\b' --include='*.css'` resolved to real definitions in all three projects |
| No design tokens exist | All four projects run Tailwind **4.3.3** and all four contain `@theme` blocks (1/2/4/1 files). Tokens exist. | `grep -oE '"tailwindcss"[^,]*' package.json` + `grep -rl '@theme' --include='*.css'` |
| akitao.com uses UIkit alongside Tailwind | **Unverified — do not act on this.** UIkit is absent from `package.json` and imported in no CSS/JS asset; the only trace is a `/uikit/**` route rule in `nuxt.config.ts`. The 336 `uk-*` class occurrences are therefore either inert classes or markup served from a legacy static path. Needs a project-level check, not a corpus change. | `grep -rn -i 'uikit' nuxt.config.* package.json app.vue` + asset scan |

The consequence of the correction is that the diagnosis got **sharper**, not weaker: these projects are not missing a design system. They have tokens, a shared stylesheet, and 15–38 components each. The failure is that the system is bypassed and re-invented, which the next finding captures.

### One name, several definitions — worse than plain duplication

`.detail-label` is defined **two to three times inside a single project** (`admin-shared.css`, plus scoped `<style>` blocks in `AdminDrawer.vue` and `TopUpModal.vue`), and byte-identically **across** projects (`tachnhac/AdminDrawer.vue:441` and `tuvi/AdminDrawer.vue:446` carry the same declaration). akitao.com redefines **43% of all its selectors** (117 of 274).

This is strictly worse than raw duplication: a shared semantic name promises a single definition it does not deliver, and which definition wins depends on load order — invisible at every call site. `ui.B4` mandated *recording* a new pattern but never mandated *looking one up*, so a write-only duty produced exactly this.

Corroborating detail: `tachnhac.com/app/assets/css/admin-shared.css:64` already contains a hand-written comment documenting this very pattern for `.admin-muted`. A prior session diagnosed it correctly and the rule offered nowhere to put the fix.

### Root defect: the tier ladder has no rung that removes anything

Every tier in `ui.A1` — utility, pattern class, variant, component — is a way to **package** repetition. None removes it. The first rung is already "write the utility", so the cheapest outcome (the style does not need to exist) is unreachable by construction. `text-sm leading-relaxed` × 116 is inheritable typography that belongs once on a container; the ladder had no step where that thought could occur.

`RULE-ui-pattern.md`'s own Map section listed design-core Laws 1, 2, 4, 5, 7 — and omitted **Law 8** (reshape rather than stack). The file never inherited the corpus's own subtraction discipline, which already existed in `think.B4`, `design.B3`, and akiflow's standing Red Team subtraction pass.

### Second defect: Rule of Three names a threshold nothing can observe

- `design.A2` — extract at ≥3 occurrences across ≥2 call sites.
- `design.A5` — *"The second paste is a mandatory STOP: plan the shared shape before a third exists."*
- `ui.A1` (before this change) — *"Climb to tier 2 only when Rule of Three fires — never pre-extract a pattern class."*

`ui.A1` kept A2's threshold and dropped A5's trigger. The ≥3 count is repo-wide; a session editing one file cannot see the other ninety. So the prohibiting half ("never pre-extract") was trivially enforceable while the enabling half was unobservable — a structural bias toward never abstracting. `components/base/` = 0 in all four projects, against 2,447 duplicate occurrences in akitao alone, is that bias measured.

### Third defect: a rule naming a file the stack no longer uses

`ui.A2` mandated *"a token in `tailwind.config` + a CSS variable"*. Every measured project runs Tailwind v4 CSS-first `@theme`. A rule that names the wrong mechanism teaches the reader the rule is decorative — and this one did so on the single highest-traffic rule file in the corpus.

### Fourth defect: an unnamed fifth tier

`ui.A1` asserted *"Every style belongs to exactly one tier — there is no fifth tier"* while listing tiers 0–4, none of which is inline `style=`. Static inline styles were therefore unclassified — neither permitted nor forbidden — and 870 accumulated in akitao.com. They are invisible to every scan in `ui.C1`, cannot carry a token, and cannot be overridden without `!important`.

### Correction to the optimization target itself

"Reduce CSS code volume" is ambiguous, and one reading of it is false: **writing a Tailwind utility fewer times does not reduce shipped CSS bytes.** JIT emits each used utility exactly once regardless of call-site count. The real costs of a bloated class surface are source volume, agent context, and edit amplification (change one color → touch 128 sites). The optimization target is therefore the **markup class surface and the bespoke `<style>` layer**, not the generated stylesheet — recorded here so a later reader does not chase the wrong metric.

## Decision

**Action — applied to the corpus this session.** No address was renumbered; every fix landed at an existing one.

| Address | Change |
|---|---|
| `ui` Map section | Added the missing **Law 8** mapping — the ladder packages, Law 8 eliminates |
| `ui.A1` | **Subtraction pass** (delete → inherit → hoist) placed *before* any tier; mandatory order becomes `subtraction → Utility → Pattern class → Component variant → hand-written CSS` |
| `ui.A1` | Rule of Three restated: **the second copy is the STOP, the third is only the extraction threshold** — preserving `design.A2` (do not extract at 2) while restoring `design.A5` (decide at 2). "Leave both inline" stays legitimate, but as a decision rather than a default |
| `ui.A1` | Inline `style=` classified: a **runtime-computed escape hatch only**; static inline styles are always violations |
| `ui.A1` | `<style>`-block budget: "last resort" made a **quantity claim measured in aggregate** against the shared layer, since per-file inspection cannot see inversion. Legitimate residents enumerated (keyframes, `:has()`/`::-webkit-scrollbar`/print, third-party overrides, unauthored CMS markup) so the rule is strict without being unfollowable |
| `ui.A2` | Token mechanism made version-aware (`@theme` v4 / `tailwind.config` v3 / plain custom properties), with an instruction to read the project's actual setup; added **one theme source per project** as token-layer SSoT |
| `ui.B4` | Duty made **two-way, lookup first** — grep the shared stylesheet and token source before defining any named style; records why a write-only duty is worse than plain duplication |
| `ui.C1` | **Inversion check promoted to the first scan**, plus a redefined-selector scan; two blind spots now stated in the report contract (`:class` bindings are invisible so counts are floors; absence of `@apply` never implies absence of Tier 2 — the exact error this session made) |
| `design.B3` | New first bullet of the critique gate: **subtract before you share** — the other three bullets all assume the code must exist |
| `index.md` | New Cross-cutting lens row (**Subtraction before abstraction**: root `think.B4` → `design.B3`, `ui.A1`, akiflow Red Team) + rewritten `ui` manifest row |
| `akirule/SKILL.md` | Minimization keyword set added to the `RULE-ui-pattern.md` audit signals (`tối giản`, `giảm CSS`, `CSS rác`, `style block`, `inline style`, `@theme`, …) |

**No action — deliberately not done, with reasons:**

- **No audit playbook added to `RULE-design-core.md`** for non-UI duplication, despite the symmetric gap being real (`ui.C` has scans, severity, matrix, report template; `design.C1` has only a self-check list). `design-core` is default ON for *all* code work including backend, Tauri, and CLI; a UI-shaped audit section would tax every non-UI session for a benefit `ui.C` already delivers where the evidence actually is. Reopen when non-UI duplication has produced measured harm, not before.
- **No `PostToolUse` hook.** Twice owner-rejected, and independently the wrong instrument here: a hook sees one file, while the defect this session found is only visible in aggregate. It would fire on all four projects at every edit (2,507 pre-existing violations in akitao alone) and be disabled within a week.
- **No new penalty card in `RULE-agent-behavior.md` §0.** The card vocabulary belongs to the always-loaded core floor; a UI-domain card would cost every Tauri, CLI, and backend session for a concern `RULE-ui-pattern.md` already loads on file extension alone.
- **No new detector script.** `ui.C1` now carries the exact commands, and `scythe.sh` precedent does not extend here: its cards are format classes with a single correct answer, whereas every finding above needs a judgment call about whether the style should exist.

**Assumptions to monitor:**

- That the second-copy STOP does not swing the corpus into premature abstraction. `design.A2`'s ≥3 extraction threshold is deliberately unchanged and "leave both inline" is explicitly legitimate — but a project minting a pattern class per pair would be this change failing, and is the first thing to look for.
- That the aggregate `<style>` budget is not gamed by moving bespoke CSS into the shared stylesheet without reducing it. The ratio would improve while nothing got better; the redefined-selector and duplicate-string scans are the counter-checks.
- That `ui.A1` remains readable. It now carries the subtraction pass, the tier table, inter-tier rules, the inline-style rule, and the `<style>` budget. If it grows again, split before it becomes a wall — but not preemptively (`design.A2`).

**Cross-references:** `penalty-cards-scythe-aug4.md` (the not-re-proposed hook, and the renumbering precedent this change obeys) · `akirule-akiflow-upgrade-aug3.md` (enforcement-tier vs reminder-tier diagnosis, and the earlier lint-hook rejection) · `public-private-abc-restructure.md` (address-stability precedent).

**Follow-up needed at project level, not corpus level:** akitao.com's 336 `uk-*` occurrences and 43% selector-redefinition rate. Neither is a rule problem; both need a project-scoped `ui.C` audit run.
