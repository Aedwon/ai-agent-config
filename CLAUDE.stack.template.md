# CLAUDE.stack.md — Stack Overlay (TEMPLATE)

This is a **template**. Copy it into a new project as `CLAUDE.stack.md` and fill in the bracketed sections. It adds stack-specific rules on top of `CLAUDE.base.md`.

Delete this instructions block once you've filled the file in.

---

## Stack (the non-negotiables)

Fill in what applies. Delete rows that don't.

- **Runtime / platform:** [e.g. Next.js (latest) / Expo SDK 52 / Node 20 / Python 3.12 / Go 1.22]
- **Language + strictness:** [e.g. TypeScript with `strict: true` — no `any`, no `@ts-ignore` without justification in a comment]
- **Framework conventions:** [e.g. Next.js App Router only / FastAPI with dependency injection / etc.]
- **UI / component system:** [e.g. React + shadcn/ui / React Native + NativeWind / SwiftUI / n/a]
- **Styling:** [e.g. Tailwind CSS / NativeWind / vanilla CSS modules / n/a]
- **Runtime validation:** [e.g. Zod / Pydantic / serde + validator]
- **Data layer:** [e.g. Postgres via Drizzle / Supabase / SQLAlchemy + Postgres / not yet decided]
- **Auth:** [e.g. Clerk / NextAuth / Supabase Auth / rolling my own / not yet decided]
- **Testing:** [e.g. Vitest + Playwright / pytest / Jest + Detox / none yet]
- **Deployment:** [e.g. Vercel / Fly.io / Railway / self-host]
- **CI/CD:** [e.g. GitHub Actions / none yet]

### Backend decision gate

If the project has no backend yet (or parts of it are undecided), keep this rule:

> **Backend decisions require explicit approval.** If a task requires persistence, auth, file storage, background jobs, or any server-side state beyond what the current stack can do — **stop and ask me which service to use before writing code or installing packages.** Do not silently pick Supabase / Firebase / Prisma / Drizzle / any alternative.

Delete this block once all backend pieces are settled.

---

## Stack-specific rules

Add the rules that matter for this stack. Examples of the kind of thing that goes here:

- Server Components vs Client Components defaults (Next.js App Router)
- Sync vs async conventions (FastAPI, Django)
- When to use Server Actions vs API routes (Next.js)
- Hooks rules (React, React Native)
- Concurrency patterns (Go, Rust, async Python)
- ORM vs raw SQL conventions
- State management defaults
- Styling rules (class order, theme tokens, dark mode handling)

**Example block (Next.js App Router):**

> - Default: Server Component. Only add `"use client"` when the component genuinely needs it (hooks, event handlers, browser APIs).
> - Push `"use client"` as far down the tree as possible.
> - When you add `"use client"`, say why in one line.

**Example block (Python + FastAPI):**

> - All route handlers are async unless there's a blocking reason.
> - Pydantic models for every request/response body — no raw dicts across the boundary.
> - Dependency injection for auth, DB sessions, and config — never import the session directly in a handler.

Replace these examples with your real rules.

---

## File layout

Show the agent the directory structure you want. Example:

```
src/
  app/ or pages/      # routes
  components/         # shared UI
  features/           # feature-scoped code
  lib/                # pure helpers, no framework imports
  schemas/            # validation schemas (Zod / Pydantic / etc.)
  types/              # shared types
tests/
```

State any rules:

- Where new files go when the answer isn't obvious
- What goes in `lib/` vs a feature folder (rule of thumb: extract to `lib/` when used in 3+ places)
- What the entry points are

---

## Naming & imports

- File names: [e.g. `kebab-case.ts` for modules, `PascalCase.tsx` for components / `snake_case.py` / `camelCase.ts`]
- Exports: [e.g. named exports preferred, default exports only where the framework requires]
- Imports: [e.g. absolute via `@/...` not relative `../../`]

---

## Production-grade additions (stack-specific)

On top of `CLAUDE.base.md` §3, every feature in this stack also ships with:

- [ ] [stack-specific thing 1, e.g. `loading.tsx` and `error.tsx` per route segment]
- [ ] [stack-specific thing 2, e.g. `metadata` export on pages for SEO]
- [ ] [stack-specific thing 3, e.g. Zod parse of every external response]
- [ ] [etc.]

---

## Red flags in this stack

Things that, if you find yourself about to do them, should make you stop and reconsider:

- [e.g. `"use client"` on a top-level page or layout]
- [e.g. reaching for `useEffect` to fetch data when Server Components exist]
- [e.g. raw SQL when the ORM handles it]
- [e.g. `any` / `as unknown as X` to silence a type error]
- [e.g. installing a state management library before we've discussed it]
