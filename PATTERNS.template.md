# PATTERNS.md — Project Patterns (TEMPLATE)

This is a **template**. Copy it into a new project as `PATTERNS.md` and fill in the sections as real patterns emerge in the codebase.

`CLAUDE.base.md` and `CLAUDE.stack.md` tell the agent the rules. `PATTERNS.md` tells the agent the **examples** — canonical "this is how we do X in this project" references.

Don't fill this file in up-front. Grow it as you go. Each time a non-obvious choice is made, write it down here so it's not re-derived next time.

Delete this instructions block once the file has real content.

---

## How to use this file

- **Agent:** before making an architectural choice, skim this file. If a relevant pattern exists, follow it and point the developer to the section. If one doesn't exist, ask — and propose adding the decision here.
- **Developer:** when a new pattern emerges, add a section. Short. Copy-pasteable example. One reason per section.

Each pattern section follows this shape:

```
### [Pattern name]

**What it is:** [one paragraph]
**When to use it:** [bullets]
**When NOT to use it:** [bullets]
**Example:** [minimal, copy-pasteable code]
**Why this pattern:** [what it prevents or enables]
```

---

## 1. Runtime validation at boundaries

*Fill in when you pick your validation library (Zod, Pydantic, serde, etc.). This is one of the first patterns to establish.*

**What it is:**
[Describe your library and the trust-boundary concept: data from network, forms, env vars, storage, files gets validated before use.]

**When to use it:**
- [e.g. API responses]
- [e.g. form submissions]
- [e.g. env var parsing on startup]

**When NOT to use it:**
- [internal function args — types already cover those]

**Example:**
```
[minimal schema + parse example in your language]
```

**Why this pattern:**
[Types vanish at runtime. Validation at the boundary turns "mystery bug in production" into "caught at the edge with a clear error."]

---

## 2. Data fetching

*Fill in once your approach is settled.*

**What it is:** [server-side / client-side / hybrid approach]
**When server:** [e.g. initial page loads, SEO-critical data]
**When client:** [e.g. user-driven refetches, optimistic updates]
**Example:**
```
[minimal data-fetch in your stack]
```
**Why:** [what other approaches trade off]

---

## 3. Error handling

**Three layers:**
1. **Framework layer** — [e.g. `error.tsx` boundaries, exception middleware, panic recovery]
2. **Feature layer** — [try/catch around fallible operations with context-rich logs]
3. **Input layer** — [validation errors surfaced to the user]

**Never:**
- Swallow errors silently (`catch {}` / bare `except:` / unchecked `Result`)
- Show raw error messages to users
- Throw / raise strings or plain values instead of proper error types

**Always:**
- Log enough context to debug (what you were trying, with which inputs)
- Distinguish expected failures (bad input) from unexpected ones (system broken) — UX should differ

---

## 4. File structure

*Fill in when you settle on a layout.*

```
[paste your actual directory tree with one-line comments]
```

**Rules:**
- [e.g. co-locate feature components under `features/<name>/`]
- [e.g. extract to `lib/` only when used in 3+ places]
- [e.g. routes stay lean — they orchestrate, real logic lives in modules]

---

## 5. Accessibility defaults

*Skip if not applicable. Fill in for UI projects.*

- [Semantic markup over divs]
- [Accessible names for interactive elements]
- [Visible focus indicators]
- [Keyboard navigation works]
- [Color is not the only signal]
- [Images have alt text; decorative images get `alt=""`]

---

## 6. Performance defaults

*What's worth doing up-front, what's not.*

**Free wins (always do):**
- [e.g. use the framework's image component]
- [e.g. lazy-load heavy components below the fold]
- [e.g. stream slow sections with Suspense / equivalent]

**Not worth doing up-front:**
- [e.g. `useMemo` / `useCallback` without a measured problem]
- [e.g. micro-optimizations on small lists]

---

## 7. Testing

*Fill in once you start writing tests.*

**What we test:** [e.g. pure logic always, integration on critical flows, UI only where it's brittle]
**What we don't test:** [e.g. framework internals, third-party lib behavior]
**Tools:** [test runner, assertion library, mocking approach]
**Example:**
```
[a canonical test from this project]
```

---

## 8. Adding a new pattern

When a decision comes up that this file doesn't cover, and you make a choice — write it here. Short. One section. Format above (§ "How to use this file").

Future-you (and future-agent) will thank you.
