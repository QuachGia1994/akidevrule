# Multi-CLI Permission & Allowlist Standard

## The fact

Agent Skills (`SKILL.md`) frequently contain deterministic Python scripts (e.g. `scythe.py` format lint, `council_verify.py` gate validation) meant to run unattended. When an agent CLI/IDE executes these scripts via shell/command tools, platform security policies prompt the user for permission unless pre-allowed in the platform's configuration.

Each AI developer environment implements its own permission schema, syntax, and configuration path:

| Platform | Configuration Path | Rule Syntax | Wildcard Support | Evaluation Order |
|---|---|---|---|---|
| **Claude Code** | `~/.claude/settings.json` | `Bash(python3 ~/.claude/skills/*)` | `*` only | Deny → Ask → Allow |
| **Antigravity CLI (`agy`)** | `~/.gemini/antigravity-cli/settings.json` | `command(python3 ~/.gemini/config/skills/*)` | `*` | Deny → Ask → Allow |
| **Antigravity IDE & Desktop** | `~/.gemini/settings.json` | `command(python3 ~/.gemini/config/skills/*)` | `*` | Deny → Ask → Allow |
| **Kiro CLI (3.0+)** | `~/.kiro/settings/permissions.yaml` | `capability: shell`, `match: ["python3 ~/.kiro/skills/*"]` | Glob matching | Deny → Ask → Allow |
| **Grok CLI** | `~/.grok/user-settings.json` | `Bash(python3 ~/.grok/skills/*)` | `*` only | Deny → Ask → Allow |
| **Codex CLI** | `~/.codex/config.toml` | `prefix_rule(pattern = ["python3", ...], decision = "allow")` | Prefix array | Priority-based |

---

## 1. Platform Details & Configurations

### 1.1 Claude Code
- **Path**: `~/.claude/settings.json`
- **Schema**:
  ```json
  {
    "permissions": {
      "allow": [
        "Read(//~/.aki/akidevrule/**)",
        "Bash(python3 ~/.claude/skills/*)",
        "Bash(python3 ~/.aki/akidevrule/agskills/*)"
      ]
    }
  }
  ```
- **Semantics** (verified against Claude Code's own docs, `code.claude.com/docs/en/permissions`): `Bash` rules have **no** gitignore-style `**` — that distinction exists only for `Read`/`Edit` path rules. A bare `*` in a `Bash` rule already matches any sequence of characters *including* `/` and spaces, so it spans multiple path segments and arguments on its own (`Bash(git *)` matches `git log --oneline --all`). Writing `**` adds nothing — it is a dead-weight duplicate of `*`, not a broader match. A **space before a trailing `*`** enforces a word boundary (`Bash(ls *)` matches `ls -la` but not `lsof`; `Bash(ls*)` with no space matches both) — irrelevant here since the path's own `/` already acts as the boundary.

### 1.2 Google Antigravity (AGY CLI, IDE, Desktop)
- **Paths**:
  - CLI: `~/.gemini/antigravity-cli/settings.json`
  - Global IDE/Desktop: `~/.gemini/settings.json`
- **Schema**:
  ```json
  {
    "permissions": {
      "allow": [
        "command(python3 ~/.claude/skills/*)",
        "command(python3 ~/.gemini/config/skills/*)",
        "command(python3 ~/.aki/akidevrule/agskills/*)"
      ]
    }
  }
  ```
- **CLI Flag (headless/unattended)**: `agy --dangerously-skip-permissions -p "<prompt>"`

### 1.3 Kiro CLI
- **Path**: `~/.kiro/settings/permissions.yaml`
- **Schema**:
  ```yaml
  rules:
    - capability: shell
      match:
        - "python3 ~/.kiro/skills/*"
        - "python3 ~/.claude/skills/*"
        - "python3 ~/.aki/akidevrule/agskills/*"
      effect: allow
  ```
- **CLI Flag**: `kiro-cli chat --trust-all-tools`

### 1.4 Grok CLI
- **Path**: `~/.grok/user-settings.json`
- **Schema**: Uses Claude Code-compatible syntax:
  ```json
  {
    "permissions": {
      "allow": [
        "Bash(python3 ~/.grok/skills/*)",
        "Bash(python3 ~/.claude/skills/*)"
      ]
    }
  }
  ```

---

## 2. Pre-allow Principles for akidevrule

1. **Principle of Least Privilege**: Only pre-allow Python execution for explicitly managed skill and payload script paths (`~/.claude/skills/*`, `~/.gemini/config/skills/*`, `~/.kiro/skills/*`, `~/.aki/akidevrule/agskills/*`). Never grant open-ended `Bash(python3 *)` or `command(python3 *)`.
2. **Non-destructive Merging**: `install.py` must preserve existing user permissions, settings keys, and comments/formatting where possible, only inserting or updating the managed entries idempotently.
3. **Multi-surface Portability**: Skills should resolve scripts relative to their installed location or fallback gracefully across CLI environments.
