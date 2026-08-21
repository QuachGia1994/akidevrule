# Plan — literal `/akiship` activation gate

**Status:** executed 2026-08-22.
**Evidence:** [research/akiship-literal-activation-aug22.md](../../research/akiship-literal-activation-aug22.md) — the incident, the residency asymmetry behind it, and the two findings deliberately left out of this change.

## Goal

Make it impossible for the akiship run to start on anything but an explicit, imperative `/akiship`, by placing the guard at the same residency as the trigger. One structural fix, not one patch per symptom — the owner's instruction was explicit: *"đừng chắp vá quá nhiều"*.

## Owner constraints taken as given

- `MỌI THỨ KÍCH HOẠT /akiship LÀ BẮT BUỘC PHẢI CÓ CHÍNH XÁC "/akiship"` — the literal token is a necessary condition, no synonym qualifies.
- The token alone is not sufficient: *"nếu để /akiship thì cần gì để trọn vẹn?"* is a request to **use the checklist as reference and answer**, while *"thực hiện /akiship trọn vẹn"* is a request to **run**.
- `RULE-release.md` stays. It predates the skill and is looser, but deleting it or merging it into the skill would lose the release trigger signals and the narrow release context the skill does not carry.

## Edits

| File | Change |
|---|---|
| `skills/akiship/SKILL.md` | New `## Activation gate` section ahead of Phase 1: condition 1 = the turn contains the exact string `/akiship`, condition 2 = the turn is imperative, not interrogative (`agent.A3`), with a two-row table of real phrasings and consult as the tie-break default. Explicitly demotes the bare word "akiship", "release trọn gói", "chạy full release", "ship đợt này" and every standalone completion-intensity word to vocabulary, and states that seeing this file or `release.B8` in context is not an invocation. |
| `skills/akiship/SKILL.md` `description:` | Rewritten to open with the gate. This is the fix, not decoration: the description is the one line resident in every session, so the guard now travels with the trigger it guards. |
| `skills/akiship/SKILL.md` Phase 1 §3, Boundaries | Intensity phrasing re-scoped to "inside a valid execute-mode invocation"; a boundary added forbidding any phase from running on a turn that failed the gate, and forbidding a consult answer from being treated as a later go-ahead. |
| `payload/RULE-release.md` B8 | Heading and intro rewritten: activation is owned by the skill and is literal, this section is **not a trigger**, being routed into context grants nothing, the skill's gate is SSoT for whether the run may start (`pattern.A1`) — the sole documented exception to the skill's "the rule file wins". First bullet now reads "a valid `/akiship` invocation = standing authorization"; the intensity bullet now says it modifies a run already authorized to start and never creates that authorization. |
| `skills/akirule/SKILL.md` | Release keyword group relabelled — those keywords load the rule file and never start a run. |
| `payload/index.md`, `README.md` | B8 summary and the akiship skill row synced to the new activation semantics. |
| `docs/arch/rule-delivery-architecture.md` | Added the general form of the root cause as a delivery fact: a skill's `description:` is resident in every session while its body is not, so a trigger word in the description must carry its own guard. Stamp refreshed. |
| `CHANGELOG.md` | `[Unreleased] → Fixed` entry recording the incident, the mechanism, the fix, and the follow-up batch below. |
| `.gitignore`, `REPORT.html` | Separate leftover found while sweeping the round: `/akihtmlreport` had written a lowercase `report.html` against its own "uppercase, no variant names" rule, and `.gitignore` had been widened to hide it rather than fix it. File renamed, extra ignore line reverted. |

## Verification

| Check | Result |
|---|---|
| Guard present in the resident line | `description:` opens with `ACTIVATION IS LITERAL` — verified by reading the frontmatter |
| Frontmatter still parses (one key per physical line) | verified — `name:` and `description:` on separate lines, the AG silent-skip trap from `arch/rule-delivery-architecture.md` § Verified behavior |
| Deployed copies carry the gate | `~/.claude/skills/akiship/SKILL.md` and `~/.gemini/config/skills/akiship/SKILL.md` both contain `## Activation gate` after `install.sh` |
| Format lint | `scythe.py` exit 0 over all files touched |
| Cross-file consistency | `payload/index.md` manifest ↔ `RULE-release.md` B8 ↔ `akirule/SKILL.md` routing ↔ `README.md` skill row all state the same activation semantics |
| Session actually obeys the gate | **not verified** — a behavior claim about a model, with no detector in this repo that could settle it (`coding.B3`). Reopen trigger recorded in the research doc. |

## Follow-up batch — the two findings first deferred, then closed the same day

Both were held back as a different defect class from activation, then folded in when the owner instructed that nothing in the round stay outstanding. One bullet each; neither touches activation.

| Finding | Fix |
|---|---|
| **Self-answering the owner's intent.** The session decided for the owner what "trọn vẹn không tồn đọng plan" meant. `B8`'s self-answer clause governs repo-determined facts; nothing separated those from owner intent, and akiflow's anchor primitive is the right shape but is skill-local. | `payload/RULE-release.md` B8 — new final bullet: the licence covers what the repo determines and never what the owner meant; a criterion in his own words is his to define, deciding it for him overwrites the anchor, and his own ambiguous wording is the one question worth the interrupt. |
| **No precedence rung for standing user instruction.** `index.md` § Precedence ran source → current conversation → project `CLAUDE.md` → shared rules → older docs, with no place for `~/.claude/CLAUDE.md` / `CLAUDE.local.md` — so a shared-corpus rule at rung 4 read as outranking the ABSOLUTE machine-local never-push ban, which is what happened. | `payload/index.md` § Precedence — new rung 3 for the user's standing instructions: an item marked ABSOLUTE there is never weakened by anything below it, including a shared rule granting an autonomy other projects rely on; ordinary guidance there still yields to a more specific project rule. |
