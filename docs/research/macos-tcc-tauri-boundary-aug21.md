# Research: macOS TCC / Gatekeeper boundary for subprocesses spawned by a Tauri backend (2026-08-21)

## 1. Start time

2026-08-21, ~13:30 (Linux dev server, Claude Code Opus 5 session). Baseline: akidevrule 2.5.0@1d1691c, working tree carrying the uncommitted agy permissions/bias round.

## 2. Initial purpose

An earlier session removed `tauri.B7` ("macOS Subprocess & Filesystem Boundaries — TCC 3-Tier Model") from `payload/RULE-stack-tauri.md` on two grounds: it was outside the scope of every doc in that round, and the owner did not recognise it when asked. The owner overturned both grounds on 2026-08-21: the problem is real and personally experienced on the Mac, and "what is this?" is evidence that the *presentation* failed, never authorization to delete. The deletion was therefore an `agent.A3` misclassification (a question read as a decision) compounded by `agent.B3` (removing shared rule text without asking).

That leaves the one part of the original finding that still needs settling before the section can go back: are the section's load-bearing TCC claims true? This doc records that verification event. It does not re-open the removal decision — the owner already settled it.

## 3. Strategy

Primary/authoritative sources only, no reliance on this machine's local state (the owner's real Tauri work happens on the Mac; nothing here is representative). Three questions, each needing an exact-wording source: (Q1) does Full Disk Access supersede the per-folder Files & Folders consent, or sit beside it? (Q2) what does the Developer Tools pane actually authorize? (Q3) is the section's premise — child processes attributed to the host `.app` — correct?

## 4. Checklist

- [x] Q1 — FDA vs Files & Folders precedence: Apple PPPC deployment doc (service list) + The Eclectic Light Company's TCC decision-chain description
- [x] Q2 — `kTCCServiceDeveloperTool`: Apple Support "Control the ability of apps to run software that doesn't meet the system's security policy on Mac" + the pane's own on-screen wording
- [x] Q3 — responsible-process attribution and inheritance across `fork`/`posix_spawn`, including the `responsibility_spawnattrs_setdisclaim()` opt-out
- [x] Sticky-denial and `cdhash` invalidation behavior cross-checked before keeping those two bullets

## 5. Result

**Q1 — the original claim is inverted (CERTAIN).** B7 said FDA "does **not** bypass granular user-consent prompts for protected personal folders." The decision chain runs the other way: if the app at the head of the attribution chain holds Full Disk Access, listing and reading are granted outright; only when it does *not* is the location-specific Files & Folders setting consulted; only when neither exists is the user prompted. FDA is the superset, not a parallel tier. Apple's own description of `SystemPolicyAllFiles` ("access to data like Mail, Messages, Safari, Home, Time Machine backups…") describes its *extra* reach, not a carve-out from the user folders.

**Q2 — the original claim is inverted (CERTAIN).** B7 said Developer Tools lets child toolchains "inspect and build code trees without being interrupted by TCC consent dialogs." The pane's actual grant, in Apple's words, is the ability "to run software locally that does not meet the system's security policy" — a Gatekeeper/notarization exemption covering what the app *executes*, not what it *reads*. It silences no file-consent dialog. This is the standard misdiagnosis and worth keeping in the rule as an explicit negative, since the wrong switch is the one a developer reaches for first.

**Q3 — the premise is correct (CERTAIN).** TCC resolves a request against the *responsible process*, tracked in-kernel (`p_responsible_pid` / `p_responsible_uuid`) and inherited by children across `fork`/`posix_spawn`; a spawned process is judged by the app at the head of that chain unless it deliberately disclaims via `responsibility_spawnattrs_setdisclaim()`. So a sidecar that runs freely from the user's Terminal can be denied inside the `.app`, and the grant is charged to the bundle's identity. The two supporting bullets also hold: a "Don't Allow" is sticky (recorded as a denial, no re-prompt, cleared only by resetting the entry), and TCC keys authorizations to the binary's `cdhash`, so re-signing an ad-hoc local build silently voids them while the Settings toggle still displays ON.

**Verification labels.** Q1/Q2/Q3 — measured against published vendor/authoritative wording, not against a live Mac; no macOS host was available to this session (Linux dev server; Rust/Tauri builds are Mac-only per the machine rule). Nothing in the corrected text depends on a runtime observation this session could have made. Reopen trigger: an observed prompt on a protected folder from an app that already holds FDA, which would mean the chain has an exception this doc missed.

Sources: [Apple — PPPC payload service list](https://support.apple.com/guide/deployment/privacy-preferences-policy-control-payload-dep38df53c2a/web) · [Apple — run software that doesn't meet the system's security policy](https://support.apple.com/en-ca/guide/mac-help/mchlc5fb7f9c/mac) · [The Eclectic Light Company — Privacy: Files & Folders or Full Disk Access?](https://eclecticlight.co/2026/04/08/privacy-files-folders-or-full-disk-access/) · [Qt — The Curious Case of the Responsible Process](https://www.qt.io/blog/the-curious-case-of-the-responsible-process) · [HackTricks — macOS TCC](https://hacktricks.wiki/en/macos-hardening/macos-security-and-privilege-escalation/macos-security-protections/macos-tcc/index.html)

## 5b. Correction — same day, from an independent fact-check

An isolated agent re-verified all six claims of the drafted section against primary sources, forbidden from reading this doc. Three corrections, all now applied to `tauri.B7`; §5 above stands as written for Q1/Q2/Q3, which it confirmed.

- **The `cdhash` bullet was wrong in the direction that matters.** It blamed "ad-hoc/self-signed" builds jointly. Apple's TN3127 scopes the loss to *ad-hoc* signing (`codesign --sign -`, Xcode's Sign to Run Locally): the authorization is tied to that exact build, so each rebuild starts over. A **stable self-signed certificate is the documented remedy**, not a cause — the original wording sent the reader away from the one fix that works. The claim "the Settings toggle still displays ON" found no source at all and was dropped rather than kept as an unlabeled guess.
- **Sticky-denial recovery was half wrong.** Toggling an existing Files & Folders entry back on restores *access* but not *prompting*; only removing the entry (or `tccutil reset`) returns the app to first-run behavior.
- **The chain has a scope limit the draft never stated.** It governs consent-based listing and reading. Paths the user chooses in an Open/Save dialog or by drag-and-drop are granted by user intent and bypass it, and Apple's own log analysis excludes file *writes*. Without that sentence the section would misdiagnose a write-only or picker-driven sidecar.

Method note worth keeping: the fact-checker was told to treat this repo's docs as the thing under test and not as evidence, and it found a defect the authoring pass had missed — the value came from the isolation, not from the second opinion being better informed.

Added sources: [Apple TN3127 — Inside Code Signing: Requirements](https://developer.apple.com/documentation/technotes/tn3127-inside-code-signing-requirements) · [Apple — Controlling app access to files in macOS](https://support.apple.com/guide/security/controlling-app-access-to-files-secddd1d86a6/web) · [Eclectic Light — Privacy: how locations are protected](https://eclecticlight.co/2026/04/20/privacy-how-locations-are-protected/) · [Preserve macOS app permissions across rebuilds with self-signed certificates](https://evoleinik.com/posts/macos-dev-signing-preserve-permissions/)

## 6. Decision

- **Action →** `docs/plan/done/tauri-b7-macos-tcc-correction.md` (executed and closed the same day): restore B7 with Q1/Q2 corrected and the three switches named by what they actually control, keeping the verified premise, path-scoping and `cdhash` bullets.
- **Process finding, recorded because it caused the incident:** a rule section whose subject is unrecognisable to its own owner fails `agent.A4` (report for fast re-orientation) — the fix is a section title and opening line that name the symptom the reader would experience, not the subsystem's internal vocabulary. Deleting is never the remedy for that; the owner is the only party who can classify unfamiliar shared-rule text (`agent.B5` "never auto-classify ambiguous work").
- **Cross-references:** corrects `docs/plan/done/audit-fixes-agy-aug21.md` §0/F7 (decision overturned by the owner; that record gains a dated correction note rather than a rewrite) · `payload/RULE-stack-tauri.md` B7 · `payload/index.md` tauri row.
