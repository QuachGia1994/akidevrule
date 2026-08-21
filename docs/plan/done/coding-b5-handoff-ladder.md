# Plan: `coding.B5` — stop manufacturing owner-run items

> Executed 2026-08-21, same day as the trigger. Evidence: `docs/research/handoff-vs-self-verification-aug21.md`. Trigger: owner rejection of this round's closing report — *"có những thứ không cần đùn đẩy cho tôi test máy này có agy mà? … tìm xem nó là rule nào, ghi ra mọi điều mọi khía cạnh có thể ghi để không tái diễn vụ này nữa"*.

## 1. Problem

The round's closing report ended in a five-row "owner-run" table. Re-climbing each row on the same machine settled three of them outright and reduced a fourth to a static reading, with no owner action and no new tooling — see the research doc for the per-row result. The hand-offs were not blocked work; they were unattempted work with a blocked label.

Why the existing rules did not catch it:
- `agent.A3` kill-tests govern **questions**. A row in an owner-run table is not phrased as a question, so it slipped the filter while costing the owner exactly what a question costs — a read plus an action.
- `coding.B3` governs **manual testing of a done-transition** ("do not park finished work as waiting-for-manual-test") and the **hand-off ledger's shape** (one batch, deduped by flow). Both assume the hand-off is legitimate and only regulate its packaging. Neither asks whether the item had to leave the agent at all.
- The gap is therefore not enforcement of an existing rule but a missing one: **who performs the check**, decided before **how the hand-off is packaged**.

Recurrence evidence: the owner reports re-stating this by hand in most sessions across projects, including in the prompt that triggered this plan. A rule the owner has to re-type per session is a rule that does not exist yet.

## 2. Steps

- [x] **S1** — `payload/RULE-coding.md` gains **B5 — Handing a check to the human is the last rung of a ladder, never the default**: a six-rung ladder (read the flow → search the local tree → search vendor docs/web → probe mechanically here → run the real thing reversibly → hand off), the residue rules (each survivor names the rung that failed and why; hand over a result to confirm, not a task to design; re-climb at closing time; default to the report), and the named forbidden rationalizations. Placed in group B after B4 so `B3` keeps owning *what counts as verification* while B5 owns *who performs it*.
- [x] **S2** — `payload/index.md`: `coding.B5` added to the **Interrupting the owner** cross-cutting lens row (root stays `agent.A3`), and the `coding` group line updated to "B Quality, changing code & who verifies".
- [x] **S3** — the three deferred rows from the same round re-climbed and closed with measurements rather than requests: permissions **V2** and the `--add-dir` boundary question by live probe, **V5** by static reading plus a local render simulation, **B7-on-Mac** by source authority. Recorded in the research doc and in each feature plan's own matrix.
- [x] **S4** — `CHANGELOG.md` `[Unreleased]` entry; `install.py` fix that S3's V5 reading exposed (Windows launcher tokens).
- [x] **S5** — installer run so the deployed corpus at `~/.aki/akidevrule` carries B5 (`coding.B3` external-action completeness: the rule is not live until the copy the harness reads contains it).

## 3. Non-goals

- No weakening of `B3`'s honesty floor. What genuinely cannot be settled here is still reported as unverified, never as "Done"; B5 targets the manufactured hand-off only.
- No mechanical detector. Whether a rung was actually climbed is a judgment about effort, not a pattern in the bytes — `scythe.py` stays out of it (`agent` §0: `[FLUFF]` is never claimed by a script, and this is the same class of judgment).
- No change to `agent.A3`. The kill-tests are correct for questions; B5 is the sibling rule for work items, and the lens row is what ties them together.
