# Plan: Pre-allow Skill Scripts Across Multi-CLI Environments (v2.4.2)

## 1. Problem Statement

Executing deterministic skill scripts (e.g. `scythe.py` format lint, `council_verify.py` gate validation) currently triggers interactive permission prompts on Antigravity CLI (`agy`), Antigravity IDE, and Claude Code because:
1. `install.py` previously only granted file read permissions (`Read(//~/.aki/akidevrule/**)`) in `~/.claude/settings.json`.
2. No execution permissions (`Bash(...)` or `command(...)`) were merged for managed skill paths in Claude Code or Antigravity configuration files (`~/.gemini/antigravity-cli/settings.json`, `~/.gemini/settings.json`).
3. Kiro CLI permissions (`~/.kiro/settings/permissions.yaml`) were unmanaged.

## 2. Target Scope

- **Installer (`install.py`)**:
  - `merge_settings()`: Merge `Bash(python3 ~/.claude/skills/*)` and `Bash(python3 ~/.aki/akidevrule/agskills/*)` into `~/.claude/settings.json` (single `*` — Bash rules have no `**`, unlike Read/Edit; see `docs/ref/cli-permission-allowlist-standard.md` § 1.1).
  - `merge_antigravity_permissions()`: Idempotently merge `command(python3 ~/.claude/skills/*)`, `command(python3 ~/.gemini/config/skills/*)`, `command(python3 ~/.aki/akidevrule/agskills/*)` into `~/.gemini/antigravity-cli/settings.json` and `~/.gemini/settings.json`.
  - `merge_kiro_permissions()`: Idempotently configure `~/.kiro/settings/permissions.yaml` if `~/.kiro` directory exists.
  - Update pre-install status check and post-install summary to reflect permission status across all supported environments.
- **Documentation**:
  - Reference doc `docs/ref/cli-permission-allowlist-standard.md` registered in `docs/index.md`.
  - `CHANGELOG.md` entry for v2.4.2.
- **Verification**:
  - Run `python3 install.py` and verify all target JSON/YAML files for correctness and idempotency.
  - Bash rule glob semantics cross-checked against Claude Code's own permissions docs (`code.claude.com/docs/en/permissions`): a bare `*` already spans `/` and spaces, so the shipped `*`-only rule matches nested skill script paths — no live prompt-trigger test needed to settle this.

## 3. Implementation Steps

- [x] Step 1: Update `install.py` with multi-environment permission merging functions (`merge_settings`, `merge_antigravity_permissions`, `merge_kiro_permissions`).
- [x] Step 2: Update `inspect_status()` and `print_summary()` in `install.py`.
- [x] Step 3: Update `docs/index.md` with active plan entry and reference doc.
- [x] Step 4: Run `python3 install.py` to test live deployment on local machine.
- [x] Step 5: Update `CHANGELOG.md` for `[2.4.2]`.
- [x] Step 6: Move plan to `docs/plan/done/` upon completion.
