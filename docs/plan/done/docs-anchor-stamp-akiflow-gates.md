# Plan (executed) — anchor stamp for SSoT docs, plus two akiflow gates

**Status:** done · executed 2026-08-12 · council session `2026.08.12-0640-drift-akiflow-gaps` (`~/.aki/agent-council/akidevrule/`, pruned after 30d — this file is the durable record per `docs.B1`).

**Mode:** `audit` for the drift sweep, `execute` for the rule and script changes. Roster: `judge-docs(sonnet)` · `judge-proportion(sonnet)` · `conduct(sonnet)` · `challenger(sonnet)` · `hands-mdsweep(haiku, ro:--tools Read,Grep,Glob)`.

## Trigger

Owner anchor, four asks: grep every `.md` for drift · state what anti-drift doctrine exists and add an `updated <time> <version>` stamp to the header of every `arch|biz|feat` doc · counter-critique three akiflow proposals raised by another agent, deliberating through `/akiflow` itself · check whether agent-behavior rules are force-loaded and whether `YAP|WRAP|redundant code` are adequately documented.

## Decisions taken

| # | Decision | Reason |
|---|---|---|
| 1 | New rule `docs.A4` — `> updated <YYYY-MM-DD> · v<version>` on the first line under the H1 of every `arch|biz|feat` doc, rewritten in the same edit as any content change | Those three folders hold current state and are the SSoT other docs and code are written against; a reader cannot separate a still-true doc from a silently rotted one without knowing when it was last confirmed |
| 2 | `plan|research|ref` carry no stamp | The first two are immutable event records already dated by their own schema (`docs.B1`, `docs.B2`); `ref/` is verified by running its commands, not by a date |
| 3 | `<version>` is the last **released** version from `CHANGELOG.md`, never an `[Unreleased]` buffer | `release.A` — a version exists only at the release event; a doc stamped with an unreleased number certifies against something that does not exist |
| 4 | Proposal 1 (lead writes a "REQ with no item" line, fed to the challenger, gate FAILs if absent) — **right diagnosis, wrong cure** → reshaped into a mechanical diff | The gap is real: `aki-challenger` only sees items the lead cut, so a requirement never turned into an item is outside every seat's reach. But the cure asks the party that made the omission to report it — the self-attestation `agent.B2` forbids — and an omission is unconscious by definition. Shipped as `council_verify.py` check 7: diff the ratified ledger against each item's `covers`, both artifacts the lead already wrote for other reasons |
| 5 | Proposal 2 (`council_open.py` refuses a room with no checklist) — **accepted, chokepoint moved** | The anchor must be pinned at open time (R1: the ledger quotes it), so the checklist cannot gate file creation. It gates **convening** — `council_open.py --convene <dir>` — which is where "N agents circling an uncut question" actually costs money |
| 6 | Proposal 3 (`outcome: held/reversed` field + ratio script) — **rejected** | Nothing triggers a return visit to the line when a decision is later reversed, so the field stays permanently `unknown` and the ratio becomes a confident number computed from data nobody maintains |
| 7 | No hook wiring for `scythe.py` | It already has a front door — the `akilint` skill, whose own text records that the exit code is left "usable from CI or hooks without parsing" deliberately. Runtime automation is a stated repo non-goal (`CLAUDE.md`) |
| 8 | No REQ-coverage prose mandate added to `aki-challenger.md` | Subtraction: the mechanical check supersedes it, and a prose duty that duplicates a gate is the weaker of the two copies (`pattern.A1`) |

## Defects found and fixed

| Where | Defect | Class |
|---|---|---|
| `skills/akiflow/SKILL.md` | Turn format demanded `CLAIM/EVIDENCE/ATTACK/OPEN` while the gate checks `FACT/CONSTRAINT/ASSUMPTION` — following the skill made the room fail the skill's own gate | Wrong |
| `docs/arch/akiflow.md` | Failure mode 12 required an `effort` parameter the same document records as nonexistent for in-session spawns | Wrong |
| `docs/arch/akiflow.md` | `council-verify.sh` cited after the rename to `council_verify.py` (2 sites) | Stale |
| `payload/index.md` | A "Red Team" seat named in the manifest that no longer exists in the roster | Stale |
| `README.md` | `scythe.sh` and a repo tree predating the `.py` rename | Stale |

## Verification

- `council_verify.py` over the live session: **7 PASS, exit 0**. Its first run FAILed on `REQ-4`, closed as *"satisfied by this run existing"* — the same self-attestation the check was built to catch. Re-cut as ITEM 6 whose closing criterion is the gate's own exit code, which the lead does not author.
- `council_open.py --convene` over the same session: `PASS convene: 5 item(s) fully specified`. Over a nonexistent dir: exit 1.
- Both scripts `python3 -m py_compile` clean.
- Two parser bugs caught by running against the real artifact rather than a fixture: only one of the two checklist forms (block vs one-line pipe) was recognised, and the heading `## REQ with no item` matched `item` as a substring, routing a deliberately-uncovered REQ into the covered set — a **false PASS**, the silent direction for a coverage check.

## Close-out

`council_cost.py` over the session transcript, reconciling the roster's declared `model` against actual spend:

| agent | model | turns | in | out | cache_w | cache_r |
|---|---|---|---|---|---|---|
| LEAD | `claude-opus-5` | 199 | 2,538 | 248,813 | 904,113 | 23,909,438 |

Two caveats on that table, both understatements rather than errors. Per-seat rows did not separate — the script labels a sidechain by akiflow's own `You are <NAME>` prompt opener, which is best-effort per name and collapsed to `LEAD` here, so seat-level attribution for this run is unavailable rather than zero. And the run predates the fix at Step 6 below: the first attempt to delegate the tally went to `aki-hands`, which holds no `Bash` and returned a refusal, so the lead ran the script itself — cheap here (the script aggregates in-shell and prints only this table) but the wrong default, now closed in the skill text.

Tokens only; dollar cost is `tokens × current per-model price`, billing `in + cache_w` as input and pricing `cache_r`/`out` separately (`release`-independent, prices drift).
