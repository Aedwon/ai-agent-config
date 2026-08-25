# Bot Service Overlay

Baseline: `software-project.md`

Add these rules for event-driven services, background workers, and chat or
automation bots.

- Request the least permission needed and validate authorization at every
  command or event boundary.
- Make background work durable when loss matters; define retries,
  idempotency, and duplicate-event behavior.
- Recover safely after restart and test work that was queued, running, or partly
  completed.
- Version persistent state and define forward and rollback migration behavior.
- Respect upstream rate limits with bounded retries, backoff, and useful failure
  reporting.
- Exercise operational failure paths: unavailable dependencies, malformed
  events, partial delivery, permission changes, and shutdown during work.
