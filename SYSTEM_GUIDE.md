# Claude Templates — Read Me

A portable instruction system for working with AI coding agents. Stack-agnostic, reusable across any software project.

---

## What's in this folder

| File | Purpose | When to use |
|---|---|---|
| `CLAUDE.base.md` | Collaboration contract — how you and the agent work together. | **Every project.** Never changes. |
| `CLAUDE.session.md` | Token and session discipline for long sessions. | Any project with marathon sessions (days on same code). |
| `CLAUDE.stack.template.md` | Template for stack-specific rules (framework, language, libraries). | **Every project.** Copy, rename to `CLAUDE.stack.md`, fill in. |
| `PATTERNS.template.md` | Template for project-specific canonical patterns and examples. | **Every project.** Copy, rename to `PATTERNS.md`, grow as you go. |
| `NEW_PROJECT_SETUP.md` | Step-by-step playbook for starting a new project. | Read before starting any new project. |
| `README.md` | This file. | Now. |

---

## How the system works

AI coding agents work best when they know three things:

1. **How to collaborate with you** — plan-first, when to ask, when to decide, how to debug, how to commit.
2. **What the stack is** — what framework, language, libraries, conventions, file layout.
3. **What canonical patterns exist** — examples of "how we do X in this project."

Most people cram all three into one file, or skip them and hope the agent figures it out. Both fail.

This system splits them:

```
Project root:
  CLAUDE.md            ← pointer file for Claude Code
  GEMINI.md            ← pointer file for Gemini CLI (same content as CLAUDE.md)
  AGENTS.md            ← pointer file for Antigravity / cross-tool (same content)
  CLAUDE.base.md       ← collaboration rules (identical across all projects)
  CLAUDE.session.md    ← session discipline (identical across all projects)
  CLAUDE.stack.md      ← stack-specific rules (unique per project)
  PATTERNS.md          ← canonical examples (unique per project, grows over time)
```

The base and session files you reuse forever. The stack file you fill in once per project. The patterns file grows as you work. The three pointer files exist because different tools discover different filenames — keep them all so the stack is loaded no matter which tool/model you launch (Claude Code, Antigravity, Gemini CLI, etc.). Per-model behavioral nudges live in `CLAUDE.base.md` §10; skill-vs-mode-prefix arbitration lives in `CLAUDE.session.md` §5.1.

---

## Quick start for a new project

1. Copy `CLAUDE.base.md`, `CLAUDE.session.md`, `CLAUDE.stack.template.md`, and `PATTERNS.template.md` into the new project root.
2. Rename the two templates: `CLAUDE.stack.template.md` → `CLAUDE.stack.md` and `PATTERNS.template.md` → `PATTERNS.md`.
3. Create a pointer `CLAUDE.md` at the root (example in `NEW_PROJECT_SETUP.md` step 3).
4. Fill in `CLAUDE.stack.md` with your stack details.
5. First prompt: `"Summarize the four instruction files in 5 bullets each before we start."`
6. If the agent passes that, start working.

Full walkthrough in `NEW_PROJECT_SETUP.md`.

---

## The philosophy

Three principles shaped this system:

**1. Rules > reminders.** If you're typing the same instruction at the end of prompts, it belongs in a file. Every reminder is a tax.

**2. Ask on ambiguity, decide on tactics.** A good agent asks about branch points and decides on naming. A bad agent asks about naming and decides on architecture. Files enforce the right split.

**3. Context is scarce.** Long sessions fail not because models are bad but because context decays. Explicit session management (handoffs, checkpoints, mode prefixes) is how you survive marathon work.

---

## Maintenance

The templates are meant to evolve. After every project:

- **Did a rule save you?** Keep it, maybe strengthen it.
- **Did a rule get ignored every time?** Make it more specific, or cut it.
- **Did a new pattern emerge that'd apply to other projects?** Fold it back into the templates.

Your templates are your accumulated experience, externalized. A year from now they should look meaningfully different from today.

---

## One habit change that matters most

Stop typing instructions at the end of prompts. Start using **mode prefixes at the beginning**:

- `[quick]` — trivial task, skip the plan
- `[deep]` — non-trivial, plan first
- `[plan]` — plan only, no code
- `[review]` — review existing code, don't change it
- `[debug]` — diagnose, don't patch
- `[explain]` — explain existing code
- `[learn]` — teach me the concept

Defined in `CLAUDE.session.md` §5. One line replaces a paragraph. Over a marathon session that's thousands of tokens saved and clearer signals to the agent.
