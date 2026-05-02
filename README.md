# claude-templates

A portable instruction system for working with AI coding agents. Stack-agnostic, reusable across any software project, designed for developers who direct AI agents to scaffold, iterate, and ship production code.

Works with Claude Code, Cursor, Windsurf, Antigravity, and any other agent that reads `CLAUDE.md`-style instruction files.

---

## Compatibility & multi-model use

The content files (`CLAUDE.base.md`, `CLAUDE.session.md`, etc.) are model-agnostic. The `CLAUDE.*` naming is historical, not a signal that only Claude should read them. To make sure the stack is actually loaded regardless of which tool or model you're using:

- Create three pointer files at the project root — `CLAUDE.md`, `GEMINI.md`, and `AGENTS.md` — all containing the same one-screen pointer text (see [`NEW_PROJECT_SETUP.md`](./NEW_PROJECT_SETUP.md) step 3).
- Different tools discover different filenames: Claude Code reads `CLAUDE.md`, Gemini CLI reads `GEMINI.md`, Antigravity reads `AGENTS.md`. Three pointer files = guaranteed discovery across tools.
- Per-model behavioral notes (e.g. nudging Gemini to be more explanatory than its default) live in [`CLAUDE.base.md`](./CLAUDE.base.md) §10.
- If you use installed skills (e.g. `superpowers:*`, `frontend-design`), see [`CLAUDE.session.md`](./CLAUDE.session.md) §5.1 — your file stack outranks skills, and mode prefixes override skill-mandated workflows.

---

## Why this exists

AI coding agents produce mediocre work by default. Not because the models are weak, but because every session starts with the agent knowing nothing about you, your stack, your conventions, or how you want to collaborate. Most developers paper over this by typing the same instructions at the end of every prompt — which wastes tokens, wastes attention, and still doesn't work reliably.

This repo is the system I use to fix that. Four small files at the root of a project, plus a couple of templates to fill in per project, and the agent walks in already knowing how to work with me.

---

## What's in here

| File | Purpose |
|---|---|
| [`CLAUDE.base.md`](./CLAUDE.base.md) | Collaboration contract — how the agent and I work together. Never changes across projects. |
| [`CLAUDE.session.md`](./CLAUDE.session.md) | Token and session discipline for long sessions. Includes mode prefixes (`[deep]`, `[quick]`, `[plan]`, etc.). |
| [`CLAUDE.stack.template.md`](./CLAUDE.stack.template.md) | Template for stack-specific rules (framework, language, libraries). Copy + fill in per project. |
| [`PATTERNS.template.md`](./PATTERNS.template.md) | Template for canonical project patterns. Copy + grow as the project develops. |
| [`NEW_PROJECT_SETUP.md`](./NEW_PROJECT_SETUP.md) | Step-by-step playbook for spinning up a new project with this system. |
| [`SYSTEM_GUIDE.md`](./SYSTEM_GUIDE.md) | Detailed guide to the system itself (how the files relate, philosophy, maintenance). |

---

## How it works in 30 seconds

Most people cram everything into one giant `CLAUDE.md`. This system splits it into layers:

```
Project root:
  CLAUDE.md           ← pointer file (tells agent to read the others)
  CLAUDE.base.md      ← collaboration rules (identical across all projects)
  CLAUDE.session.md   ← session discipline (identical across all projects)
  CLAUDE.stack.md     ← stack-specific rules (unique per project)
  PATTERNS.md         ← canonical examples (unique per project, grows over time)
```

The base and session files get reused forever. The stack file gets filled in once per project. The patterns file grows as the project develops.

---

## Quick start

1. Clone or download this repo
2. Copy the four core files into a new project root
3. Rename `CLAUDE.stack.template.md` → `CLAUDE.stack.md` and `PATTERNS.template.md` → `PATTERNS.md`
4. Fill in `CLAUDE.stack.md` with your stack details
5. Create a pointer `CLAUDE.md` at the root (example in [`NEW_PROJECT_SETUP.md`](./NEW_PROJECT_SETUP.md))
6. First prompt: *"Summarize the four instruction files in 5 bullets each before we start."*

Full walkthrough in [`NEW_PROJECT_SETUP.md`](./NEW_PROJECT_SETUP.md).

---

## The principles behind it

**Rules beat reminders.** If you're typing the same instruction at the end of prompts, it belongs in a file. Every reminder is a tax.

**Ask on ambiguity, decide on tactics.** A good agent asks about branch points and decides on naming. A bad agent asks about naming and decides on architecture. Files enforce the right split.

**Context is scarce.** Long sessions fail not because models are bad but because context decays. Explicit session management (handoffs, checkpoints, mode prefixes) is how you survive marathon work.

---

## The one habit change that matters most

Stop typing instructions at the end of prompts. Start using **mode prefixes at the beginning**:

- `[quick]` — trivial task, skip the plan
- `[deep]` — non-trivial, plan first
- `[plan]` — plan only, no code
- `[review]` — review existing code, don't change it
- `[debug]` — diagnose, don't patch
- `[explain]` — explain existing code
- `[learn]` — teach me the concept

One line replaces a paragraph. Defined in [`CLAUDE.session.md`](./CLAUDE.session.md).

---

## License & use

Use these however you want. Fork, adapt, strip for parts, rewrite entirely. The templates reflect my preferences — a developer should absolutely shape their own version over time.

If you build on top of this, I'd love to see it.

---

## Credits

Developed iteratively through a long conversation with Claude (Anthropic), refined against real use of agent-first IDEs. The structure is mine; the prose is largely Claude's; the accumulated opinions are earned.
