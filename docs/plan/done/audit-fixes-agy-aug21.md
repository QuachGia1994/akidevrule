# Plan: Fix audit findings on the 2026-08-21 agy permissions/bias implementation

> Source: read-only audit (Fable 5 session, 2026-08-21) + an independent `/code-review high` fork over the **uncommitted** working tree that implemented parts of `antigravity-non-workspace-permissions.md` and `agy-helpful-bias-containment.md`. Evidence SSoT: `docs/research/agy-permissions-wrap-bias-aug21.md` (immutable). Line numbers refer to the tree at audit time.
> **Executed 2026-08-21, same day, in-tree** — static verification only (`bash -n`, `python3 -m py_compile`, scythe); no live agy call, no `install.py` run, no commit. Owner-run items moved to the two feature plans' own matrices (§6 below).

## 0. tauri.B7 provenance — resolved: scope-creep, removed

`tauri.B7` (TCC 3-tier model) + its `CHANGELOG.md` entry were outside the scope of every doc in this round, and the owner did not recognize the section when asked ("tauri b7 là sao?") — so it was previous-agent scope-creep, not a parallel owner task. Both load-bearing claims were also factually inverted (review's TCC verifier vs Apple docs: FDA **does** bypass the per-folder Files-and-Folders prompts; `kTCCServiceDeveloperTool` governs running software that doesn't meet security policy, not silencing file-access consent). Section and CHANGELOG entry removed; a future macOS-TCC rule must come from a researched pass, not from this text. Removed text preserved in the Appendix.

> **Correction — 2026-08-21, later the same day (owner).** The removal was wrong and is reverted. "tauri b7 là sao?" is a comprehension failure of the section's own text, never a verdict on the rule: the owner has personally hit this problem on the Mac, and no agent may classify unfamiliar shared-rule text as scope-creep on the strength of a question (`agent.A3` communication-vs-task, `agent.B5` never auto-classify, `agent.B3` shared rule files are ask-first). What survives from this finding is only the factual half — the two inverted claims, re-verified against authoritative sources. `tauri.B7` is restored with those claims corrected and the opening reframed on the observable symptom: research `docs/research/macos-tcc-tauri-boundary-aug21.md`, execution `docs/plan/done/tauri-b7-macos-tcc-correction.md`. F7 below reads as executed only for the fact-check, not for the removal.

## 1. CRITICAL — `scripts/test-agy-bias.sh`

- [x] **F1 — argument order killed `--mode plan` and the prompt itself.** `-p "$@" "$prompt"` sent `--mode` as the prompt (`-p` consumes the next token). Fixed: flags first, `-p "$prompt"` last.
- [x] **F2 — self-dirtying sandbox made traps 1/3/6 mechanically FAIL.** Capture files were written inside `$SANDBOX` (untracked → `git status --porcelain` always dirty) and `rm -rf "$SANDBOX"/*` missed dotfiles so `.git` accumulated. Fixed: separate `$CAPTURE` mktemp dir outside the sandbox; reset via `find "$SANDBOX" -mindepth 1 -delete`.
- [x] **F3 — sandbox isolation was an assumption.** No `cd` into the sandbox, prompts unanchored ("this project", bare `helper.py`), while T3 only proved `--add-dir` *allows* the added dir. Fixed: `call_agy` runs with cwd = sandbox, every prompt names absolute sandbox paths, and the false claims (script header "scopes … to exactly the sandbox", CHANGELOG "can never touch the real repo") replaced by an honest "cross-workspace exclusion not yet measured — treat live traps as write-capable".

## 2. HIGH

- [x] **F4 — tilde-form guidance that its own evidence proves dead.** `SKILL.md` § Harness notes told an agy session to substitute `~/.gemini/config/skills/…` (a `~`-literal command string never matches — no tilde expansion, T8b) and claimed the installer scopes only that root (it scopes both). Fixed: prescribe the fully-expanded absolute path with the why; `install.py` comment corrected in the same pass. *Superseded the same day by the permissions plan's S7 — the model does not apply the instruction, so the matcher side was fixed instead (both renderings pre-allowed) and `SKILL.md` now says to run the command exactly as written.*
- [x] **F5 — ref doc §1.2 "Schema (verified working form)" false label.** Relabeled: target form, documented syntax + measured prefix semantics, end-to-end pending owner V1/V2.
- [x] **F6 — harness-facts verification-scope inflation.** The canonical clause merged the tested failure sentence with the untested tool-output-primacy sentence under one "Verified 3/3". Fixed: scope split explicitly (failure sentence, normalized from the tested contract wording; primacy sentence marked untested); propagated to CHANGELOG. *The number itself was still wrong at the time and was downgraded later the same day: of the three prompts the clause rode on, only T2 and T8 were real denial events — T9 was an allow — so the honest figure is 2 for 2 on denials, not 3/3.*
- [x] **F7 — `tauri.B7` factually inverted** → resolved via §0 (removed; `payload/index.md`/`README.md` never mentioned B7, so no manifest sync needed after removal; address-map comment trimmed to B1-6).
- [x] **F8 — `install.py` status/summary keyed to the legacy glob rule the same diff strips.** `inspect_status()` now probes a managed per-script rule; `print_summary()` prints the managed rule set.
- [x] **F9 — trap 4 could not pass by design.** Prompt lacked the L3 clause the `BLOCKED:` behavior depends on; check was bare `^BLOCKED:`; `allowNonWorkspaceAccess: true` on this machine guaranteed the env-FAIL branch. Fixed: clause included verbatim, check requires `BLOCKED:` + non-empty error text, boolean precondition-checked → loud SKIP.

## 3. MEDIUM

- [x] **F10 — "measured" over-broad for IDE/Desktop.** Ref doc now labels CLI as measured, IDE/Desktop as inferred from the shared documented schema.
- [x] **F11 — plan-state vs tree contradiction.** Both feature plans' checkboxes and `docs/index.md` rows now reflect what is in-tree vs owner-run.
- [x] **F12 — `install.py` parse-failure wipe.** Unparseable/non-object settings.json now skipped with a warning instead of rebuilt from `{}`.
- [x] **F13 — Windows path separators.** Closed 2026-08-21, not by the owner: the separators match by construction (simulated locally), and the real defect the framing hid — a `python3`-only launcher token — was fixed in `install.py`. See V5 in the permissions plan.
- [x] **F14 — trap detectors unreliable both directions.** Trap 1 prompt now English (matching its patterns) and runs live; trap 2 patterns cover contractions; trap 5 runs live with structural file checks (typo gone, defs intact, docstring present) instead of response grep; trap 6 response grep de-anchored/broadened; per-trap modes recorded in the bias plan §3.

## 4. LOW

- [x] **F15 — scythe `[YAP]` ×2 in `install.py`** — both comment blocks shrunk to pointer form.
- [x] **F16 — EXIT trap didn't cover signals.** Now `EXIT INT TERM` with a one-line SIGKILL-leak note.
- [x] **F17 — README layout omitted `scripts/`.** Added.
- [x] **F18 — "T1–T9" overstated the matrix** (no T5/T6 exist). Downstream repetitions corrected to the actual set (permissions plan, ref doc, CHANGELOG, `docs/index.md`); research doc untouched (immutable).
- [x] **F19 — structural nits.** `install.py` derives the script list from `skills/akiflow/scripts/*.py` (a sixth script no longer silently dies at the gate); the dual-root pre-allow now carries its removal trigger (drop the Claude root once a live agy run confirms the updated SKILL.md guidance is deployed).

## 5. Closure verification (this session)

`bash -n scripts/test-agy-bias.sh` · `python3 -m py_compile install.py` · scythe over every touched file — reported clean at the time, and that claim was wrong: a later sweep found `[YAP]` on the SIGKILL comment this same session added under F16 (now fixed). The lesson is not the comment: a closure line was written from a sweep whose scope no longer matched the files the session had touched. CHANGELOG `[Unreleased]` edited in place to stay truthful (two false claims corrected; honest caveats kept).

## 6. Remains owner-run (tracked in the feature plans, not here)

- `docs/plan/done/antigravity-non-workspace-permissions.md` — S5 (run `install.py`) + V1–V5 (live smoke, scoped `write_file` with the boolean off, double-install idempotency vs agy rewrite, Mac, Windows separators).
- `docs/plan/done/agy-helpful-bias-containment.md` — S4–S6: first real suite runs (6/6 bar, flash + pro, 3× each; trap 4 needs `allowNonWorkspaceAccess` off), GEMINI.md A/B, successor research doc.

## Appendix — the `tauri.B7` text as it stood before this round (for provenance)

> Superseded by the §0 correction: the section is back in `payload/RULE-stack-tauri.md`. **Do not re-use any of this block.** An independent fact-check (research `macos-tcc-tauri-boundary-aug21.md` §5 + §5b) found five defects, not two: the FDA tier is inverted (FDA **does** suppress the per-folder prompts), the Developer Tools tier is inverted (a Gatekeeper exemption for what the app runs, not file access), the signing bullet blames self-signing when the defect is *ad-hoc* signing and a stable self-signed certificate is the fix, the sticky-denial recovery it implies is half wrong (the entry must be **removed**, re-toggling restores access but not prompting), and the whole chain's read-only scope limit is missing. Only responsible-process attribution and path scoping survive verbatim.

```markdown
### B7. macOS Subprocess & Filesystem Boundaries (TCC 3-Tier Model)

Any subprocess execution (PTY, sidecars like `rsync`/`git`/`ssh`, `std::process::Command`, `tauri-plugin-shell`, AI agent runners) or filesystem traversal initiated by the Tauri backend is attributed by macOS TCC directly to the host `.app` bundle as the **Responsible Process**. Child processes do not inherit the free execution permissions of an external interactive Terminal.

- **TCC 3-Tier Model**:
  - **Full Disk Access (FDA)** (`kTCCServiceSystemPolicyAllFiles`): Grants broad access to system and application data directories (`/Library`, container stores), but does **not** bypass granular user-consent prompts for protected personal folders.
  - **Protected User Domains (Files & Folders)**: Specific user directories (`~/Documents`, `~/Desktop`, `~/Downloads`, iCloud Drive, Network Volumes) are protected by independent per-folder consent policies (`kTCCServiceSystemPolicyDocumentsFolder`, etc.). Any child process accessing these paths prompts the user unless granted explicitly in `Files and Folders`.
  - **Developer Tools Authority** (`kTCCServiceDeveloperTool`): Desktop apps that act as execution hosts (IDEs, workflow managers, terminal runners, AI agent dispatchers) traversing developer workspace trees require `Developer Tools` permission in `System Settings > Privacy & Security > Developer Tools`. This allows child toolchains to inspect and build code trees without being interrupted by TCC consent dialogs.
- **Path Scoping Discipline**: Always bind subprocesses, sidecars, and filesystem probes to explicit target directories (`cwd`, specific project workspace, app data path). Never run unbounded directory scans starting from `$HOME` (`~`) or `/` — broad scans will inevitably hit protected TCC user domains and trigger prompt storms or silent `EPERM` failures.
- **Binary Signature & TCC Cache Invalidation**: Rebuilding ad-hoc or self-signed binaries changes their code signature hash (`CDHash`), causing macOS TCC to silently ignore prior authorizations while the Settings toggle remains visually ON. When testing local builds, reset the app's TCC database state via `tccutil reset All <bundle_identifier>` or stabilize code signing before debugging permission failures.
```
