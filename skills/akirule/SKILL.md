---
name: akirule
description: Aki's contextual rule router. Signal-triggered loading with high sensitivity for contextual and analytical rules; full load on explicit command. Core rules are not routed here — the harness embeds them via CLAUDE.md.
user-invocable: false
---

## What this skill does and does not guarantee

**Nothing in this file is guaranteed to run.** A skill loads only when the model chooses to invoke it, so every rule routed below is best-effort.

The rules that must apply unconditionally are not here. `index.md` and `RULE-agent-behavior.md` are embedded by the harness through `@` imports in `~/.claude/CLAUDE.md`, which is read mechanically at session start. Do not move them back into this file: an `@` path inside a skill body is not expanded by the harness the way it is inside `CLAUDE.md`, so declaring them here would look like an import while loading nothing.

## Addressing scheme (recall only — does not affect routing)

Every rule file is internally organized into groups `A`/`B`/`C` and numbered items `1`/`2`/`3…` (e.g. `coding.B2`, `stack.C1`). `topic` = filename minus its `RULE-`/`METHOD-` prefix. This is a naming convention for referring to a specific rule precisely — it has no effect on which files load or when; that is still governed entirely by the tiers below. Full map: `~/.aki/akidevrule/index.md`.

---

## Tier 1 — Contextual loading

**Sensitivity bias: when in doubt, load. A false positive (loading an unused file) costs a few tokens. A false negative (missing a rule) causes wrong behavior.**

Before responding, scan the user message and any file paths mentioned. For each rule below: if ANY single signal matches → Read that file immediately, before generating a response.

**A file extension alone is a sufficient signal.** Touching a `.md` loads `RULE-docs.md`; a `.vue`/`.css` loads `RULE-ui-pattern.md`; `.rs`/`Cargo.toml` loads `RULE-stack-tauri.md`; `.sql`/`migrations/` loads `RULE-db-design.md`. The project does **not** need a matching folder structure, a `docs/` tree, or an existing design system first — match on what is being touched, not on how mature the project is. The keyword and action lists below are additional entry points, never a required second condition.

### RULE-coding.md
**Default ON whenever the task touches code at all.** This file was previously force-loaded; treat a miss as a real failure, not a wasted read. Skip only when the task provably touches no source file (pure prose, pure discussion, pure config-free doc edit). Load if message or file path contains any of:
- **Keywords:** `code`, `function`, `class`, `bug`, `fix`, `error`, `exception`, `crash`, `refactor`, `implement`, `write`, `edit`, `test`, `verify`, `type`, `null`, `undefined`, `race`, `async`, `await`, `try/catch`, `validate`, `sanitize`, `secret`, `token`, `password`, `injection`, `encoding`, `UTF-8`, `unicode`, `performance`, `slow`, `leak`, `sửa`, `lỗi`, `viết hàm`, `kiểm thử`, `bảo mật`, `hiệu năng`
- **Paths:** any source file — `**/*.{ts,js,vue,rs,py,go,sh,sql,json,toml,yaml}`
- **Actions:** writing, editing, reviewing, debugging, or verifying any code; deciding whether something is safe to call done

### RULE-design-core.md
**Default ON together with RULE-coding whenever the task creates or changes any function, module, flow, or structure** — skip only for trivial value-level edits (a constant, a string, a config value). This file previously loaded only when a design keyword was named explicitly, which is exactly when structural work ran without the forest view and patched instead of reshaping (`design.A8`, `design.B2`). Additional signals — load if message or file path contains any of:
- **Keywords:** `design pattern`, `pattern design`, `nguyên tắc thiết kế`, `DRY`, `SOLID`, `SRP`, `OCP`, `single responsibility`, `single source of truth`, `SSoT`, `module`, `tách module`, `decomposition`, `phân rã`, `tái sử dụng`, `reuse`, `abstraction`, `trừu tượng hoá`, `pattern lặp`, `duplicate logic`, `rule of three`, `bounded context`, `clean code`
- **Context:** designing/splitting a module, extracting shared code, refactoring for reuse, hunting duplication, or any "how should this be structured" decision — any stack (backend, Tauri, CLI, library, DB, UI)

### RULE-docs.md
Load if message or file path contains any of:
- **Keywords:** `docs`, `CLAUDE.md`, `README`, `PLAN`, `plan/`, `diagram`, `mermaid`, `architecture`, `arch/`, `doc sync`, `documentation`, `index.md`, `feat/`, `plan lifecycle`, `tài liệu`, `sơ đồ`, `kiến trúc`
- **Keywords (drift audit):** `drift`, `audit docs`, `stale docs`, `outdated docs`, `out of date`, `docs khớp code`, `còn khớp`, `lệch`, `lỗi thời`, `rà soát tài liệu`, `docs cũ`, `kiểm tra tài liệu`
- **Paths:** **any `.md` file, anywhere** — writing or editing Markdown *is* a docs task; do not wait for a `docs/` folder to exist. Also `docs/**`, `PLAN.md`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `*.mdx`, `SKILL.md`
- **Actions:** creating, editing, moving, or completing any plan or doc file; checking whether docs still match the code after the fact (`docs.C`)

### RULE-content-write.md
Load if message or file path contains any of:
- **Keywords:** `button`, `label`, `heading`, `error message`, `tooltip`, `empty state`, `i18n`, `locale`, `translation`, `t(`, `$t(`, `meta title`, `meta description`, `og:`, `JSON-LD`, `FAQ`, `landing page`, `copy`, `UI text`, `nội dung`, `văn bản`, `nhãn`, `thông báo lỗi`, `semantic`
- **Paths:** `locales/**`, `i18n/**`, `*.i18n.*`, `public/content/**`; any file where a string a user will read is being added or renamed
- **Actions:** renaming a concept or term used across the product

### RULE-stack-akiNuxtCf.md
**Default ON for any Aki project context.** Skip only when the task is provably stack-independent (plain markdown, isolated script, config unrelated to the Aki frontend stack). Load if message or file path contains any of:
- **Keywords:** `nuxt`, `vue`, `cloudflare`, `workers`, `pages`, `wrangler`, `tailwind`, `composable`, `middleware`, `layout`, `plugin`, `component`, `useRoute`, `useFetch`, `definePageMeta`, `nitro`, `vite`, `breadcrumb`, `scroll-to-top`, `back-to-home`, `layout chrome`, `useBreadcrumb`
- **Paths:** `components/**`, `pages/**`, `composables/**`, `layouts/**`, `middleware/**`, `wrangler.toml`, `nuxt.config.*`, `tailwind.config.*`, `app.vue`

### RULE-ui-pattern.md
Load if message or file path contains any of:
- **Keywords (enforcement):** `component`, `vue`, `nuxt`, `tailwind`, `css`, `class`, `style`, `design token`, `token`, `variant`, `design system`, `atomic design`, `pattern class`, `@apply`, `@layer`, `BaseButton`, `c-btn`, `c-card`
- **Keywords (audit):** `dọn dẹp`, `class trùng`, `duplicate class`, `duplicate CSS`, `trùng lặp`, `audit CSS`, `refactor CSS`, `refactor UI`, `arbitrary value`, `quét class`, `w-[`, `text-[`
- **Paths:** any `.vue`, `.css`, `.scss`, or `.tsx`; `components/**`, `assets/css/**`, `tailwind.config.*`
- **Actions:** writing/refactoring any component or style; auditing a frontend codebase for DRY/SOLID violations

### RULE-seo.md
Load if message or file path contains any of:
- **Keywords:** `seo`, `schema`, `sitemap`, `robots`, `canonical`, `usePageSeo`, `useSchemaOrg`, `JSON-LD`, `structured data`, `og:`, `ogImage`, `hreflang`, `alternateName`, `sameAs`, `knowsAbout`, `LLM visibility`, `AI visibility`, `AI Overview`, `entity`, `schema.org`, `DefinedTerm`, `validate-seo`, `meta title`, `meta description`, `OG image`, `trailing slash`
- **Paths:** `docs/seo/**`, `docs/ref/seo*`, `scripts/validate-seo*`, `composables/usePageSeo*`, `composables/useSeoSchemas*`
- **Actions:** creating a new page, adding schema, configuring sitemap or robots

### RULE-release.md
Load if message or file path contains any of:
- **Keywords:** `release`, `release note`, `release notes`, `changelog`, `CHANGELOG`, `version`, `versioning`, `semver`, `bump`, `bump version`, `major.minor.patch`, `releases.json`, `phát hành`, `phiên bản`, `cập nhật phiên bản`, `nâng version`
- **Paths:** `CHANGELOG.md`, `app/data/releases.json`, `pages/releases/**`
- **Keywords (pre-ship gate):** `chưa push`, `trước khi push`, `trước khi deploy`, `sắp release`, `chuẩn bị ship`, `pre-release`, `ready to ship`, `xong chưa`, `đã xong hết chưa`
- **Keywords (commit/push/deploy — load even without an explicit "release" word):** `commit`, `git commit`, `push`, `git push`, `deploy`, `deployment`, `git tag`, `ship it`, `commit và push`, `push lên`, `đẩy lên`, `triển khai`
- **Actions:** committing or pushing code, deploying, shipping a change that should be recorded for users or maintainers; bumping a version; checking whether finished-but-unpushed work is actually shippable (`release.B7`)

### RULE-stack-tauri.md
**Default ON for any Tauri project context.** Skip only when the task is provably unrelated to the Tauri/Rust backend (pure frontend copy change with no `src-tauri` involvement, isolated doc edit). Load if message or file path contains any of:
- **Keywords:** `tauri`, `#[tauri::command]`, `invoke(`, `spawn_blocking`, `async_runtime`, `Cargo.toml`, `tauri.conf.json`, `capabilities`, `IPC`, `blocking UI`, `freeze`, `treo app`, `đứng app`, `block UI`
- **Paths:** any `.rs`; `src-tauri/**`, `tauri.conf.json`, `Cargo.toml`, `capabilities/*.json`
- **Actions:** adding/editing any `#[tauri::command]`, touching window/IPC code, bumping app version, diagnosing an app freeze/hang

### RULE-db-design.md
Load if message or file path contains any of:
- **Keywords:** `schema`, `migration`, `D1`, `SQL`, `database design`, `ERD`, `refactor DB`, `event sourcing`, `bounded context`, `normalization`, `1NF`, `table design`, `thiết kế db`, `thiết kế database`, `migration DB`
- **Paths:** any `.sql`; `migrations/**`, `schema.sql`, `**/d1/**`
- **Actions:** designing a new table/schema, writing a DB migration, refactoring how data is stored

### METHOD-flow-audit.md
Load if message contains any of:
- **Keywords:** `refactor`, `restructure`, `simplify`, `fragile`, `complicated`, `flow`, `state machine`, `async chain`, `tại sao phức tạp`, `luồng`, `tracing`, `cause and effect`, `over-guarded`, `conditional`, `timing`, `tái cấu trúc`, `đơn giản hóa`
- **Context:** fixing a bug spanning multiple files, tracing cause and effect across a chain

### RULE-biz.md
Load if message or file path contains any of:
- **Keywords:** `pricing`, `price`, `monetization`, `monetize`, `positioning`, `USP`, `target audience`, `customer`, `market`, `marketing`, `conversion`, `landing page`, `business model`, `revenue`, `tier`, `plan`, `subscription`, `giá`, `định giá`, `kiếm tiền`, `khách hàng`, `thị trường`, `đối tượng`, `chuyển đổi`, `mô hình kinh doanh`, `doanh thu`, `gói`, `định vị`
- **Paths:** `docs/biz/**`
- **Context:** any market-facing decision — evaluating an idea's commercial shape, writing/reviewing landing or sales copy, creating or editing `docs/biz/`, deciding what to charge or who the product is for

### METHOD-ux-psych.md
Load if message contains any of:
- **Keywords:** `UX`, `user experience`, `usability`, `user behavior`, `user psychology`, `onboarding`, `user flow`, `friction`, `cognitive load`, `empty state`, `first run`, `dead end`, `dark pattern`, `trải nghiệm người dùng`, `tâm lý người dùng`, `hành vi người dùng`, `khó dùng`, `rối`, `luồng người dùng`, `đánh giá giao diện`, `review UI`, `review UX`
- **Context:** evaluating an interface or flow through user behavior (not just visual styling — that is `RULE-ui-pattern.md`), designing an onboarding/conversion flow, diagnosing "why don't users do X"

### METHOD-deep-think.md
Load if message contains any of:
- **Keywords:** `new feature`, `tính năng mới`, `should we`, `có nên`, `simplest way`, `đơn giản nhất`, `is this worth`, `có đáng`, `tradeoff`, `scope`, `effort`, `value`, `premature`, `complexity`, `abstraction`, `tooling`, `first principles`, `tư duy nguyên bản`, `phản biện`, `mục tiêu tối thượng`, `one-way door`, `quyết định lớn`, `decision record`, `pre-mortem`, `evaluate`, `assess`, `review the approach`, `worth refactoring`, `good idea`, `side effect`, `edge case`, `đánh giá`, `bàn luận`, `nên refactor`, `đánh giá ý tưởng`, `đánh giá chiến lược`, `tác dụng phụ`, `trường hợp biên`
- **Context:** architectural or tooling decision, scope or effort/value discussion, a big or hard-to-reverse decision, a request for first-principles/critique-style thinking, or *discussing/evaluating* (rather than just executing) a refactor, a code review, a strategy/plan, or an idea — the four cases that trigger Module 5 (MVP focus, side-effects/edge-cases weighed by severity)

---

## Tier 2 — Full load

**Trigger** — match any of the following (case-insensitive): `nạp full`, `load full`, `full load`, `nạp tất cả rule`, `load all rules`, `full akirule`, `nạp hết rule`

**Protocol — execute in order:**
1. Run `ls ~/.aki/akidevrule/RULE-*.md ~/.aki/akidevrule/METHOD-*.md` to discover the actual file list
2. Read each file returned (skip anything under `ref-ECC/`)
3. Output confirmation: `[akirule:full] Loaded: <comma-separated filenames>`

---

## Load confirmation

After any loading, output one line at the start of the response:
- Tier 1: `[akirule] +RULE-coding.md +RULE-docs.md` (list files actually loaded this turn)
- Tier 2: `[akirule:full] Loaded: <all filenames>`
- Nothing loaded: no output needed
