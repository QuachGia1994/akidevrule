# akidevrule — Improvement Plan (Jun 24, revised Aug 17)

Status: done — executed 2026-08-17  
Scope: `skills/akirule/SKILL.md`, `CHANGELOG.md`, this plan file

---

## Context

Original plan (Jun 24) tightened Tier keyword signals in SKILL.md to cut router false positives. Re-audited 2026-08-17 against the current SKILL.md (153 lines, post-2.4.0): ~70% of the keyword loosenesses are still live; 2 items went stale via restructure (`METHOD-techbiz-optimizer.md` → `METHOD-deep-think.md`; Tier 3 → Tier 2), 1 secondary issue changed shape into a format conflict. Deep-think pass (goal chain, steelman, pre-mortem) run on the revised list; its three corrections are folded into the checklist below and marked ⚠.

**Why change at all (steelman of not changing):** Tier 1's sensitivity bias says a false positive "costs a few tokens" — but a bare keyword like `scope`, `value`, `conditional` matches nearly every coding message, so the affected rule file is loaded effectively every session, defeating the tier design. The FP cost is a full-file Read per session per file, not a few tokens. Tightening only the truly ubiquitous words, keeping path signals and Context lines as the safety net, preserves the bias for genuinely ambiguous cases.

**Deep-think corrections to the Jun 24 wording (⚠):**
1. Jun 24's Default ON replacement ("references the Aki stack **or the akirule skill**") is wrong: every project CLAUDE.md in this system references akirule — including Tauri-only projects and this rule repo — so the clause would turn the web-stack rule default ON everywhere. Condition must name the web stack specifically.
2. Jun 24's `flow` → `user flow` would cross-route: `user flow` is now a METHOD-ux-psych keyword (SKILL.md line 98). Add only `luồng xử lý`.
3. Jun 24 justified removing `plugin` by a `plugins/**` path pattern that does not exist in the current Paths line. Removal without replacement loses all coverage — replace with `nuxt plugin` keyword and add the missing `plugins/**` path.

---

## Execution checklist — `skills/akirule/SKILL.md` (line numbers per current file)

### 1. RULE-content-write.md block (line 41)
- Remove `copy` — coverage remains via `UI text` (Jun 24 said "UI copy"; that keyword does not exist — `UI text` is the live one)
- Remove `văn bản` — coverage via `thông báo lỗi`, `nhãn`, `nội dung UI`
- Replace `semantic` → `semantic stability`
- Replace `nội dung` → `nội dung UI`, `nội dung giao diện`

### 2. RULE-stack-akiNuxtCf.md block (lines 46–48)
- ⚠ Replace the first sentence of line 46 with: `**Default ON when the project CLAUDE.md references the Aki web stack (Nuxt/Cloudflare — AkiNuxtCf).**` — keep the existing Skip sentence unchanged (it already matches Jun 24's proposal verbatim)
- Remove `pages` — `pages/**` path (line 48) covers it
- Replace `workers` → `cloudflare workers`, `cf workers`
- ⚠ Replace `plugin` → `nuxt plugin`, and add `plugins/**` to the Paths line (line 48)
- Replace `layout` → `nuxt layout` — bare removal would drop the message-level entry point to the stack rule's layout-width SSoT; `layouts/**` path and `layout chrome` keyword stay

### 3. METHOD-flow-audit.md block (line 87)
- ⚠ Remove `flow`, add `luồng xử lý` — do NOT add `user flow` (owned by METHOD-ux-psych)
- Replace `conditional` → `nested conditional`, `điều kiện lồng nhau`
- Replace `timing` → `timing issue`, `race condition`

### 4. METHOD-deep-think.md block (line 108) — retargeted from the deleted METHOD-techbiz-optimizer.md
- Remove `value` and `effort` — both bare words match everywhere; the Context line ("scope or effort/value discussion") plus `tradeoff`, `is this worth`, `có đáng`, `đánh giá` keep coverage
- Replace `scope` → `scope creep`, `mở rộng scope`

### 5. RULE-docs.md block (line 34)
- Replace `feat/` → `docs/feat/` — bare `feat/` is a git branch prefix
- Remove `index.md` — "any `.md` file, anywhere" path rule (line 36) covers it

### 6. Tier 2 protocol step 3 (line 130) — receipt format consolidation
- The original Jun 24 duplication is gone, but a new conflict exists: step 3 says output `[akirule:full] Loaded: <filenames>` while the Load-confirmation section (line 146) says Tier 2 writes `(router:full)` inside the `[RULES]` line — two formats for one event
- Replace step 3 with: `3. Emit the [RULES] receipt per § Load confirmation, with the loaded set marked (router:full)` — delete the `[akirule:full]` format

### 7. Tier 1 intro (after line 25) — skip-if-already-loaded
- Add one line: `Skip the Read if that file was already loaded earlier in this conversation — a signal match on an already-loaded rule costs a redundant Read and changes nothing.`

### Explicitly NOT done (recorded per docs.C2 "No action")
- `nạp full` false-trigger hardening (Jun 24 secondary #3): no observed false trigger; act only if one appears in practice
- Other broad deep-think keywords (`complexity`, `abstraction`, `tooling`, `edge case`): moderately broad but each maps to a real deep-think trigger phrase; no evidence of FP flood — leave until observed

---

## Companion edits (same run)

1. `CHANGELOG.md` — open a new `## [Unreleased]` section on top (state is Pre-bump: 2.4.0 released today) with a `### Changed` entry summarizing: Tier keyword tightening in akirule SKILL.md (list the removed/narrowed keywords), receipt-format consolidation (`[akirule:full]` folded into `[RULES] … (router:full)`), skip-if-already-loaded line. Note the deep-think corrections (Default ON wording, `user flow` cross-route, missing `plugins/**`) so the reasoning survives.
2. This plan file — after all edits verified: set Status to `done — executed 2026-08-17`, move to `docs/plan/done/improve-jun24.md` (`docs.B1`).
3. Propagate: run `bash /home/guest/aki/AkiDevRule/install.sh` so the deployed copy at `~/.aki/akidevrule` and `~/.claude/skills/akirule` match source. No git commit — leave the working tree for the owner.

## Verify (static, per coding.B3)
- `grep -n "văn bản\|akirule:full" skills/akirule/SKILL.md` → 0 hits
- `grep -cn "nội dung UI\|scope creep\|nested conditional\|race condition\|nuxt plugin\|nuxt layout\|cloudflare workers\|docs/feat/\|luồng xử lý" skills/akirule/SKILL.md` → all present
- Bare `scope`, `value`, `effort`, `conditional`, `timing`, `flow`, `pages`, `layout`, `plugin`, `copy`, `semantic`, `index.md`, `feat/` no longer appear as standalone keywords in the touched blocks (substrings inside longer keywords are fine)
- Diff of installed `~/.claude/skills/akirule/SKILL.md` vs source is empty after install
