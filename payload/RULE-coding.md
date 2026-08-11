# Core Coding Rules

<!-- Address map: coding.A1-3 · coding.B1-4 · coding.C1-5 -->

## A. Philosophy & source of truth

### A1. Language
- Code and comments: English only
- Commit messages: English, imperative style

### A2. Philosophy
- Single-maintainer friendly — about who maintains, not how many use; never an excuse to cut UX
- MVP-first
- DRY, but no abstraction for its own sake
- YAGNI
- Default to simple, direct solutions

### A3. Source of truth
Priority order:
1. Local source code, type definitions, runtime output, and build output
2. Official documentation
3. Live observed results

Project docs and memory are useful context, not final truth.

## B. Quality & changing code

### B1. Code quality
- Naming: `pattern.A7` is the root rule — not restated here
- Prefer one clear responsibility per function/module
- Modularize only when it improves clarity, reuse, or testability
- Prefer existing code and patterns over re-implementation

### B2. Changing existing code
A principle with the procedure that guarantees it — apply to any edit of code you did not just write:
- **Before:** grasp the flow and intent of the code before you change it — read the docs it references first (code often points to `docs/...`), then the code, and the git history only when the logic is complex or has been reworked many times (Chesterton's Fence: know why a piece is there before you remove it).
- **After:** confirm the intents and flows you did NOT set out to touch still hold — a fix scoped to problem X must not silently break an unrelated property Y.

### B3. Verification
- Done means verified — never claim success from intention alone.
- Verify by the **narrowest tool that actually settles the doubt**: static reading and type/lint/unit checks first. Never spin up a full build or dev server just to catch a typo a typecheck would catch.
- **Static reading IS verification** when the property is fully determined by visible code flow — state what was read as the evidence and close the checklist item on that evidence. Escalate a tier (typecheck → unit → runtime) only when you can name the specific doubt that tier settles.
- **Never gate a done-transition on human manual testing for a check that static reading or an automated tier settles.** A plan's verify checklist stays fully detailed — the violation is not the checklist, it is parking finished work as "waiting for manual test" on items whose truth the code flow already proves. Hand the human only what genuinely needs human runtime judgment: UX feel, visual rendering, live external integration.
- **Running the app is not a default verification step — but not running it does not let you claim "Done".** Starting a dev server, making live network calls, or driving a full build/headless screenshot is **user-triggered**, not self-authorized (cost and side effects are the user's call). When a change's real risk lives **only at runtime** — hydration, layout/z-index, route/auth flow, a dynamically-built class a build step may purge — and you cannot settle it statically, you may **not** report "Done": halt and report the state as **"unverified — needs a runtime check"**, propose the exact command, and hand it to the user (see [[RULE-agent-behavior]] A3). "Done" for logic you only compiled is not done.
- **A change that requires a separate action against an external system to take effect is not done when the file describing that action is written.** Migrations, remote config, env vars, cache purges, cron/schedule registration — writing the script/config is not the same event as the target system actually reflecting it. Git diff and a green build both stay silent about this gap: neither touches the external system, so both can look complete while the real target (a remote database, a dashboard toggle, a deployed cron) is still on the old state. Verify the action was actually executed **against the real target**, not just that the instructions to perform it exist locally, before reporting "Done" on that change. Domain instantiation: [[RULE-release]] (a release/CHANGELOG entry is not truthful until this holds) and stack-specific execution commands (e.g. `RULE-stack-akiNuxtCf.md` §C8 for D1 migrations).

### B4. Self-documenting code — comments are a last resort
Domain application of the density root (`agent.A4` — every line must carry information the reader does not already have); the naming root is `pattern.A7`. Penalty card: `[YAP]` (`agent` §0).
- Naming and shape come first: a comment that explains *what* a block does is a failed name or a failed extraction — fix the name/structure (`pattern.A7`, `pattern.A3`), then delete the comment. Clean flow plus role-named functions and variables need no narration.
- A comment may state only what the code cannot say: a non-obvious constraint, an external contract, a genuine why. Never narrate the next line, restate the signature, or record change history.
- Deletion test, per comment: if removing it loses nothing a reader needs beyond what the code already says, remove it. Default is silence — comment density is a smell, not a virtue.
- Comments rot: no compiler checks a comment, so it drifts silently as the code under it changes, and a stale comment misleads worse than none — one more reason deletion is the default, and why a rationale that must stay current lives in a doc the code references ([[RULE-docs]] B3), never duplicated inline.
- One line when a comment is genuinely needed; a rationale bigger than that lives in docs, with the comment holding only the reference (see [[RULE-docs]] B3).

## C. Runtime safety

### C1. Error handling
- Validate at system boundaries: user input, external APIs, filesystem, network, persistence
- Do not add defensive guards for impossible internal states — and size the ones that do guard a reachable state against who can actually reach it (`METHOD-proportionality.md`), instead of adding protection by reflex
- Fail loudly in development when it helps reveal broken assumptions
- Keep production failures safe and user-appropriate
- **Never fabricate mock/fixture data as a runtime fallback for a missing dependency** (DB, API, service binding). Throw/return a real error instead. If a local dev environment genuinely lacks that dependency, fix the environment itself (real local instance, proper binding/proxy) — don't paper over it with fake data. Verify the dependency is actually unavailable by reading how the runtime/framework wires it in dev before assuming a fallback is needed at all.

### C2. Result pattern for external calls
When calling external APIs, Firebase, or any fallible I/O at a system boundary, return a Result type instead of throwing:

```ts
type Result<T> = { ok: true; data: T } | { ok: false; error: string }
```

- The function that owns the boundary (composable, service module) does the try/catch once and returns Result
- Callers check `.ok` before using `.data` — no try/catch spread across UI or business logic
- TypeScript narrows the type correctly after the `.ok` check — no `data!` assertions needed
- For batch calls: each item returns its own Result; one failure does not crash the batch

```ts
// ✅ boundary function — catches once
async function fetchUser(uid: string): Promise<Result<User>> {
  try {
    const doc = await getDoc(ref('users', uid))
    return { ok: true, data: doc.data() as User }
  } catch (e: any) {
    return { ok: false, error: e.code ?? 'unknown' }
  }
}

// ✅ caller — no try/catch needed
const result = await fetchUser(uid)
if (!result.ok) return showError(result.error)
doSomethingWith(result.data) // TypeScript knows this is User
```

### C3. Performance
- Minimize query/call count and CPU cost **incrementally, everywhere** — not just identified hot paths
- Prefer flat, non-correlated queries over nested CTEs or per-row correlated subqueries; push merge/aggregation logic to plain application code when data volume makes that cheap and clearer
- Before shipping a nested/correlated query, ask: could two flat queries + an application-layer merge replace this more simply and just as fast?

### C4. Security
- Sanitize external input
- Never expose secrets in client code
- Avoid command injection, XSS, SQL injection, unsafe redirects, and token leakage
- Treat generated files, external data, and user-provided content as untrusted until validated

### C5. Unicode / UTF-8 safety
A string and its byte representation are different things; nearly every Unicode bug comes from conflating them. Applies to every runtime, and bites hardest where there is no Node `Buffer` to hide it (e.g. Cloudflare Workers).
- **base64 / JWT / cookie payloads:** `atob()`/`btoa()` are Latin1-only, not UTF-8 codecs — `JSON.parse(atob(jwt))` silently mojibakes non-ASCII text (accented names, emoji) and `btoa()` throws on codepoints > U+00FF. Decode via `new TextDecoder().decode(bytes)`, encode via `new TextEncoder().encode(str)` before base64.
- **Compare / store / dedupe / keys:** normalize first with `str.normalize('NFC')`. The same visible text (e.g. "Nguyễn") can be two different byte sequences, so an un-normalized equality check, unique key, or dedupe treats identical-looking values as different.
- **Length limits & sizes:** measure bytes, not `str.length` (which counts UTF-16 units) — use `new TextEncoder().encode(str).length` for body size, storage/field limits, and `Content-Length`.
- **Truncating text:** never slice by index into the middle of a character — `slice`/`substring` split accented characters and emoji into `�`. Iterate codepoints (`[...str]`) when cutting previews or slugs.
