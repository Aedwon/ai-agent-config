# NEW_PROJECT_SETUP.md — Starting a Project Cleanly

This is the playbook for spinning up a new project with a working AI-agent setup. The goal: never start from scratch again.

---

## The template system

```
~/claude-templates/
  CLAUDE.base.md              ← never changes, collaboration contract
  CLAUDE.session.md           ← include for long/marathon projects
  CLAUDE.stack.template.md    ← copy + fill in per project
  PATTERNS.template.md        ← copy + grow per project
  NEW_PROJECT_SETUP.md        ← this file
  README.md                   ← how the system fits together
```

Keep this folder in a dotfiles repo, a private gist, a cloud drive — wherever you can pull from reliably.

---

## Step-by-step: starting a new project

### 1. Identify the project shape

Answer these three questions before you touch code:

1. **What runs the code?** Browser, server, mobile device, CLI, background worker, embedded?
2. **What's the primary framework/language?** (Name it specifically.)
3. **What's the bar?** Weekend prototype, real side project, production app?

Your answers determine how you fill in the stack overlay and how strict the rules should be.

### 2. Copy the files in

From `~/claude-templates/` into the new project root:

```bash
# Always include these two
cp ~/claude-templates/CLAUDE.base.md        ./CLAUDE.base.md

# Include session discipline if the project will have long sessions
cp ~/claude-templates/CLAUDE.session.md     ./CLAUDE.session.md

# Copy and rename the stack template — this is the one you'll fill in
cp ~/claude-templates/CLAUDE.stack.template.md  ./CLAUDE.stack.md

# Copy the patterns template — leave mostly empty, grow as you work
cp ~/claude-templates/PATTERNS.template.md      ./PATTERNS.md
```

### 3. Make a pointer `CLAUDE.md`

Most AI agents look for a single `CLAUDE.md` at the root. Create one that points to the others:

```markdown
# CLAUDE.md

This project uses a split instruction system. Read all of these before your first response:

1. `CLAUDE.base.md` — how we work together (collaboration contract)
2. `CLAUDE.session.md` — token and session discipline
3. `CLAUDE.stack.md` — stack-specific rules for this project
4. `PATTERNS.md` — canonical patterns as they emerge

If any conflict: base wins on collaboration, stack wins on stack specifics.
```

That's it. Four files the agent reads, one entry point.

### 4. Fill in `CLAUDE.stack.md`

Open the file and replace the bracketed placeholders with real answers. Do this before the first prompt, not during. 10 minutes of filling in now saves hours of correction later.

Be specific. "TypeScript strict, no `any`" is a rule. "Use TypeScript well" is not.

### 5. Customize the bar

If it's a prototype, add a note near the top of `CLAUDE.stack.md`:

> **Project bar:** Prototype. Relax accessibility, responsive design, and test coverage unless asked. Keep type safety and error handling.

If it's production, leave the defaults.

An agent that doesn't know the bar over-engineers prototypes and under-engineers production work.

### 6. Verify the agent actually read everything

First prompt of the first session:

> "Summarize the four instruction files in 5 bullets each before we start."

If it can't, it didn't read them. Fix that before writing any code.

---

## Working over time

### After every feature

- Is there a pattern we just established that belongs in `PATTERNS.md`? Add it.
- Did the agent do something that surprised me (good or bad)? That's a candidate rule.

### After every session (for long projects)

- Have the agent produce a handoff summary (`CLAUDE.session.md` §4.1).
- Save it as a Knowledge Item / append to `SESSION_NOTES.md`.
- Commit pending work with descriptive messages.

### After every project

Ask yourself three questions:

1. **Did a rule save me?** Keep it. Maybe strengthen it.
2. **Did a rule get ignored every time?** Either make it enforceable (more specific, with examples) or cut it. Dead rules train the agent to treat the file as flexible.
3. **Did a pattern emerge that isn't documented?** Add it to the relevant `PATTERNS.md` — and if it'd apply to other projects, fold it back into your templates.

### When to spin up a new stack overlay for your templates

After your **2nd project in a stack**, you'll know what the repeatable rules are. Before that, the "overlay" is just notes in that project's `CLAUDE.stack.md` — don't extract prematurely.

Once you have two projects' worth of rules that agree, create:

```
~/claude-templates/stacks/<stack-name>/
  CLAUDE.stack.md
  PATTERNS.starter.md   ← patterns common to that stack
```

Then future `<stack>` projects start from that pre-filled overlay.

---

## Rules of thumb that apply to any stack

These are worth knowing even when you don't yet have a stack overlay:

### Always
- **Validate at trust boundaries.** Every language has this. TS → Zod. Python → Pydantic. Rust → serde + validator. Go → go-playground/validator. Swift → Codable + manual checks.
- **Typed / validated config.** Parse env vars once at startup, fail loudly if invalid.
- **Separate pure logic from I/O.** Business logic that doesn't touch the network, disk, or globals is testable, portable, and survives rewrites.
- **Error handling with context.** `catch` that loses the original error is worse than no catch. Always log what you were trying to do.

### Never (without asking)
- Install a dependency
- Delete files
- Run migrations
- Force-push
- Rewrite working code
- Silently swap one library for another

---

## Language/stack quick-map

When you don't have a stack overlay yet and you're about to start, decide these up-front. If you're unsure, ask the agent: "For a [project type], what's the idiomatic choice for each of these?"

| Concept                | Options to pick from                                        |
|------------------------|-------------------------------------------------------------|
| Runtime validation     | Zod / Pydantic / serde / marshmallow / Yup / Joi            |
| Data fetching (server) | Framework-native / fetch / httpx / requests                 |
| Data fetching (client) | TanStack Query / SWR / RTK Query / none                     |
| Forms                  | react-hook-form + Zod / Formik / native form + validation   |
| ORM / DB               | Drizzle / Prisma / SQLAlchemy / Tortoise / raw SQL          |
| Auth                   | Clerk / Supabase Auth / NextAuth / Auth.js / custom         |
| Testing                | Vitest / Jest / pytest / Go test / XCTest                   |
| E2E testing            | Playwright / Cypress / Detox (RN) / none                    |
| Styling (UI)           | Tailwind / NativeWind / vanilla CSS / CSS Modules           |
| Component lib (web)    | shadcn/ui / Radix / none (from scratch)                     |
| Env validation         | Zod + custom `env.ts` / Pydantic BaseSettings / dotenv-safe |
| Logging                | Pino / Winston / structlog / tracing (Rust) / slog (Go)     |

Decide these **before** the first feature. Changing them later costs more than picking imperfectly now.

---

## Red flags that signal your templates need an update

- You find yourself typing the same instruction into chat across multiple projects → that rule belongs in `CLAUDE.base.md`.
- The agent keeps making the same mistake across projects → that's a guardrail you need to add.
- You copy-paste code between two of your projects → that's a snippet or pattern that belongs in your templates.
- You have to explain the same concept to the agent twice in one project → it belongs in `PATTERNS.md` for that project.

Your templates aren't static documents. They're your accumulated experience, externalized. Treat them like that.
