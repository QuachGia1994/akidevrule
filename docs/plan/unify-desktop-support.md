# Plan — unify desktop support (macOS · Linux · Windows)

**Status:** ✅ implemented (2026-08-11, v2.0.0) — all three batches shipped: `install.py` SSOT + `install.ps1`/`install.sh` launchers, five helpers ported to Python, CI install-smoke gate, docs synced. §11 mcp-sv coupling deliberately left open; the mcp-sv repo was not touched.

**Owner framing (2026-08-10):** only macOS and Linux work today; no Windows machine available for local test; rewriting every `.sh` into `.ps1`/`.bat` is costly but worth weighing; Windows is the largest user base and must be supported eventually; **akidevrule is now a dependency of [aki-mcp-sv](https://github.com/lacvietanh/aki-mcp-sv)** (force-loaded core rules in the paste-in instruction prompt, trusted script dirs under `~/.aki`, and an explicit Windows install note already present on the mcp-sv side).

**Decisions locked (2026-08-10):**

| Decision | Choice |
|---|---|
| Installer language | **Python SSOT** (`install.py`); thin `install.sh` / `install.ps1` launchers only |
| Skill runtime scripts | **Python SSOT** as well — not dual `.sh`/`.ps1`, not bash-only forever |
| Sequencing | Phased: installer first (Batch 1), then skill helpers (Batch 2), polish (Batch 3) |
| Dual PowerShell ports of every helper | **Rejected** as primary strategy |

**Baseline:** current `install.sh` + five `skills/akiflow/scripts/*.sh` + one Python hook (`claude/hooks/aki-update-check.py`). README marks Windows ❌.

---

## 1. Problem statement

| Fact | Consequence |
|---|---|
| Installer and runtime helpers are POSIX bash (`set -euo pipefail`, process substitution, bash arrays, `BASH_SOURCE`, `find`/`rsync`/`sed`/`awk`) | Native Windows (PowerShell / cmd) cannot run them |
| `python3` is already a hard dependency of `install.sh` (settings.json merge, AG rule frontmatter, status printing) | A second language is already in the critical path — the cost of "Python as SSOT" is largely paid |
| Payload + skills content is pure text (`RULE-*.md`, `METHOD-*.md`, `SKILL.md`) | Content layer is already OS-neutral; only delivery and a few mechanical scripts are not |
| aki-mcp-sv already claims **Windows, Linux, macOS** and force-loads akidevrule core | Windows mcp-sv users get a degraded path: instruction prompt can name rules that were never installed into `%USERPROFILE%\.aki\akidevrule` |
| Owner has no Windows box | Any solution must be CI-testable (`windows-latest`) and/or community-testable; "works on my Mac under Wine" is not a gate |

This is not a content problem. It is a **delivery + mechanical-script** problem, with a **dependency amplification** (mcp-sv) that makes postponement more expensive every release.

---

## 2. Inventory of OS-sensitive surface

### 2.1 Install path (must work on day one of Windows support)

| Asset | Role | POSIX-only techniques |
|---|---|---|
| `install.sh` | Full installer | `bash` arrays, process substitution, `rsync --delete`, `find`+`sort`+`head` for backup prune, `sed`/`tr` for AG dest names, ANSI `echo -e`, `~`-rooted paths, `cp -R` |
| Embedded `python3` blocks inside `install.sh` | settings.json, skills.json, AG description JSON-escape, summary from `index.md` | Already portable if invoked as `python`/`python3` with pathlib |
| `claude/hooks/aki-update-check.py` | SessionStart notify-only | Already Python — portable with minor path fixes |

### 2.2 Runtime helpers (used after install, mainly by `/akiflow` and `/akilint`)

| Script | Role | Portability notes |
|---|---|---|
| `skills/akiflow/scripts/council-open.sh` | Open session dir, prune >N days, pin anchor | `find -mtime`, process substitution, `git rev-parse`, slugify via `tr`/`sed` |
| `skills/akiflow/scripts/council-read.sh` | Slice `chat.md` without loading whole file | Pure text slicing — Python-natural |
| `skills/akiflow/scripts/council-verify.sh` | Mechanical closure gate (6 checks) | Grep/awk-heavy — high value to port |
| `skills/akiflow/scripts/council-cost.sh` | Token tally from transcript | Parse-only — Python-friendly |
| `skills/akiflow/scripts/scythe.sh` | `[WRAP]`/`[YAP]` detector | Heavy `awk` (mawk-sensitive history already in CHANGELOG). Highest logic density; port last with fixtures |

### 2.3 Content that is already neutral

- Entire `payload/` rule corpus
- Entire `skills/*/SKILL.md` (and most references)
- `claude/agents/*.md` (Claude Code format; path separators inside docs need a pass for Windows examples)
- Generated AG rules under `~/.gemini/config/rules/` (text files)

### 2.4 Consumer CLIs — path conventions to verify on Windows

| Target | Unix path today | Windows expectation (to confirm) |
|---|---|---|
| Shared rule SSOT | `~/.aki/akidevrule/` | `%USERPROFILE%\.aki\akidevrule\` |
| Claude Code | `~/.claude/` | `%USERPROFILE%\.claude\` (verify with Claude Code Windows build) |
| Antigravity / Gemini | `~/.gemini/` | `%USERPROFILE%\.gemini\` (verify) |
| Codex CLI skills | `~/.agents/skills/` | verify |
| Kiro CLI skills | `~/.kiro/skills/` | verify |
| Grok CLI skills | `~/.grok/skills/` | verify |

**Open verification items (blockers for a correct Windows install map):** exact skill roots and settings paths for each CLI on Windows; whether Claude Code's `@`-import in `CLAUDE.md` accepts backslashes or requires forward slashes; whether `Read(//path/**)` permission rules use POSIX-style paths only.

---

## 3. Strategic options (cost × risk × drift)

| Option | Idea | Cost to ship | Ongoing drift | Risk | Verdict |
|---|---|---|---|---|---|
| **A. Dual shell** | Keep `install.sh`, add parallel `install.ps1` + port each helper to `.ps1` | High (full rewrite of 6 scripts + parity tests) | **Very high** — every installer change must land twice | Easy to ship a Windows path that silently diverges | **Rejected** |
| **B. WSL-only** | Document "install under WSL"; no native Windows | Low | Low | mcp-sv and native Claude Code on Windows are not WSL; largest-user-base goal fails | Stopgap only, not the target |
| **C. Python SSOT everywhere mechanical** | `install.py` + skill helpers as `.py`; thin OS launchers where useful | Medium (one rewrite per surface, not per OS) | **Low** — one implementation | Python already required; pathlib/shutil replace rsync/find/awk | **Locked** |
| **D. Node/npx package** | `npx @aki/akidevrule install` | Medium–high (new packaging surface) | Low if single TS/JS codebase | Adds Node as hard dep; overlaps poorly with current stack | Defer unless distribution becomes the bottleneck |
| **E. Phased delivery** | Installer (Batch 1) before skill helpers (Batch 2) | Medium, split across releases | Medium until Batch 2 lands | Windows users get rules+skills first; `/akiflow` mechanical gates lag briefly | **Locked sequencing** |

**Rejected naive path:** "translate every `.sh` to `.ps1`". That maximizes dual-maintenance cost and does not reduce complexity — PowerShell is not simpler for `scythe`'s awk logic or for settings JSON merges already written in Python.

---

## 4. Ecosystem research — what skill scripts actually use

Research date: 2026-08-10. Scope: Agent Skills open standard, Anthropic official skills, community collections, and how `SKILL.md` instructs agents to invoke bundled code.

### 4.1 What the standard allows

The Agent Skills format (`agentskills.io`, adopted by Claude Code, Antigravity/AGY, Codex, Cursor, Copilot, and others) defines a skill as:

```text
my-skill/
├── SKILL.md          # required
├── scripts/          # optional — executable code
├── references/       # optional — docs loaded on demand
└── assets/           # optional — templates, data
```

Official guidance on scripts:

- Scripts are **executed**, not loaded into context — only their stdout/stderr cost tokens.
- Allowed languages called out in docs and examples: **Python, Bash, JavaScript** (and "etc.").
- Invocation is documented inside `SKILL.md` as ordinary shell commands the agent runs, e.g.:
  - `python scripts/helper.py input.txt`
  - `python3 scripts/process.py --input results.json`
  - `uv run scripts/extract.py` (PEP 723 inline deps)
  - `bash scripts/validate.sh "$INPUT"`
- Relative paths are resolved from the **skill directory root**.
- Claude Code additionally supports `${CLAUDE_SKILL_DIR}` so the same instruction works for personal, project, and plugin install locations.

There is **no requirement** that scripts be bash. Bash is one option among several; the standard is language-agnostic at the folder level.

Sources: [agentskills.io — using scripts](https://agentskills.io/skill-creation/using-scripts), [Agent Skills SKILL.md overview](https://agentskills.io/skill.md), [Claude Code skills docs](https://code.claude.com/docs/en/skills) (bundle utility scripts; prefer run over read).

### 4.2 What Anthropic ships in practice

Public repo [anthropics/skills](https://github.com/anthropics/skills) (language breakdown observed 2026-08):

| Language | Share (approx.) |
|---|---|
| **Python** | **~85.6%** |
| HTML | ~11.4% |
| Shell | ~1.8% |
| JavaScript | ~1.2% |

Concrete patterns:

- `skill-creator/scripts/` is **all Python** (`package_skill.py`, `init_skill.py`, `quick_validate.py`, eval runners, …).
- Document/PDF/dataset-style skills ship **Python** helpers and tell the agent in `SKILL.md` to run them (`python scripts/...`) rather than reimplement logic in the model.
- Template text inside `init_skill.py` explicitly lists "Python scripts, shell scripts, or any executable code" — Python first in examples.

Conclusion: the reference implementation of the ecosystem treats **Python as the default language for real skill logic**.

### 4.3 Community and secondary sources

| Pattern | Observation |
|---|---|
| PEP 723 + `uv run` | Common for self-contained `.py` scripts with deps declared inline — no separate `requirements.txt` install step for the skill consumer |
| Bash wrappers | Still used for tiny glue or Unix-only ops; collections that care about cross-platform treat bash as non-SSOT |
| Quality bars | Some registries list "self-contained scripts (PEP 723)" as a quality signal |
| Progressive disclosure blogs / guides | Canonical example tree often shows `scripts/helper.py`, not only `.sh` |

Microsoft Agent Framework, various SKILL.md guides, and multi-agent skill SDKs all treat `scripts/` as "Python / Bash / JS" with Python dominant in non-trivial examples.

### 4.4 Implication for akidevrule

| Our script | Nature | Ecosystem fit if ported to Python |
|---|---|---|
| `council-open` / `read` / `verify` / `cost` | Deterministic FS + markdown parse + exit-code gates | Exact use case official docs give for bundled scripts |
| `scythe` | Mechanical lint; currently awk with known mawk pitfalls | Python `re` = one behavior on three OSes; matches "prefer tested code over regenerated logic" |

Porting skill helpers to Python is **aligned with the ecosystem**, not a private preference. Dual-maintaining `.sh` + `.ps1` would be the *unusual* choice relative to how serious skills are written in 2026.

### 4.5 How `SKILL.md` should call scripts after the port

Prefer explicit, portable invocation:

```bash
python scripts/council_verify.py "$SESSION_DIR"
# or, if the environment standardizes on python3:
python3 scripts/scythe.py --all .
```

Guidelines:

- Use **stdlib-only** Python for these helpers unless a dependency is unavoidable; if a dep is needed, consider PEP 723 rather than a global install requirement.
- Do **not** hard-code bashisms (`[[ ]]`, process substitution) in the skill body.
- Optionally keep thin `.sh` wrappers during transition so old prompts that call `scripts/council-open.sh` still work on Unix; Windows-facing skill text should name the `.py` entrypoint.
- Document the interpreter discovery convention once (`python3` on Unix, `py -3` / `python` on Windows) in the skill or in installer notes — same problem the thin install launchers already solve.

---

## 5. Recommended direction (locked)

### Principle

> **One implementation language for all mechanical work that must run on three OSes. Shell and PowerShell remain thin launchers only. Content stays agent-neutral markdown.**

Python is already on the critical install path. Official and community Agent Skills practice the same choice for bundled scripts. Unifying installer **and** skill helpers on Python minimizes languages, maximizes Windows reach, and matches how the ecosystem expects skills to ship code.

### Target shape after unification

```text
install.py                      ← SSOT installer (pathlib, shutil, json)
install.sh                      ← thin: exec python3 install.py "$@"
install.ps1                     ← thin: py -3 / python install.py @args

skills/akiflow/scripts/
  council_open.py               ← ported (SSOT)
  council_read.py
  council_verify.py
  council_cost.py
  scythe.py                     ← ported last (highest logic density)
  # optional transitional:
  # council-open.sh → exec python3 "$(dirname "$0")/council_open.py" "$@"

claude/hooks/
  aki-update-check.py           ← already OK; normalize paths
```

### What "support Windows" means (definition of done)

1. **Install:** one command installs payload → `%USERPROFILE%\.aki\akidevrule`, skills into each present CLI root, agents into `.claude\agents`, writes/merges settings, generates AG rules if `.gemini` present.
2. **Idempotent re-install:** second run updates without destroying user-owned agents/skills outside the Aki namespace (same guarantees as today's per-skill sync and per-file agent copy).
3. **Core load path:** Claude Code on Windows reads `@`-imported core rules (path format verified).
4. **Skill helpers:** `council_verify` and `scythe` run under Python on Windows with stable exit codes on a frozen fixture tree.
5. **mcp-sv coupling:** Windows mcp-sv users can force-load the same four core files from the installed SSOT path; trusted script dirs resolve under `.aki` / `.claude`.
6. **CI:** GitHub Actions matrix `ubuntu-latest`, `macos-latest`, `windows-latest` runs install into a temp home and asserts a file manifest; Batch 2 adds helper smoke tests.

Non-goals for v1 Windows:

- Perfect parity of ANSI colors in the installer banner
- Supporting Windows without Python
- Rewriting skill *content* for Windows-specific coding norms (separate rules conversation)
- Shipping dual PowerShell reimplementations of council/scythe

---

## 6. Hard technical deltas (Unix → Windows)

| Concern | Unix today | Windows requirement |
|---|---|---|
| Home dir | `$HOME` / `~` | `Path.home()` (handles USERPROFILE) |
| Path join | string `/` | `pathlib.Path` only — never hand-concatenate |
| Directory sync | `rsync -a --delete` | `shutil` copy + explicit delete of **managed names only** (preserve "never wipe user skills" invariant) |
| Backup prune | `find … \| sort \| head` | `pathlib` + sort by mtime; keep 2 newest |
| Line endings | LF | Write text with `newline="\n"` for markdown/JSON consumed by CLIs; do not introduce CRLF into rule files |
| Executable bit | `chmod` irrelevant for md | N/A |
| Shell features in helpers | process sub, `[[ ]]`, bash arrays | Eliminate by using Python |
| `scythe` awk dialect | mawk/gawk differences already bit once | Python `re` — one behavior everywhere |
| CLI presence detection | `[ -d "$DIR" ]` | `Path(dir).is_dir()`; skip missing CLIs silently (same as today) |
| One-line remote install | `curl … \| bash` | Prefer `git clone` + `py -3 install.py` (inspectable, matches repo philosophy); optional `irm` only if it stays inspectable |
| Skill script invocation | `bash scripts/foo.sh` | `python scripts/foo.py` (document interpreter discovery once) |

---

## 7. Coupling with aki-mcp-sv

mcp-sv already:

- Force-loads akidevrule **core** into the residual instruction prompt (see mcp-sv 1.3.0 changelog: residual-only prompt, section 5 akidevrule).
- Treats `~/.aki` (and related) as trusted script territory.
- Documents a Windows install note.

Implications for this plan:

1. **Install path stability is an API.** `%USERPROFILE%\.aki\akidevrule` must stay stable once published; mcp-sv and any prompt builder key off it.
2. **Version skew:** mcp-sv should detect missing/outdated SSOT and point at the install command (or embed a submodule/subtree policy — decide explicitly; do not silently ship prompts that name absent files).
3. **Trusted dirs on Windows:** path normalization (drive letters, case-insensitivity) must match how mcp-sv resolves allowlist dirs. Python helpers under `.aki` / skill `scripts/` become first-class trusted content once installed.
4. **Release sequencing:** prefer landing Windows-capable `install.py` in akidevrule **before** advertising "full Windows" in mcp-sv docs; otherwise the note stays a half-promise.

Open question for owner: is akidevrule consumed by mcp-sv as **git submodule / subtree**, **documented external install**, or **copied fragments**? That choice changes whether a Windows install bug is one repo or two.

---

## 8. Phased execution plan

### Batch 0 — Research locks (no user-visible change)

| Task | Output |
|---|---|
| Confirm Claude Code Windows paths (`CLAUDE.md`, `settings.json`, `skills/`, `agents/`, hooks) | short table here or `docs/research/windows-cli-paths.md` |
| Confirm Antigravity / Gemini Windows config root | same |
| Confirm Codex / Kiro / Grok skills roots on Windows | same |
| Decide mcp-sv consumption model (submodule vs external) | one paragraph decision |
| Add CI skeleton (matrix 3 OS, empty or minimal job) | `.github/workflows/install-smoke.yml` |

**Exit:** path map reviewed by owner; no more guessing `~` equivalents.

### Batch 1 — Python installer SSOT

| Task | Notes |
|---|---|
| Implement `install.py` mirroring current `install.sh` behavior | Feature parity checklist from README "What the installer does" steps 1–9 |
| Preserve invariants | per-skill sync without touching foreign skills; agents copied file-by-file; `CLAUDE.local.md` create-only; backup + prune 2 |
| Thin `install.sh` | `exec python3 "$REPO_ROOT/install.py" "$@"` |
| Add `install.ps1` | `py -3` / `python` discovery with clear error if missing |
| README Requirements table | Windows → ✅ with Python 3.x prerequisite |
| CHANGELOG + `docs/index.md` | mandatory companions per repo CLAUDE.md |

**Verification:** CI on `windows-latest` installs into a temporary `HOME`/`USERPROFILE` and checks for `index.md`, core RULE files, and at least one skill `SKILL.md` under the Claude skills path when that path is pre-created.

### Batch 2 — Skill runtime helpers to Python

Aligned with ecosystem practice (§4). Order by dependency and blast radius:

1. `council_open.py` + `council_verify.py` (closure gate is load-bearing for `/akiflow`)
2. `council_read.py`, `council_cost.py`
3. `scythe.py` last — port fixtures from the 2026-08 scythe CHANGELOG measurements; assert zero regressions on a frozen markdown set if available

Also:

- Update `skills/akiflow/SKILL.md` (and any agent briefs) to invoke `python scripts/…` instead of bash-only paths.
- Optional thin `.sh` wrappers calling the `.py` files for Unix back-compat during one release cycle; delete when nothing references them.
- Prefer stdlib-only; no new global pip dependency for these helpers unless justified.

**Verification:** same fixture session tree passes `council_verify` on all three OS CI images; `scythe` finding counts match pre-port baseline on a frozen file list (stderr kept; no silent mawk-style collapse).

### Batch 3 — Polish & docs

- Uninstall instructions for Windows
- `akihelp` live paths aware of OS
- mcp-sv docs: replace "Windows install note" with a verified procedure
- Optional one-line Windows install only if inspectable
- Move this plan to `docs/plan/done/` when Batches 1–2 have landed and been used in anger

---

## 9. Cost estimate (order-of-magnitude)

| Work | Effort (single maintainer familiar with repo) |
|---|---|
| Batch 0 path research + CI skeleton | 0.5–1 day |
| Batch 1 `install.py` parity + thin launchers + CI smoke | 2–4 days |
| Batch 2 helpers (except scythe) | 1–2 days |
| Batch 2 `scythe.py` + fixture parity | 1–2 days |
| Batch 3 docs / mcp-sv sync | 0.5–1 day |
| **Total** | **~5–10 days** concentrated work |

Compare to dual `.sh`/`.ps1` maintenance: similar initial cost, **then permanent 2× on every installer or detector change**. Python SSOT for both installer and skill scripts is cheaper within one release cycle if more than one non-trivial change is expected (it is).

---

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Owner cannot smoke-test Windows locally | CI `windows-latest` is the gate; recruit 1–2 Windows users from mcp-sv audience for a checklist |
| Claude Code Windows path differs from assumed | Batch 0 research; if `@` import fails with backslashes, normalize to forward slashes in written `CLAUDE.md` |
| `scythe` Python port changes findings | Freeze fixture file list; compare exit code + finding counts before/after; bias to silence on structural lines (existing policy) |
| Dual-run period confuses contributors | README states `install.py` and `scripts/*.py` are SSOT; shell/ps1 are launchers only |
| mcp-sv ships Windows claim before akidevrule is ready | Sequence releases; mcp-sv documents "rules optional until akidevrule ≥ version X" |
| Python missing on a Windows machine | Installer and skill docs print one clear message with install link; do not silently fall back to a half-broken ps1 reimplementation |
| Agents keep calling old `.sh` paths after port | Transitional wrappers + explicit SKILL.md edit in the same batch that lands the `.py` files |

---

## 11. Decision checklist

| Item | Status |
|---|---|
| Primary strategy: Python SSOT for **installer** | ✅ locked 2026-08-10 |
| Primary strategy: Python SSOT for **skill scripts** | ✅ locked 2026-08-10 (ecosystem research §4) |
| Reject dual `.sh`/`.ps1` as SSOT | ✅ locked |
| Phased sequencing (install → helpers → polish) | ✅ locked |
| mcp-sv consumption model (submodule / external / other) | ⏳ open |
| Minimum Windows bar for first public claim: install-only vs install+helpers | ⏳ open (recommend: claim install after Batch 1; claim full `/akiflow` mechanics after Batch 2) |
| CI `windows-latest` as merge gate for installer changes | ⏳ open (recommend: yes) |
| Remote install UX on Windows: clone+`py -3` only vs also `irm` | ⏳ open (recommend: clone first) |

---

## Close-out (2026-08-11, v2.0.0)

Executed as a mini akiflow `execute` run: lead (Claude) coordinating two external CLI hands — kiro-cli and agy on claude-sonnet-4-6 — doing the file labor, no in-harness Claude seats. `council_verify.py` PASS on all six checks. Batches 1–3 landed together: `install.py` (parity-verified, 203/203 identical files) + `install.ps1`/`install.sh` launchers, five helpers ported and each diffed against its bash original, CI install-smoke matrix, and doc sync. §11 mcp-sv coupling left open by owner decision; mcp-sv repo untouched.

Cost note: the bulk of spend was headless (agy/kiro) and is invisible to `council_cost.py`, which only sees Claude transcripts — a full token tally would undercount by construction, so it was not run.

## 12. How to resume

1. Read this plan for *what* and *why* (including §4 ecosystem evidence).
2. Complete Batch 0 path table before writing `install.py`.
3. Implement Batch 1 only after any remaining §11 open items the owner cares about are closed.
4. Every batch ends with install (and later helper) smoke on three OS in CI and companion doc updates (`README.md`, `CHANGELOG.md`, `docs/index.md`).

---

## Related

- README Requirements (Windows ❌ today)
- `install.sh` — current installer SSOT by historical accident
- `skills/akiflow/scripts/*.sh` — current helper SSOT; to become transitional or deleted after Batch 2
- `docs/ref/agent-skills-standard.md` — SKILL.md is shared Claude ↔ Antigravity; scripts folder is part of that neutral layout
- `docs/arch/rule-delivery-architecture.md` — delivery model to keep consistent
- aki-mcp-sv CHANGELOG 1.3.0 — residual prompt + Windows note + trusted dirs
- Prior plan style: `docs/plan/akiflow-reduction-agent-layer.md`
- External: [agentskills.io](https://agentskills.io), [anthropics/skills](https://github.com/anthropics/skills) (Python-majority scripts), Claude Code skills docs (run bundled scripts; don't load them into context)
