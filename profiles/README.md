# Personal Profiles

A profile adds private working preferences after project rules and selected
workflows. It may define writing style, preferred ceremony, routing choices, or
local account constraints.

Cloning this repository does not create or discover a profile. Run
`python3 -m tooling.config init ...` if you want guided project setup; the
initializer can optionally copy `profiles/example.md` to an explicit path you
choose. You can also create a profile yourself.

Keep real profiles outside this public repository when they reveal identity,
paths, accounts, or commercial terms. Supply a selected profile explicitly at
render or diff time with `--profile /path/to/profile.md`.

A profile cannot grant mutation authority, override project decisions, weaken
non-waivable invariants, or silently change provider configuration.
