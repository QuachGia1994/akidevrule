# Plan (executed) — akiflow: specialist board → agent council

**Status:** done · executed 2026-07-29 in a single pass, review-driven rather than plan-first (the plan was reconstructed from the review that drove it; recorded here to keep the `RULE-docs.md` B1 lifecycle honest).

**Supersedes in spirit:** [`akiflow-skill.md`](akiflow-skill.md) (original sized-pipeline design) and the board rewrite that followed it. Current-state design: [`../../arch/akiflow.md`](../../arch/akiflow.md).

## Trigger

A review of the board rewrite found six gaps, all in the same direction — the design named good mechanisms but never stated the goal they serve, so nothing in it could adjudicate a tradeoff:

1. No stated purpose. Every rule read as an independent constraint.
2. No stopping behaviour for a long room — only a per-pair round limit.
3. No session file contract (location, naming, turn format, retention).
4. No specialist-level anchor for its own mandate; the lead alone policed scope.
5. Harness claims with no sources, and no separation of documented from observed.
6. Cost reasoning stopped at "fork reuses the cache" — no TTL, no headless, no worktree, no "load nothing" case.

## Decisions taken

| # | Decision | Reason |
|---|---|---|
| 1 | **Purpose stated first** — decide as much as possible without the owner; escalate only what neither the room nor the lead can settle, and escalate it *as a decision*. | Rigour and offloading normally pull against each other; naming the goal is what lets a rule be judged as serving it or not. |
| 2 | Named **`agent-council`**, not `board`. | "Board" reads as a dashboard as easily as a governing body; "council" carries the deciding authority the purpose requires. |
| 3 | Workspace at `~/.aki/agent-council/<project>/<YYYY.MM.DD-HHMM>-<slug>/`, lead-chosen slug. | A council record has value for days, not minutes — it belongs in the Aki namespace, not `/tmp`. |
| 4 | **Retention as a script, not a rule** — `council-open.sh` prunes >30d on every run, matching Claude Code's own `projects/` window. | Leaving `/tmp` removed its free garbage collection; a rule someone must remember would not have replaced it. |
| 5 | **Three artifacts**: per-agent mandate file, `chat.md` room, lead-owned `checklist.md`. | A mandate stated once at spawn competes with everything arriving after; re-readable mandates are cheaper than the lead policing N agents. |
| 6 | Room read **in time order** — reversing the board design's by-item sharding — with fixed heading levels for grep and `council-read.sh` for slicing. | A meeting sharded by item is unreadable as a meeting. Context flooding is answered by selective *retrieval*, not by destroying the record's shape. |
| 7 | **Steering by judgment, not a round counter.** Four named drift/cost signals; minimum intervention is one pinned CHECKPOINT line. | A fixed limit would punish exactly the deliberation the skill exists to produce. |
| 8 | `references/harness-facts.md`, every entry tagged **[doc]** or **[obs]** with source links. | A future reader must be able to tell verified fact from working belief. Progressive disclosure keeps it free until read. |
| 9 | Cost realism: cache TTL expiry, headless (`claude -p`) escalation/permission failure modes, `isolation: "worktree"` for concurrent writers, and "load nothing" for self-contained questions. | "Always load the corpus" is the same error as "never load it". |

## Files touched

- `skills/akiflow/SKILL.md` — rewritten (runnable contract).
- `skills/akiflow/scripts/council-open.sh`, `scripts/council-read.sh` — new; first `scripts/` in this repo's skills.
- `skills/akiflow/references/harness-facts.md` — new.
- `docs/arch/akiflow.md` — purpose section, workspace, steering, cost, headless; failure modes 8–9.
- `README.md` (skill row, layout listing, uninstall), `docs/index.md`, `CHANGELOG.md`.
- Collateral from the same pass: `claude/CLAUDE.md` (stale `claudedoc` prose + missing top-level `skills/` in the edit-here list), `README.md` installer step (`scripts/` alongside `references/`).

## Verification

- Both scripts: `bash -n`, then a live run — session created and seeded, three turns appended, all six read modes correct, a back-dated session pruned and its empty project folder removed.
- `install.sh` re-run: `scripts/` and `references/` deployed to both `~/.claude/skills/akiflow/` and `~/.gemini/config/skills/akiflow/`, execute bits preserved, script runs from the deployed path.
- Skill frontmatter parsed; every internal `Step N` cross-reference checked against its heading.
- **Unverified:** no full `/akiflow` run has been executed end to end — the council protocol itself (roster convening, peer messaging, phase gate) is designed against documented and observed harness behaviour, not yet exercised in a real multi-agent run.
