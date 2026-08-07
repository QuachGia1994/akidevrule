# Aki Method — Proportionality

<!-- Address map: proportion.A1-5 · proportion.B1-4 · proportion.C1-3 -->

**Tier: Analytical.** Stack-agnostic. Load whenever a guard, limit, quota, validation, permission check, rate limit, or any other defensive mechanism is proposed, sized, kept, or removed — and whenever a risk is about to be accepted.

This METHOD owns one question: **how big is the threat actually, and therefore how much defense does it earn?** It does not own the allocation of effort between the main work and its edges — that is `METHOD-deep-think.md` B5, which decides *when* a side-effect or edge-case is promoted above the MVP. This file decides *how much it is worth once promoted*. Apply both; duplicate neither.

The failure it exists to stop runs in two opposite directions that are the same error — severity asserted without anything counted. One direction builds server-side machinery against an attack nobody has a motive to run. The other ships a limit the browser enforces and calls it enforcement. Neither counted reach, capability, motive, or damage.

## A. Dimensioning — four measures before any verdict

Answer all four before proposing, keeping, or deleting a control. A few words each is enough; a measure left blank is itself the finding, because it is the one the argument is silently guessing.

### A1. Reach — how many can arrive at this state at all
Counted against the primary audience named in `docs/biz/` (`biz.A1`), never against an imagined internet. A state behind signup, a paid plan, and a specific navigation path has a different reach from one on the public homepage. State the population, not an adjective.

### A2. Capability — what it costs a person to get there
A ladder, and the rung matters more than the label: ordinary use of a visible control → deliberate misuse of a visible control → reading or replaying network requests → editing client state / scripting → chaining an exploit. Most consumer audiences thin out sharply after the second rung; a developer-tool audience does not thin out at all.

### A3. Motive — what they gain by doing it
Money, quota, rank, access, someone else's data, or nothing. Abuse that converts to money or to a scarce resource attracts scripted, repeated attempts; abuse that yields only a broken screen for the abuser attracts approximately no one. A control against a zero-motive path is decoration.

### A4. Blast radius — what breaks, and whether it comes back
Ordered: the actor's own data (recoverable) → other users' data → money or billing → an irreversible disclosure or deletion. Recoverability is the axis that matters, not the size of the mess.

### A5. Label every number measured or estimated
Logs, analytics, and a real user count are measurements. Everything else is an estimate and is written as one (`agent.B2` — verified facts separated from assumptions). An estimate is a legitimate input; an estimate wearing the clothes of a measurement is how a guess becomes doctrine.

## B. Verdict

### B1. Asymmetry — irreversibility outranks frequency
Low reach times low motive never licenses skipping a control whose blast radius is irreversible. A one-in-ten-thousand path that leaks other people's data or destroys unrecoverable state is protected on the strength of A4 alone, and the other three measures only decide *which* rung in B3 is used. This is the same shape as `think.A1`: a one-way door is sized by what it costs to be wrong, not by how often it opens.

### B2. The security floor is not sizeable
`coding.C4` (sanitize external input, never expose secrets, injection and XSS classes) and `biz.C3` (no dark patterns) are absolute floors. This METHOD sizes what sits **above** them and never argues below them. A dimensioning exercise that concludes "cheap enough to skip" on a floor item has been misused — the correct output there is which rung of B3 implements the floor, never whether to.

### B3. Cheapest sufficient control — take the lowest rung that covers the dimensioned threat
1. **Impossible by shape** — the state cannot be reached, so nothing needs checking (`design.A8`; the flow is reshaped, not guarded).
2. **Enforced once at the trust boundary that already exists** — the server handler, the DB constraint, the signed token. One place, not one place per caller.
3. **Detected and alerted** — the action succeeds, the anomaly is visible. Correct when the damage is recoverable and prevention would cost more than the cure.
4. **Accepted and recorded** — a legitimate outcome, but only as a written verdict per C1, never as silence.

**A client-side limit is UX, never enforcement.** Anything the browser computes, the browser can change: a quota, a price, a role, a rate limit, or a validity check that exists only in client code is a courtesy to honest users and nothing at all to anyone else. Ship it when it genuinely helps the honest majority — and never count it in the verdict as the control.

### B4. A guard that protects nothing is a cost, not free safety
`coding.C1` already forbids defensive guards for impossible internal states; this is that rule with the measurement attached. Dimensioning that returns reach 0 or blast radius nil means the guard should not exist: it carries maintenance cost forever, it survives refactors nobody re-examines, and it teaches the next reader that the state is reachable when it is not. Deleting such a guard still passes through `coding.B2` first — find out why it was added before removing it.

## C. Output & reuse

### C1. The verdict record
Four measures, each tagged measured or estimated · the chosen rung from B3 · and **the reopen trigger**: the observable change that would make this verdict wrong. A pricing change adds motive; a public launch multiplies reach; a new data class raises blast radius; a new audience shifts capability. Without the trigger, a deliberate "not now" becomes indistinguishable from an oversight the moment the session ends — the same reason `docs.B2` requires a "No action" decision to state its reason explicitly.

### C2. Where the record lives
A two-way door is recorded inline in the answer and nowhere else. A one-way door (`think.A1`), or any accepted risk that outlives the session, is recorded as a `docs/research/` doc on the `docs.B2` schema, with the reopen trigger in the Decision field.

### C3. Reuse as a council seat
In akiflow this METHOD is a standing domain consult named `risk-sizing`: any item whose closure adds, sizes, or removes a defensive mechanism closes only after a recorded turn from that seat. A file the room may consult is a file the room forgets; a seat with closure authority is what makes the lens actually run.

## One-line reminder

Count reach, capability, motive, and blast radius before deciding what a threat is worth — and never let "unlikely" answer "irreversible".
