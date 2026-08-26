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
     -> assign a monotonic delivery order
     -> enqueue small event
        -> Cloudflare Queue consumer
           -> GitHub compare API (read only)
           -> deterministic readiness rules
           -> conditional D1 branch-state update
           -> Discord only when readiness state changes
```

The Queue keeps GitHub API/network retries out of the webhook request path. Queue delivery order is not assumed: D1 delivery ordering prevents an older queued push from overwriting a newer branch state. D1 is the idempotency and derived-state store; GitHub remains the source of truth.

## Why no Workflow or Durable Object yet

This evaluation is short, stateless between steps, and does not need human pause/resume semantics or a strongly consistent per-workstream lock. A Worker + Queue + D1 is sufficient. Workflows and Durable Objects are reserved for later features that actually need those properties.

## GitHub-driven deployment

The experiment has a manual-only workflow at `.github/workflows/cloudflare-readiness-deploy.yml`. It does not deploy on push. A run must be started manually and the `confirm` input must equal `DEPLOY`.

Before the first run, add these repository secrets to `Aedwon/ai-agent-config`:

- `CLOUDFLARE_ACCOUNT_ID` — the one Cloudflare account ID for this experiment.
- `CLOUDFLARE_API_TOKEN` — a Cloudflare API token scoped to that account with **Workers Scripts: Edit**, **D1: Edit**, and **Queues: Edit**.
- `READINESS_WEBHOOK_SECRET` — a strong random value that will also be configured as the GitHub webhook secret.
- `READINESS_GITHUB_TOKEN` — a fine-grained GitHub token with read-only repository access to the test repository. The long-term version should replace this with GitHub App installation tokens.
- `READINESS_DISCORD_WEBHOOK_URL` — optional. If absent, readiness state is still recorded but no Discord notification is sent.

The deployment workflow then:

1. reruns typecheck, tests, and script syntax checks;
2. creates or reuses D1 database `github-readiness-sentinel`;
3. creates or reuses Queue `github-readiness-events`;
4. generates a temporary Wrangler configuration containing the real D1 UUID;
5. applies D1 migrations;
6. upserts an isolated policy for only `Aedwon/ai-agent-config:experiment/github-cloudflare-readiness-sentinel`;
7. deploys the Worker and its runtime secrets in one Wrangler deployment;
8. resolves the deployed URL from Wrangler's structured CI output;
9. calls `/health` and fails the workflow if the deployed Worker does not respond successfully;
10. removes generated secret/configuration files from the runner.

The generated configuration and secret files are ignored by Git and are not committed.

### Cloudflare token scope

The experiment's CI token should be restricted to one Cloudflare account and only these account-level permissions:

```text
Workers Scripts: Edit
D1: Edit
Queues: Edit
```

Do not use a Global API Key. Do not grant DNS, zone, billing, account-admin, R2, KV, or unrelated permissions for this experiment.

## Local setup alternative

If local Wrangler access is preferred later:

```bash
cd experiments/github-cloudflare-readiness
npm install
npx wrangler d1 create github-readiness-sentinel
npx wrangler queues create github-readiness-events
```

Put the returned D1 database ID into a local Wrangler configuration, apply the migration, and set Worker secrets locally. Do not commit secret values.

## Public test policy first

The GitHub deployment workflow automatically upserts an initial policy for the experiment branch in `Aedwon/ai-agent-config`. Pantas is deliberately not configured.

Repository policy is operational data in D1 rather than public source configuration. An empty `allowed_paths_json` array means path scope checking is disabled for that policy.

## GitHub webhook

After the first successful Cloudflare deployment, configure a webhook on the public test repository pointing at:

```text
https://<worker-host>/webhooks/github
```

Use:

- content type: `application/json`;
- the exact secret stored as `READINESS_WEBHOOK_SECRET`;
- only the **Push** event for the first experiment;
- HTTPS only.

`GET /health` is intentionally unauthenticated and returns no repository state.

## Status semantics

- `READY_FOR_VERIFICATION` — deterministic base/scope checks passed. This is **not** a claim that tests or human review passed.
- `ATTENTION` — the branch needs inspection but has no detected scope/base violation, for example no commits above the configured base.
- `BLOCKED` — protected-base lineage, divergence, behind-state, scope checks, or an unprovable oversized comparison failed.

The sentinel suppresses the initial healthy notification and repeated identical states. It notifies on a new problem and on recovery/state transitions.

## Security and failure model

- GitHub webhook HMAC-SHA256 is verified before parsing or accepting an event.
- GitHub delivery IDs are stored as idempotency keys.
- A monotonic D1 delivery order prevents stale Queue messages from replacing newer branch state.
- GitHub API credentials are read-only and stored as Cloudflare Worker secrets.
- The Cloudflare deployment credential exists only as a GitHub repository secret and is not copied into the Worker runtime.
- The Worker does not execute code from the repository or trust PR-controlled scripts.
- Repository contents are not cloned or stored in Cloudflare.
- Changed paths are used transiently for scope validation and are not persisted.
- Comparisons at GitHub's changed-file cap fail closed when path-scope validation is enabled.
- No GitHub write permission is required for the Worker.
- Queue retries cover transient failures in the readiness evaluation path.
- Discord is deliberately a best-effort notification sink. A Discord failure is recorded on the delivery but does not roll back authoritative D1 readiness state.

## Verification

```bash
npm run typecheck
npm test
npm run check:scripts
```

The included tests cover branch-ref parsing, path scopes, policy JSON validation, notification suppression, and GitHub webhook signature verification. The experiment branch also has a path-scoped verification workflow separate from the repository's normal verification workflow.

## Next increments

1. Replace the read token with a least-privilege GitHub App installation token flow.
2. Add `pull_request`, `check_suite`, and `workflow_run` inputs without changing the readiness evaluator into a CI runner.
3. Add an authenticated read-only status endpoint/dashboard over D1.
4. Add optional repository-specific rules such as required checks and integration-branch expectations.
5. Add a low-frequency stale-branch digest using a Cron Trigger.
6. Add a notification outbox if guaranteed Discord delivery becomes important.
7. Introduce Workflows only for durable multi-step/human-approval flows, and Durable Objects only if real concurrent workstream locking becomes necessary.
