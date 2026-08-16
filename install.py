#!/usr/bin/env python3
"""akidevrule installer — cross-platform SSOT.

Reproduces every observable effect of install.sh. The three launchers
(install.sh, install.ps1) are thin wrappers that exec this file.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# A launcher can still hand this an interpreter below the floor install.sh targets — fail in one line rather than 500 lines deep, where a 3.7-only feature once crashed.
if sys.version_info < (3, 7):
    sys.exit("akidevrule: requires Python 3.7+, running %s" % sys.version.split()[0])

# Windows pipes stdout as the legacy locale codec (cp1252), which cannot encode the emoji this installer prints — force UTF-8 so status output never crashes the run.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
HOME = Path.home()
INSTALL_ROOT = HOME / ".aki" / "akidevrule"
LEGACY_INSTALL_ROOT = HOME / ".aki" / "claudedoc"
CLAUDE_DIR = HOME / ".claude"
GEMINI_DIR = HOME / ".gemini"
GEMINI_RULES_DIR = GEMINI_DIR / "config" / "rules"
GEMINI_SKILLS_DIR = GEMINI_DIR / "config" / "skills"

CODEX_SKILLS_DIR = HOME / ".agents" / "skills"
KIRO_SKILLS_DIR = HOME / ".kiro" / "skills"
GROK_SKILLS_DIR = HOME / ".grok" / "skills"

OLD_SKILLS = ["akidoc-rules", "akidoc-flow-audit", "akidoc-techbiz-optimizer", "akiadvise"]

STAMP = datetime.now().strftime("%Y%m%d%H%M%S")

# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------

def _ansi_supported() -> bool:
    if not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        # Modern Windows Terminal / VS Code support ANSI via ENABLE_VIRTUAL_TERMINAL_PROCESSING, but legacy cmd.exe does not; TERM/WT_SESSION is the heuristic.
        return os.environ.get("TERM") is not None or os.environ.get("WT_SESSION") is not None
    return True


_USE_COLOR = _ansi_supported()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def cyan_bold(t: str) -> str:
    return _c("1;36", t)


def green_bold(t: str) -> str:
    return _c("1;32", t)


def yellow_bold(t: str) -> str:
    return _c("1;33", t)


def red_bold(t: str) -> str:
    return _c("1;31", t)


def blue_bold(t: str) -> str:
    return _c("1;34", t)


# ---------------------------------------------------------------------------
# Backup / prune
# ---------------------------------------------------------------------------

def backup(path: Path) -> None:
    if path.exists():
        dest = path.parent / f"{path.name}.akidevrule-backup-{STAMP}"
        if path.is_dir():
            shutil.copytree(path, dest)
        else:
            shutil.copy2(path, dest)


def prune_backups(base: Path) -> None:
    """Keep the 2 most recent backups for *base*, delete older ones."""
    pattern = f"{base.name}.akidevrule-backup-*"
    candidates = sorted(
        base.parent.glob(pattern),
        key=lambda p: p.stat().st_mtime,
    )
    for old in candidates[:-2]:
        print(f"  🗑️  Removing old backup: {old.name}")
        if old.is_dir():
            shutil.rmtree(old)
        else:
            old.unlink()


# ---------------------------------------------------------------------------
# Directory sync (replaces rsync -a --delete, scoped to Aki-owned names)
# ---------------------------------------------------------------------------

def sync_dir_delete(src: Path, dest: Path) -> None:
    """Mirror src → dest, removing files/dirs in dest that no longer exist in src.

    Semantics match `rsync -a --delete src/ dest/`: dest ends up identical to src.
    This is ONLY used for directories we fully own (e.g. payload/, per-skill folders).
    """
    dest.mkdir(parents=True, exist_ok=True)
    src_names = {p.name for p in src.iterdir()}

    # Remove anything in dest that is not in src.
    for child in list(dest.iterdir()):
        if child.name not in src_names:
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    # Copy everything from src to dest.
    for child in src.iterdir():
        dst_child = dest / child.name
        if child.is_dir():
            sync_dir_delete(child, dst_child)
        else:
            shutil.copy2(child, dst_child)


def sync_aki_skills(dest_root: Path) -> None:
    """Sync each Aki skill folder into dest_root, scoped per skill name.

    Per-skill sync uses --delete semantics (only files Aki owns inside that
    folder are pruned). Foreign skills sitting alongside in dest_root are
    never touched.
    """
    dest_root.mkdir(parents=True, exist_ok=True)
    skills_src = REPO_ROOT / "skills"
    if not skills_src.is_dir():
        return
    for skill_dir in sorted(skills_src.iterdir()):
        if not skill_dir.is_dir():
            continue
        sync_dir_delete(skill_dir, dest_root / skill_dir.name)
    for old_skill in OLD_SKILLS:
        old_path = dest_root / old_skill
        if old_path.exists():
            shutil.rmtree(old_path)


def sync_aki_agents() -> None:
    """Copy agent files one by one — never mirror with delete (shared namespace)."""
    agents_src = REPO_ROOT / "claude" / "agents"
    if not agents_src.is_dir():
        return
    dest = CLAUDE_DIR / "agents"
    dest.mkdir(parents=True, exist_ok=True)
    for agent_file in sorted(agents_src.glob("*.md")):
        shutil.copy2(agent_file, dest / agent_file.name)


# ---------------------------------------------------------------------------
# Text file writing (always LF, never CRLF)
# ---------------------------------------------------------------------------

def write_text_lf(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git_short_hash(repo: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def git_branch(repo: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Antigravity rule map
# ---------------------------------------------------------------------------

# Each entry: (rule_file, trigger, description, globs) — globs is a raw JSON array string or empty string.
AG_RULE_MAP = [
    ("RULE-agent-behavior.md", "always_on", "", ""),
    ("RULE-coding.md", "model_decision",
     'Coding philosophy, source-of-truth discipline, error handling and security. Load when writing, reviewing or refactoring code.',
     ""),
    ("RULE-pattern-core.md", "model_decision",
     'Universal design laws: single source of truth, Rule of Three, single-responsibility "and"-test, composition over inheritance, naming by role. Load on any structural or decomposition decision.',
     ""),
    ("RULE-docs.md", "model_decision",
     'Documentation structure, plan lifecycle, doc-sync behavior and the docs-versus-code drift audit. Load when writing or reorganizing docs and plans, or when checking whether existing docs still match the code.',
     ""),
    ("RULE-content-write.md", "model_decision",
     'UI copy, semantic stability, writing style and i18n. Load when writing user-facing text.',
     ""),
    ("RULE-stack-akiNuxtCf.md", "glob",
     'Nuxt, Vue, Cloudflare Pages and Workers, Tailwind, i18n, state and build conventions. Load when working in a Nuxt or Cloudflare project.',
     '["**/*.vue", "**/*.ts", "nuxt.config.*", "server/**/*.ts"]'),
    ("RULE-stack-tauri.md", "glob",
     'Tauri v2 and Rust conventions, including the never-block-the-UI rule for subprocess and network commands. Load when working in a Tauri project.',
     '["src-tauri/**", "**/*.rs", "tauri.conf.json"]'),
    ("RULE-ui-pattern.md", "model_decision",
     'Frontend design-system layer: the subtraction pass that runs before the class-tier ladder, class taxonomy, design tokens in whichever mechanism the installed framework version uses, the aggregate style-block budget, arbitrary-value policy, variant APIs and the audit playbook. Load when building, minimizing or auditing UI components and styles.',
     ""),
    ("RULE-seo.md", "model_decision",
     'Meta limits, schema.org, robots, sitemap, Open Graph and AI visibility. Load when working on SEO or page metadata.',
     ""),
    ("RULE-release.md", "model_decision",
     'CHANGELOG discipline, release versus deploy boundary, severity-driven version bumps and the pre-ship gate for finished-but-unpushed work. Load when preparing a release, writing a changelog, or checking whether finished work is actually shippable.',
     ""),
    ("RULE-db-design.md", "model_decision",
     'Immutability and event sourcing, normalization, bounded contexts, flat-query discipline. Load when designing a schema, migration or database refactor.',
     ""),
    ("RULE-biz.md", "model_decision",
     'Positioning, audience, USP, pricing, monetization and customer-psychology messaging rules. Load on any market-facing decision or when working on docs/biz content.',
     ""),
    ("METHOD-flow-audit.md", "model_decision",
     'Method for auditing end-to-end flow integrity. Load when guards and checks keep accumulating around a flow.',
     ""),
    ("METHOD-zero-trust-audit.md", "model_decision",
     'Strict mechanical-first audit: scope locked by command, detectors run before any opinion, findings split into exact machine matches versus pattern-level candidates, short findings-only report. Load when the user asks for an uncompromising sweep of a project or of a change and everything it touches.',
     ""),
    ("METHOD-deep-think.md", "model_decision",
     'Deep-think method: goal excavation, first principles, mandatory critique. Load for big, hard-to-reverse or goal-ambiguous decisions.',
     ""),
    ("METHOD-ux-psych.md", "model_decision",
     'UX psychology audit: cognitive load, recognition, feedback, defaults, motor cost and mental-model lenses with a persona walkthrough protocol. Load when evaluating an interface or user flow through user behavior.',
     ""),
    ("METHOD-proportionality.md", "model_decision",
     'Sizing a defense against its real threat: reach, capability, motive and blast radius measured before any guard, limit, quota or accepted risk is added, kept or removed; irreversibility outranks frequency; client-side limits are UX, never enforcement. Load whenever protection is being proposed, sized or dropped.',
     ""),
    ("METHOD-subtraction-audit.md", "model_decision",
     'Repo-wide subtraction sweep asking what no longer needs to exist, terminating on two consecutive rounds with no new findings, with Chesterton\'s Fence as the brake before any removal is called certain. Load when the request is to minimize or strip an existing codebase rather than to check it is correct.',
     ""),
]


def _ag_dest_name(rule_file: str) -> str:
    """akirule-<stem>.md — strips RULE-/METHOD- prefix and lowercases."""
    stem = re.sub(r"^(RULE|METHOD)-", "", rule_file)
    stem = re.sub(r"\.md$", "", stem)
    return f"akirule-{stem.lower()}.md"


def install_ag_rules() -> int:
    """Generate Antigravity rule files with YAML frontmatter. Returns count written."""
    GEMINI_RULES_DIR.mkdir(parents=True, exist_ok=True)
    # Remove stale akirule-* files from a previous install.
    for stale in GEMINI_RULES_DIR.glob("akirule-*.md"):
        stale.unlink()

    written = 0
    for rule_file, trigger, desc, globs in AG_RULE_MAP:
        src = REPO_ROOT / "payload" / rule_file
        if not src.is_file():
            print(f"  ⚠️  {rule_file} listed in AG_RULE_MAP but missing from payload/")
            continue
        dest = GEMINI_RULES_DIR / _ag_dest_name(rule_file)

        lines = ["---", f"trigger: {trigger}"]
        if globs:
            lines.append(f"globs: {globs}")
        if trigger != "always_on" and desc:
            lines.append(f"description: {json.dumps(desc)}")
        lines.append("---")
        lines.append("")
        lines.append(f"<!-- Generated by akidevrule install.py from payload/{rule_file}. Do not edit here. -->")
        lines.append("")
        lines.append(src.read_text(encoding="utf-8"))

        write_text_lf(dest, "\n".join(lines))
        written += 1
    return written


# ---------------------------------------------------------------------------
# settings.json merge
# ---------------------------------------------------------------------------

def merge_settings(settings_path: Path, install_root: Path, claude_dir: Path) -> None:
    data = json.loads(settings_path.read_text(encoding="utf-8"))

    if not isinstance(data.get("permissions"), dict):
        data["permissions"] = {}
    perms = data["permissions"]
    if not isinstance(perms.get("allow"), list):
        perms["allow"] = []
    if not isinstance(perms.get("additionalDirectories"), list):
        perms["additionalDirectories"] = []

    read_rule = f'Read(//{str(install_root).lstrip("/")}/**)'
    legacy_root = HOME / ".aki" / "claudedoc"
    legacy_read_rule = f'Read(//{str(legacy_root).lstrip("/")}/**)'
    perms["allow"] = [x for x in perms["allow"] if x not in (read_rule, legacy_read_rule)]
    perms["allow"].append(read_rule)

    legacy_str = str(legacy_root)
    install_str = str(install_root)
    perms["additionalDirectories"] = [d for d in perms["additionalDirectories"] if d != legacy_str]
    if install_str not in perms["additionalDirectories"]:
        perms["additionalDirectories"].append(install_str)

    if not isinstance(data.get("skillOverrides"), dict):
        data["skillOverrides"] = {}
    for old in ["akidoc-rules", "akidoc-flow-audit", "akidoc-techbiz-optimizer"]:
        data["skillOverrides"].pop(old, None)
    data["skillOverrides"]["akirule"] = "on"

    if not isinstance(data.get("hooks"), dict):
        data["hooks"] = {}
    hooks = data["hooks"]
    if not isinstance(hooks.get("SessionStart"), list):
        hooks["SessionStart"] = []

    def _is_aki_update(entry):
        try:
            return any("aki-update-check" in h.get("command", "") for h in entry.get("hooks", []))
        except Exception:
            return False

    hooks["SessionStart"] = [e for e in hooks["SessionStart"] if not _is_aki_update(e)]
    hooks["SessionStart"].append({
        "matcher": "startup|resume",
        "hooks": [{
            "type": "command",
            "command": f'python3 "{claude_dir}/hooks/aki-update-check.py"',
            "timeout": 8,
        }],
    })

    write_text_lf(settings_path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# skills.json for Antigravity
# ---------------------------------------------------------------------------

def update_skills_json() -> None:
    skills_json = GEMINI_DIR / "config" / "skills.json"
    skills_json.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if skills_json.exists():
        try:
            data = json.loads(skills_json.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    if not isinstance(data.get("entries"), list):
        data["entries"] = []

    abs_path = str(INSTALL_ROOT / "agskills")
    tilde_path = "~/.aki/akidevrule/agskills"
    for p in [abs_path, tilde_path]:
        if not any(isinstance(e, dict) and e.get("path") == p for e in data["entries"]):
            data["entries"].append({"path": p})

    write_text_lf(skills_json, json.dumps(data, indent=2) + "\n")


# ---------------------------------------------------------------------------
# inspect_status (pre-install preview)
# ---------------------------------------------------------------------------

def inspect_status() -> None:
    print(cyan_bold("=== SYSTEM STATUS CHECK BEFORE INSTALL ==="))

    if INSTALL_ROOT.is_dir():
        print(f"📦 Payload rules: will {yellow_bold('OVERWRITE')} {INSTALL_ROOT}")
    else:
        print(f"📦 Payload rules: will {green_bold('CREATE')} at {INSTALL_ROOT}")

    claude_md = CLAUDE_DIR / "CLAUDE.md"
    if claude_md.is_file():
        print(f"📝 Global CLAUDE.md: will {yellow_bold('OVERWRITE')} {claude_md} (backed up)")
    else:
        print(f"📝 Global CLAUDE.md: will {green_bold('CREATE')} {claude_md}")

    skills_src = REPO_ROOT / "skills"
    if skills_src.is_dir():
        for skill_dir in sorted(skills_src.iterdir()):
            if not skill_dir.is_dir():
                continue
            name = skill_dir.name
            dest_skill = CLAUDE_DIR / "skills" / name / "SKILL.md"
            if dest_skill.is_file():
                print(f"🔧 Skill {name}: will {yellow_bold('OVERWRITE')} {dest_skill}")
            else:
                print(f"🔧 Skill {name}: will {green_bold('CREATE')} {dest_skill}")

    agents_src = REPO_ROOT / "claude" / "agents"
    if agents_src.is_dir():
        for agent_file in sorted(agents_src.glob("*.md")):
            name = agent_file.name
            dest_agent = CLAUDE_DIR / "agents" / name
            if dest_agent.is_file():
                print(f"🧠 Agent {name}: will {yellow_bold('OVERWRITE')} {dest_agent}")
            else:
                print(f"🧠 Agent {name}: will {green_bold('CREATE')} {dest_agent}")

    old_present = [s for s in OLD_SKILLS if (CLAUDE_DIR / "skills" / s).is_dir()]
    if old_present:
        print(f"🗑️  Old skills will be REMOVED: {red_bold(' '.join(old_present))}")

    print("⚙️  settings.json: checking read permissions and skill overrides...")
    settings_path = CLAUDE_DIR / "settings.json"
    if settings_path.is_file():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            read_rule = f'Read(//{str(INSTALL_ROOT).lstrip("/")}/**)'
            allow = data.get("permissions", {}).get("allow", [])
            if read_rule in allow:
                print("  ✅ Read permission for the payload directory already granted.")
            else:
                print("  ⚠️  Read permission MISSING. Will be added automatically.")
            overrides = data.get("skillOverrides", {})
            if overrides.get("akirule") == "on":
                print("  ✅ akirule skill is already enabled (on).")
            else:
                print("  ⚠️  Will auto-enable skill: akirule")
            stale = [s for s in ["akidoc-rules", "akidoc-flow-audit", "akidoc-techbiz-optimizer"] if s in overrides]
            if stale:
                print(f"  🗑️  Stale skillOverrides will be REMOVED: {', '.join(stale)}")
        except Exception as e:
            print(f"  ❌ Error reading settings.json: {e}")
    else:
        print("  ⚠️  No settings.json yet. Will be CREATED.")

    print(cyan_bold("===================================================="))


# ---------------------------------------------------------------------------
# print_summary (post-install)
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(f"\n{green_bold('=== INSTALL SUCCEEDED ===')}")

    git_hash = git_short_hash(REPO_ROOT)
    hash_suffix = f" ({git_hash})" if git_hash else ""
    print(f"📅 Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{hash_suffix}")
    print(f"📂 Payload : {INSTALL_ROOT}")
    print(f"🔧 Skills  : {CLAUDE_DIR / 'skills' / ''}")
    print()

    print(cyan_bold("Rules deployed:"))
    index_path = INSTALL_ROOT / "index.md"
    if index_path.is_file():
        tier_colors = {
            "Core": red_bold,
            "Contextual": yellow_bold,
            "Analytical": blue_bold,
        }
        for line in index_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r'\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|(.+)\|', line)
            if m:
                fname, tier, desc = m.group(1), m.group(2).strip(), m.group(3).strip()
                color_fn = next((fn for k, fn in tier_colors.items() if tier.startswith(k)), None)
                tier_str = color_fn(f"{tier:<12}") if color_fn else f"{tier:<12}"
                print(f"  {tier_str} {fname:<30} {desc}")

    print()
    print(cyan_bold("Skills deployed:"))
    claude_skills = CLAUDE_DIR / "skills"
    if claude_skills.is_dir():
        for skill_dir in sorted(claude_skills.iterdir()):
            if skill_dir.is_dir():
                print(f"  🔧 {skill_dir.name}")

    agents_src = REPO_ROOT / "claude" / "agents"
    if agents_src.is_dir():
        print()
        print(cyan_bold(f"Agents deployed ({CLAUDE_DIR / 'agents'} — your own agents there are untouched):"))
        for agent_file in sorted(agents_src.glob("*.md")):
            print(f"  🧠 {agent_file.stem}")

    print()
    print(cyan_bold("Other CLI skill roots synced (harmless if that CLI isn't installed):"))
    print(f"  🤖 Codex CLI : {CODEX_SKILLS_DIR}")
    print(f"  🤖 Kiro CLI  : {KIRO_SKILLS_DIR}")
    print(f"  🤖 Grok CLI  : {GROK_SKILLS_DIR}")

    print()
    print(cyan_bold("Hooks deployed:"))
    print("  📢 aki-update-check (SessionStart, notify-only) — notifies when a new rule version is available")

    print(f"\n{green_bold('==============================')}")


# ---------------------------------------------------------------------------
# Main install logic
# ---------------------------------------------------------------------------

def run_install() -> None:
    # Legacy migration: ~/.aki/claudedoc → ~/.aki/akidevrule
    if LEGACY_INSTALL_ROOT.is_dir() and not INSTALL_ROOT.exists():
        shutil.move(str(LEGACY_INSTALL_ROOT), str(INSTALL_ROOT))
        print(f"📦 Migrated legacy install root: {LEGACY_INSTALL_ROOT} → {INSTALL_ROOT}")

    inspect_status()

    # Prompt for confirmation only when stdin is a TTY.
    if sys.stdin.isatty():
        confirm = input("Proceed with install/update given the changes above? (y/n): ").strip()
        if confirm.lower() != "y":
            print("Install cancelled.")
            sys.exit(1)
    print("Installing...")

    # --- 1. Payload → INSTALL_ROOT ---
    INSTALL_ROOT.mkdir(parents=True, exist_ok=True)
    (CLAUDE_DIR / "skills").mkdir(parents=True, exist_ok=True)

    payload_src = REPO_ROOT / "payload"
    EXCLUDED = {"ref-ECC", ".DS_Store", "GEMINI.md"}
    INSTALL_ROOT.mkdir(parents=True, exist_ok=True)
    src_names = {p.name for p in payload_src.iterdir() if p.name not in EXCLUDED}
    # Remove files from INSTALL_ROOT that are no longer in payload/ (rsync --delete semantics).
    # Dotfiles (.version, .source-repo, CHANGELOG.md, agskills/) are managed explicitly, leave them.
    MANAGED_EXTENSIONS = {".md"}
    for child in list(INSTALL_ROOT.iterdir()):
        if child.name.startswith("."):
            continue
        if child.suffix in MANAGED_EXTENSIONS and child.name not in src_names:
            child.unlink()
    # Copy all non-excluded payload files into INSTALL_ROOT.
    for child in payload_src.iterdir():
        if child.name in EXCLUDED:
            continue
        dst = INSTALL_ROOT / child.name
        if child.is_dir():
            sync_dir_delete(child, dst)
        else:
            shutil.copy2(child, dst)

    # Explicit removal of renamed/dropped files.
    stale = INSTALL_ROOT / "METHOD-techbiz-optimizer.md"
    if stale.exists():
        stale.unlink()

    # Copy CHANGELOG so any machine knows what's installed without the repo.
    shutil.copy2(REPO_ROOT / "CHANGELOG.md", INSTALL_ROOT / "CHANGELOG.md")

    # Write version stamp.
    version_lines = [f"installed={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
    git_hash = git_short_hash(REPO_ROOT)
    if git_hash:
        version_lines.append(f"commit={git_hash}")
        branch = git_branch(REPO_ROOT)
        if branch:
            version_lines.append(f"branch={branch}")
    write_text_lf(INSTALL_ROOT / ".version", "\n".join(version_lines) + "\n")

    # --- 2. Skills ---
    sync_aki_skills(CLAUDE_DIR / "skills")
    sync_aki_skills(CODEX_SKILLS_DIR)
    sync_aki_skills(KIRO_SKILLS_DIR)
    sync_aki_skills(GROK_SKILLS_DIR)

    # --- 3. Agents ---
    sync_aki_agents()

    # --- 4. Hook + source-repo ---
    hooks_dest = CLAUDE_DIR / "hooks"
    hooks_dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / "claude" / "hooks" / "aki-update-check.py",
                 hooks_dest / "aki-update-check.py")
    write_text_lf(INSTALL_ROOT / ".source-repo", str(REPO_ROOT) + "\n")

    # --- 5. CLAUDE.md ---
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    backup(CLAUDE_DIR / "CLAUDE.md")
    print("🧹 Pruning CLAUDE.md backups (keeping the 2 most recent):")
    prune_backups(CLAUDE_DIR / "CLAUDE.md")

    claude_md_src = (REPO_ROOT / "claude" / "CLAUDE.md").read_text(encoding="utf-8")
    rule_source_block = (
        "\n## akidevrule — edit source, not deployed copy (ABSOLUTE)\n\n"
        f"The deployed rule files at `{INSTALL_ROOT}` are **overwritten on every install**.\n"
        "To change any shared rule:\n"
        f"1. Edit in the **source repo**: `{REPO_ROOT}/payload/`\n"
        f"2. Run `bash {REPO_ROOT}/install.sh` to propagate.\n\n"
        f"**NEVER edit files under `{INSTALL_ROOT}` directly** — changes will be silently lost on the next install.\n\n"
        "@~/.claude/CLAUDE.local.md\n"
    )
    write_text_lf(CLAUDE_DIR / "CLAUDE.md", claude_md_src + rule_source_block)

    # --- 6. CLAUDE.local.md (create-only) ---
    local_md = CLAUDE_DIR / "CLAUDE.local.md"
    if not local_md.is_file():
        write_text_lf(local_md, (
            "# Machine-local Claude instructions\n\n"
            "This file is machine-specific and never touched by akidevrule installs.\n"
            "Add any per-machine rules here (e.g. build constraints, IDE paths, remote flags).\n"
        ))
        print(f"📝 Created {local_md} (machine-local template)")

    # --- 7. GEMINI.md (only when ~/.gemini exists) ---
    if GEMINI_DIR.is_dir():
        gemini_file = GEMINI_DIR / "GEMINI.md"
        gemini_local = GEMINI_DIR / "GEMINI.local.md"
        gemini_marker = "[AKIRULE-AG-OVERRIDES-"

        had_unmanaged = (
            gemini_file.is_file()
            and gemini_marker not in gemini_file.read_text(encoding="utf-8", errors="replace")
        )

        # Create machine-local template (create-only).
        if not gemini_local.is_file():
            write_text_lf(gemini_local, (
                "# Machine-local GEMINI instructions\n\n"
                "This file is machine-specific and never touched by akidevrule installs.\n"
                "Add machine-specific paths, CLIs, and emulator commands here.\n"
            ))
            print(f"📝 Created {gemini_local} (machine-local template)")

        backup(gemini_file)
        print("🧹 Pruning GEMINI.md backups (keeping the 2 most recent):")
        prune_backups(gemini_file)

        # Apply version marker to GEMINI.md template.
        gemini_version = f"V{datetime.now().strftime('%Y%m%d')}"
        gemini_template = (REPO_ROOT / "payload" / "GEMINI.md").read_text(encoding="utf-8")
        gemini_content = gemini_template.replace("__VERSION__", gemini_version)

        gemini_source_block = (
            "\n## 9. Shared rule source — edit source, not deployed copy (ABSOLUTE)\n\n"
            f"The deployed rule corpus at `{INSTALL_ROOT}` is **overwritten on every install**.\n"
            "To change any shared rule:\n"
            f"1. Edit in the **source repo**: `{REPO_ROOT}/payload/` (rules) or `{REPO_ROOT}/claude/` (runtime assets).\n"
            f"2. Read `{REPO_ROOT}/CLAUDE.md` first — it lists which files must be updated together.\n"
            f"3. Run `bash {REPO_ROOT}/install.sh` to propagate.\n\n"
            f"**NEVER edit files under `{INSTALL_ROOT}` directly** — changes are silently lost on the next install.\n"
        )

        local_content = gemini_local.read_text(encoding="utf-8")
        full_gemini = gemini_content + gemini_source_block + "\n---\n\n" + local_content
        write_text_lf(gemini_file, full_gemini)

        print(f"🤖 Installed {gemini_file} (marker {gemini_marker}{gemini_version}])")
        if had_unmanaged:
            print(f"  ⚠️  Your previous ~/.gemini/GEMINI.md was replaced (saved as *.akidevrule-backup-*).")
            print(f"      Move any machine-local lines from that backup into {gemini_local}.")

        # --- 8. Antigravity rules ---
        ag_count = install_ag_rules()
        print(f"🧭 Installed {ag_count} rule(s) to {GEMINI_RULES_DIR} (read by AG, AG IDE and AGY)")

        # --- 9. Antigravity skills ---
        sync_aki_skills(GEMINI_SKILLS_DIR)
        sync_aki_skills(INSTALL_ROOT / "agskills")
        update_skills_json()
        print(f"💡 Deployed skills to {GEMINI_SKILLS_DIR} & updated ~/.gemini/config/skills.json")
        print("  ℹ️  Antigravity discovers rules and skills at startup — restart the app or start a new agy session.")

    # --- 10. settings.json ---
    settings_path = CLAUDE_DIR / "settings.json"
    if not settings_path.is_file():
        write_text_lf(settings_path, "{}\n")
    backup(settings_path)
    print("🧹 Pruning settings.json backups (keeping the 2 most recent):")
    prune_backups(settings_path)
    merge_settings(settings_path, INSTALL_ROOT, CLAUDE_DIR)

    print_summary()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="akidevrule installer — deploys shared rule corpus and skills.",
    )
    # Accepts any flags install.sh might have been called with; no-ops today but keeps the thin launchers forwards-compatible.
    parser.parse_args()
    run_install()


if __name__ == "__main__":
    main()
