# Plan: Audit-first naming for audit METHOD files

Executed 2026-08-19 in the requesting session; created directly in `done/` as the execution record.

## Decision

- Renames, so every audit method sorts and reads as one `METHOD-audit-*` class: `METHOD-flow-audit.md` → `METHOD-audit-flow.md` · `METHOD-zero-trust-audit.md` → `METHOD-audit-zero-trust.md` · `METHOD-subtraction-audit.md` → `METHOD-audit-subtraction.md`.
- **Topic addresses unchanged** (`flow`, `zero-trust`, `subtract`): they were already shorter than filename-minus-prefix, so every `topic.item` reference across the corpus, agents, and scripts stays valid (`content.A3` semantic stability). The addressing-scheme wording in `payload/index.md` and `skills/akirule/SKILL.md` now names the manifest Topic column as the authority instead of implying a pure filename derivation.
- `METHOD-ux-psych.md` considered and left unrenamed: audit-capable but equally a design method, and not named audit today.

## Live references migrated

`payload/` (`index.md` manifest rows, `RULE-agent-behavior.md` B5, `RULE-docs.md` C, `RULE-pattern-core.md` A8/B2, `RULE-ui-pattern.md` C, `METHOD-audit-subtraction.md` self-refs, `METHOD-ux-psych.md`) · `skills/` (`akirule` signal-block headers, `akihelp` painpoint table, `akiship` boundary line) · `claude/agents/aki-challenger.md` · `README.md` (tier list + layout tree) · `docs/index.md` · `install.py` AG_RULE_MAP. Immutable records (`docs/research/`, `docs/plan/done/`, past CHANGELOG entries) keep the historical names per repo policy.

## Verification

- `grep -rn "METHOD-flow-audit\|METHOD-zero-trust-audit\|METHOD-subtraction-audit"` over `payload/ skills/ claude/ README.md docs/index.md install.py` → zero hits after migration.
- `bash install.sh` → deployed `~/.aki/akidevrule` carries only the new filenames; deployed copies diff clean against source; Antigravity rule map regenerated from the renamed AG_RULE_MAP entries.
- `scythe.py` clean over every touched file.
