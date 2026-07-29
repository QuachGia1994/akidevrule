# Research: Does Antigravity read Claude Code's skill directory natively?

**Start time:** 2026-07-29

**Initial purpose:** The owner ran a local experiment on this machine — deleted the old `akiclaudedoc`-era leftovers and the current akidevrule-managed skill/rule artifacts, then opened a fresh AG IDE session and a fresh `agy` CLI session. Both still surfaced Aki's skills, without anything being freshly synced into `~/.gemini/config/skills/`. That raised the hypothesis: **AG/AGY may now discover `~/.claude/skills/` natively**, which would make `install.sh`'s `sync_aki_skills "$GEMINI_SKILLS_DIR"` step (README installer step 7) redundant. Context: this repo's own `docs/research/antigravity-rule-discovery-architecture.md` (2026-07-23) already established `~/.gemini/config/skills/` as the confirmed universal auto-discovery root across all three AG surfaces, but never tested whether `~/.claude/skills/` is *also* read directly.

**Strategy:** Cross-reference the hypothesis against independent, dated sources rather than trust one experiment with an unclear baseline (the deleted state wasn't fully inventoried, so a stale `~/.gemini/config/skills/` copy or a workspace-level `.agents/skills/` could equally explain what was observed).

**Checklist:**
1. Fetched `https://antigravity.google/docs/skills` (official vendor doc) for the literal skill-discovery paths.
2. Searched for and fetched independent third-party confirmation of AG's skill format compatibility.
3. Fetched `https://atamel.dev/posts/2026/07-01_where_agy_agent_skills/` — a dedicated, recently published (2026-07-01) deep-dive by a Google Cloud Community writer (Mete Atamel) enumerating every path each of the three AG flavors (AGY, AGY CLI, AGY IDE) checks, in precedence order.
4. Compared both sources' path lists against `~/.claude/skills/`.

**Result:**
- Official doc (`antigravity.google/docs/skills`): discovery paths are `<workspace-root>/.agents/skills/<skill-folder>/` (workspace) and `~/.gemini/config/skills/<skill-folder>/` (global). No mention of `~/.claude/skills/`.
- Atamel's independent breakdown lists, in precedence order: `<workspace-root>/.agents/skills/<skill-folder>` (highest), then `~/.gemini/config/skills/<skill-folder>` (recognized by all three flavors), `~/.gemini/antigravity/skills/`, `~/.gemini/antigravity-cli/skills/`, `~/.gemini/skills/` (flavor-specific subsets), and the two builtin-skill roots. **No `~/.claude/skills/` path anywhere in the list.** The article's own explicit conclusion is to standardize on `~/.gemini/config/skills/` and ignore the others.
- **Verification:** two independent sources (vendor doc + a named third-party author with a directly relevant, recently dated post) agree on the same negative: neither lists `~/.claude/skills/` as a discovery root. This is stronger than the single local experiment, whose baseline state before deletion was not fully known (a pre-existing `~/.gemini/config/skills/` copy, or a workspace-local `.agents/skills/`, both fully explain "still worked" without requiring native Claude-directory discovery).
- **Corroborating links:** `https://antigravity.google/docs/skills`, `https://atamel.dev/posts/2026/07-01_where_agy_agent_skills/`, this repo's own `docs/research/antigravity-rule-discovery-architecture.md` §5.2 (established `~/.gemini/config/skills/` as the confirmed sync target, pre-dating this question).

**Decision:**
- **No action** on the hypothesis — it does not hold on current evidence. `install.sh`'s sync into `~/.gemini/config/skills/` (and the `~/.aki/akidevrule/agskills` + `skills.json` secondary path) stays required; it is not superseded by native discovery.
- **Cross-references:** `docs/research/antigravity-rule-discovery-architecture.md` (sibling finding on the same discovery mechanism, different question); `docs/ref/agent-skills-standard.md` (the shared-format fact this question sits next to — same file format, still a per-tool discovery path).
