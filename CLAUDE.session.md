# CLAUDE.session.md — Token & Session Discipline

This file adds **rules for managing tokens, context, and long sessions** on top of `CLAUDE.base.md`. Include it in projects where sessions run long (hours to days on the same code).

Applies to any agentic IDE (Antigravity, Cursor, Windsurf, Claude Code). Where specific features are mentioned (Knowledge Items, Artifacts), translate them to your tool's equivalent.

---

## 1. The core tension

Three goals fight each other:

- **Thoroughness** (ask questions, consider edge cases, explain choices)
- **Token efficiency** (don't repeat yourself, don't re-read files, stay terse)
- **Session longevity** (don't fill the context window, survive long tasks)

You cannot max all three at once. The rules below bias toward **thoroughness on important decisions** and **efficiency on everything else**.

---

## 2. Output shape — terse by default

Long responses eat tokens and attention. Default to:

- **Diffs over full-file rewrites.** If only 5 lines change in a 200-line file, show the 5 lines with context. Only show the full file if I ask or the structure changed significantly.
- **No recap paragraphs.** After making changes, don't summarize what you just did in prose. The diff is the summary. A one-line "updated X, Y, Z — ready for review" is the cap.
- **No "let me know if..." outros.** I know I can follow up.
- **No preamble.** Skip "Great question! Here's what I'll do...". Go straight to the plan block or the work.
- **Code comments in code, not in chat.** If something needs explaining, comment it in the file, not in the response.

When I need more depth, I'll ask "explain that further" or "walk me through X." Default is terse; depth is on demand.

---

## 3. Context discipline — don't re-read what you already read

In a long session, the biggest token waste is re-reading the same files repeatedly.

**Before reading a file, ask: have I already read it in this session?** If yes, and nothing has changed, don't re-read. Work from what you have.

**When you edit a file**, remember the new state. Don't re-read it to "verify" unless you have reason to believe something else changed it.

**Never dump a whole codebase into context "to understand the project."** Read files on demand, in response to specific questions. The IDE's file index and search are faster and cheaper than reading.

**When I reference a file, read that file — not ten related ones.** Expand scope only when the task genuinely requires it, and say when you do: "Also reading X because Y imports it."

---

## 4. Session length management

### 4.1 End-of-session handoff

When I say **"wrap up"** or **"end session"**, produce a **handoff summary** before closing out:

```
## Session Handoff
**What we finished:** <bullet list of completed features>
**What's in flight:** <anything started but not done, with current state>
**Decisions made:** <architectural or scope decisions worth remembering>
**Known issues / follow-ups:** <bugs deferred, TODOs created, questions unresolved>
**Where to pick up:** <specific next step>
```

Save this as a Knowledge Item (Antigravity) or append to `SESSION_NOTES.md` at the project root. Future sessions read this at the start instead of re-deriving everything.

### 4.2 Mid-session checkpoints

For features that take more than ~30 minutes, checkpoint the plan as you complete milestones:

```
## Checkpoint
**Done:** ✓ <item>  ✓ <item>
**Next:** → <item>
**Blocked on:** <if anything>
```

Keep it to 3–5 lines. This is the anchor that prevents **context rot** — where you forget, ten prompts in, what we were originally doing.

### 4.3 Resuming a session

At the start of a new session on existing work, **before writing code**:

1. Check for a `SESSION_NOTES.md` or Knowledge Item from the last session.
2. Restate the current goal in one sentence back to me.
3. Confirm you have the latest state of the relevant files (don't assume — re-verify if code was written outside the agent).

This is 30 seconds of investment that saves hours of "wait, you deleted the middleware I added yesterday" pain.

### 4.4 When context is getting full

If you sense context pressure (responses slowing, older parts of conversation getting vague), **proactively suggest** splitting the work:

> "We're ~60% through this feature. I suggest we wrap up what's done, write a handoff summary, and resume in a fresh session for the rest."

Don't wait for the context window to fill. Degraded context produces worse code.

---

## 5. Mode prefixes — one line that replaces an outro

Instead of long instructions at the end of prompts, I can put **mode prefixes** at the start. You should recognize and respond to them:

| Prefix | Meaning |
|---|---|
| `[plan]` | Plan only — don't write code. Give me the plan block (base §2.1), then stop. |
| `[quick]` | Trivial task, skip the plan block. Just do it and show the diff. |
| `[deep]` | Non-trivial. Plan block + more explanation of choices + flag what I should learn. |
| `[review]` | Don't change code, review what's there. Point out issues by severity. |
| `[explain]` | Don't change code, explain what exists. No edits unless asked. |
| `[debug]` | Diagnostic mode. Read, hypothesize, propose — don't patch until I approve. |
| `[learn]` | Tutor mode turned up. Teach me the concept, ideally with the code in front of us. |

If no prefix is given, assume `[deep]` for anything that isn't obviously a one-line fix.

---

## 6. Things that waste tokens — don't do these

- Re-stating my question back to me at the start of a response
- Listing out "what I'm going to do" and then doing it (the plan block replaces this; don't do both)
- Full-file dumps when a diff would do
- Explaining code that speaks for itself
- Apology paragraphs when something goes wrong ("I sincerely apologize for the confusion. Let me correct this..." → just correct it)
- Re-listing project rules back to me ("As per CLAUDE.md, I'll use X...") — just follow them
- Asking permission for things you've already been given permission for (don't re-confirm a plan I just approved)
- Reading files you've already read, unread, and re-read

---

## 7. Things that SAVE tokens — do these

- **Commit frequently.** Completed work in git is free context — it's in the diff history, not your working memory.
- **Delete your own scratch.** If you wrote exploratory code that's not needed, remove it. Don't let it linger.
- **Use file pointers, not file contents.** "See `src/lib/auth.ts` for the existing pattern" is better than pasting the file.
- **Artifact important decisions.** Save architectural decisions as a Knowledge Item, an Artifact, or in a `DECISIONS.md` — then reference them instead of re-deriving.
- **Keep plan blocks updated, not re-written.** If the plan evolves, edit the checkpoint, don't restate the whole plan.

---

## 8. When I'm about to run out

If I say "context feels full" or "running low," do this **in order**:

1. Produce a handoff summary (§4.1).
2. Commit current work with a descriptive message (base §2.7).
3. Suggest what to carry into the next session and what to leave behind.
4. Wait for me to start a fresh session.

Don't try to "compress" by summarizing the current conversation and continuing. That's how bugs slip in — compressed context loses the detail that matters.
