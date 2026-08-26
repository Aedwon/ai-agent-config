# GitHub + Cloudflare Branch Readiness Sentinel

A small, read-only experiment for turning GitHub branch pushes into deterministic readiness checks without spending GitHub Actions minutes.

The first version intentionally does **not** merge branches, create branches, change pull requests, dispatch workflows, or fetch repository file contents.

## What it checks

For configured repository/branch patterns, a push event is evaluated against a configured protected base SHA.

The sentinel checks:

- whether the branch still descends from the configured protected base;
- whether it has unexpectedly diverged or fallen behind that base;
- whether changed paths stay inside a configured scope;
- whether there is any work above the protected base.

It records only derived coordination state in D1. Changed file paths are processed in memory and are not persisted or sent to Discord. Discord notifications contain counts and status changes, not source code or file names.

## Event flow

```text
GitHub push webhook
  -> Cloudflare Worker
     -> verify X-Hub-Signature-256
     -> deduplicate X-GitHub-Delivery in D1
     -> enqueue small event
        -> Cloudflare Queue consumer
           -> GitHub compare API (read only)
           -> deterministic readiness rules
           -> D1 branch state
           -> Discord only when readiness state changes
```

The Queue keeps GitHub API/network retries out of the webhook request path. D1 is the idempotency and derived-state store; GitHub remains the source of truth.

## Why no Workflow or Durable Object yet

This evaluation is short, stateless between steps, and does not need human pause/resume semantics or a strongly consistent per-workstream lock. A Worker + Queue + D1 is sufficient. Workflows and Durable Objects are reserved for later features that actually need those properties.

## Local setup

```bash
cd experiments/github-cloudflare-readiness
npm install
npx wrangler d1 create github-readiness-sentinel
npx wrangler queues create github-readiness-events
```

Put the returned D1 database ID into `wrangler.jsonc`, then apply the migration:

```bash
npx wrangler d1 migrations apply github-readiness-sentinel --remote
```

Add secrets with Wrangler; never commit their values:

```bash
npx wrangler secret put GITHUB_WEBHOOK_SECRET
npx wrangler secret put GITHUB_READ_TOKEN
npx wrangler secret put DISCORD_WEBHOOK_URL
```

`DISCORD_WEBHOOK_URL` is optional. If omitted, evaluations still update D1 and generate no external notification.

For the experiment, `GITHUB_READ_TOKEN` should be a fine-grained read-only token restricted to only the test repository or repositories. The long-term multi-repository version should replace this token with short-lived GitHub App installation tokens.

## Configure a public test repository first

Repository policy is operational data and is deliberately not committed to this public experiment branch.

Example only:

```sql
INSERT INTO repo_policies (
  repo_full_name,
  branch_glob,
  protected_base_sha,
  allowed_paths_json,
  priority
) VALUES (
  'example/repository',
  'experiment/*',
  '0123456789abcdef0123456789abcdef01234567',
  '["src/**","test/**","README.md"]',
  100
);
```

An empty `allowed_paths_json` array means path scope checking is disabled for that policy.

## GitHub webhook

After deployment, configure a repository webhook pointing at:

```text
https://<worker-host>/webhooks/github
```

Use:

- content type: `application/json`;
- a strong random webhook secret matching `GITHUB_WEBHOOK_SECRET`;
- only the **Push** event for the first experiment;
- HTTPS only.

`GET /health` is intentionally unauthenticated and returns no repository state.

## Status semantics

- `READY_FOR_VERIFICATION` — deterministic base/scope checks passed. This is **not** a claim that tests or human review passed.
- `ATTENTION` — the branch needs inspection but has no detected scope/base violation (for example, no commits above the configured base).
- `BLOCKED` — protected-base lineage, divergence, behind-state, or scope checks failed.

The sentinel suppresses the initial healthy notification and repeated identical states. It notifies on a new problem and on recovery/state transitions.

## Security model

- GitHub webhook HMAC-SHA256 is verified before parsing or accepting an event.
- GitHub delivery IDs are stored as idempotency keys.
- GitHub API credentials are read-only and stored as Cloudflare secrets.
- The Worker does not execute code from the repository or trust PR-controlled scripts.
- Repository contents are not cloned or stored in Cloudflare.
- Changed paths are used transiently for scope validation and are not persisted.
- No GitHub write permission is required for this version.
- Queue retries handle transient GitHub/Discord failures; failed delivery state remains visible in D1.

## Verification

```bash
npm run typecheck
npm test
```

The included tests cover branch-ref parsing, path scopes, policy JSON validation, notification suppression, and GitHub webhook signature verification.

## Next increments

1. Replace the read token with a least-privilege GitHub App installation token flow.
2. Add `pull_request`, `check_suite`, and `workflow_run` inputs without changing the readiness evaluator into a CI runner.
3. Add an authenticated read-only status endpoint/dashboard over D1.
4. Add optional repository-specific rules such as required checks and integration-branch expectations.
5. Add a low-frequency stale-branch digest using a Cron Trigger.
6. Introduce Workflows only for durable multi-step/human-approval flows, and Durable Objects only if real concurrent workstream locking becomes necessary.
