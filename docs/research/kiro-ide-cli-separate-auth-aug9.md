# Kiro IDE and Kiro CLI use separate auth stores on macOS

**Date:** 2026-08-09

## Question

Can Kiro IDE and Kiro CLI be logged into different accounts simultaneously on the same machine?

## Investigation

The question arose from an experiment: the owner logged into a different account on Kiro CLI while the current Kiro IDE session remained active, then checked whether the two clients shared a credential store.

Both the IDE and CLI write configuration under `~/.kiro/`. The `settings/cli.json` file contains only IDE preferences (not credentials). Session conversation files live under `~/.kiro/sessions/cli/` (CLI) and `~/.kiro/sessions/<hash>/` (IDE) — again separate, but these are session logs, not auth tokens.

The actual credentials were found in the macOS Keychain:

```
security dump-keychain | grep -E "svce|acct"
```

Output showed two distinct entries:

| Entry | Keychain service | Account field | Client |
|---|---|---|---|
| IDE | `Kiro Safe Storage` | `Kiro` | Kiro IDE (Electron safeStorage) |
| CLI | `kirocli:social:token` | (null) | Kiro CLI |

Both entries were created minutes apart during the experiment and neither overwrote the other. The IDE uses Electron's `safeStorage` API, which stores an encrypted blob under a fixed service name in the OS keychain. The CLI uses a separate keychain entry named `kirocli:social:token`. The two paths are independent at the OS level.

## Conclusion

**Yes — Kiro IDE and Kiro CLI can be logged into different accounts at the same time on the same machine.** They use separate macOS Keychain entries and do not share a session. Logging into a new account on the CLI does not affect the IDE session, and vice versa.

This was verified empirically on macOS (darwin, `~/.kiro/` config root) by inspecting the Keychain after a cross-account CLI login with the IDE session already active.

## What the official docs say

Kiro's authentication documentation lists the same providers for both clients (GitHub, Google, AWS Builder ID, IAM Identity Center, external IdP). The one asymmetry is that the CLI additionally supports API key auth (`KIRO_API_KEY`) for headless/CI use, which the IDE does not. The docs do not explicitly describe the credential isolation — this note records the empirical finding.

The `KIRO_HOME` environment variable, documented as a way to redirect the `~/.kiro/` config directory, is not needed for account isolation. The auth stores are already separate by design.

## Relevance

Useful to know when running automated CLI tasks (scripted agents, CI-style invocations) under a service account while keeping the IDE logged into a personal account on the same development machine.
