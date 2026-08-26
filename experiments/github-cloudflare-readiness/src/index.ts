export interface Env {
  DB: D1Database;
  EVENTS: Queue<ReadinessEvent>;
  GITHUB_WEBHOOK_SECRET: string;
  GITHUB_READ_TOKEN: string;
  DISCORD_WEBHOOK_URL?: string;
}

export interface ReadinessEvent {
  deliveryId: string;
  eventName: "push";
  repoFullName: string;
  branchName: string;
  headSha: string;
}

interface PushPayload {
  after?: string;
  deleted?: boolean;
  ref?: string;
  repository?: {
    full_name?: string;
  };
}

interface RepoPolicy {
  repo_full_name: string;
  branch_glob: string;
  protected_base_sha: string;
  allowed_paths_json: string;
  integration_branch: string | null;
}

interface BranchState {
  status: ReadinessStatus;
}

type ReadinessStatus = "READY_FOR_VERIFICATION" | "ATTENTION" | "BLOCKED";

interface GitHubCompare {
  status: string;
  ahead_by: number;
  behind_by: number;
  merge_base_commit: { sha: string };
  files?: Array<{ filename: string }>;
}

const encoder = new TextEncoder();
const decoder = new TextDecoder();

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return Response.json({ ok: true, service: "github-readiness-sentinel" });
    }

    if (request.method !== "POST" || url.pathname !== "/webhooks/github") {
      return new Response("not found", { status: 404 });
    }

    const rawBody = await request.arrayBuffer();
    const signature = request.headers.get("x-hub-signature-256");
    if (!(await verifyGitHubSignature(env.GITHUB_WEBHOOK_SECRET, rawBody, signature))) {
      return new Response("invalid signature", { status: 401 });
    }

    const eventName = request.headers.get("x-github-event");
    const deliveryId = request.headers.get("x-github-delivery");
    if (!deliveryId || !eventName) {
      return new Response("missing GitHub delivery headers", { status: 400 });
    }

    if (eventName !== "push") {
      return new Response("ignored event", { status: 202 });
    }

    let payload: PushPayload;
    try {
      payload = JSON.parse(decoder.decode(rawBody)) as PushPayload;
    } catch {
      return new Response("invalid JSON", { status: 400 });
    }

    const repoFullName = payload.repository?.full_name;
    const branchName = branchFromRef(payload.ref);
    const headSha = payload.after;
    if (!repoFullName || !branchName || !headSha || payload.deleted || isZeroSha(headSha)) {
      return new Response("ignored push", { status: 202 });
    }

    const duplicate = await env.DB.prepare(
      "SELECT delivery_id FROM webhook_deliveries WHERE delivery_id = ?",
    )
      .bind(deliveryId)
      .first();
    if (duplicate) {
      return new Response("duplicate delivery", { status: 200 });
    }

    const receivedAt = new Date().toISOString();
    await env.DB.prepare(
      `INSERT INTO webhook_deliveries
       (delivery_id, event_name, repo_full_name, status, received_at)
       VALUES (?, ?, ?, 'accepted', ?)`,
    )
      .bind(deliveryId, eventName, repoFullName, receivedAt)
      .run();

    const event: ReadinessEvent = {
      deliveryId,
      eventName: "push",
      repoFullName,
      branchName,
      headSha,
    };

    try {
      await env.EVENTS.send(event);
    } catch (error) {
      await env.DB.prepare("DELETE FROM webhook_deliveries WHERE delivery_id = ?")
        .bind(deliveryId)
        .run();
      console.error("queue send failed", error);
      return new Response("queue unavailable", { status: 503 });
    }

    return new Response("accepted", { status: 202 });
  },

  async queue(batch: MessageBatch<ReadinessEvent>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      try {
        await evaluateBranch(message.body, env);
        message.ack();
      } catch (error) {
        const reason = error instanceof Error ? error.message : "unknown error";
        await env.DB.prepare(
          "UPDATE webhook_deliveries SET status = 'failed', last_error = ? WHERE delivery_id = ?",
        )
          .bind(reason.slice(0, 500), message.body.deliveryId)
          .run();
        console.error("readiness evaluation failed", message.body.deliveryId, error);
        message.retry();
      }
    }
  },
} satisfies ExportedHandler<Env, ReadinessEvent>;

async function evaluateBranch(event: ReadinessEvent, env: Env): Promise<void> {
  const policy = await env.DB.prepare(
    `SELECT repo_full_name, branch_glob, protected_base_sha, allowed_paths_json, integration_branch
     FROM repo_policies
     WHERE repo_full_name = ? AND ? GLOB branch_glob AND enabled = 1
     ORDER BY priority DESC
     LIMIT 1`,
  )
    .bind(event.repoFullName, event.branchName)
    .first<RepoPolicy>();

  if (!policy) {
    await markDelivery(event.deliveryId, "ignored", env);
    return;
  }

  const compare = await fetchCompare(
    event.repoFullName,
    policy.protected_base_sha,
    event.headSha,
    env.GITHUB_READ_TOKEN,
  );

  const files = compare.files ?? [];
  const allowedPaths = parseAllowedPaths(policy.allowed_paths_json);
  const scopeViolations =
    allowedPaths.length === 0
      ? 0
      : files.reduce((count, file) => count + (pathAllowed(file.filename, allowedPaths) ? 0 : 1), 0);

  const reasons: string[] = [];
  if (compare.merge_base_commit.sha !== policy.protected_base_sha) {
    reasons.push("merge base differs from the configured protected base");
  }
  if (compare.status === "diverged") {
    reasons.push("branch diverged from the configured protected base");
  }
  if (compare.behind_by > 0) {
    reasons.push(`branch is ${compare.behind_by} commit(s) behind the configured protected base`);
  }
  if (scopeViolations > 0) {
    reasons.push(`${scopeViolations} changed path(s) exceed the declared scope`);
  }
  if (compare.ahead_by === 0 && reasons.length === 0) {
    reasons.push("branch has no commits above the configured protected base");
  }

  const status: ReadinessStatus =
    reasons.length === 0
      ? "READY_FOR_VERIFICATION"
      : compare.ahead_by === 0 && scopeViolations === 0 && compare.behind_by === 0
        ? "ATTENTION"
        : "BLOCKED";

  const previous = await env.DB.prepare(
    "SELECT status FROM branch_state WHERE repo_full_name = ? AND branch_name = ?",
  )
    .bind(event.repoFullName, event.branchName)
    .first<BranchState>();

  const now = new Date().toISOString();
  await env.DB.prepare(
    `INSERT INTO branch_state
     (repo_full_name, branch_name, head_sha, protected_base_sha, status, ahead_by, behind_by,
      changed_files, scope_violations, reasons_json, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(repo_full_name, branch_name) DO UPDATE SET
       head_sha = excluded.head_sha,
       protected_base_sha = excluded.protected_base_sha,
       status = excluded.status,
       ahead_by = excluded.ahead_by,
       behind_by = excluded.behind_by,
       changed_files = excluded.changed_files,
       scope_violations = excluded.scope_violations,
       reasons_json = excluded.reasons_json,
       updated_at = excluded.updated_at`,
  )
    .bind(
      event.repoFullName,
      event.branchName,
      event.headSha,
      policy.protected_base_sha,
      status,
      compare.ahead_by,
      compare.behind_by,
      files.length,
      scopeViolations,
      JSON.stringify(reasons),
      now,
    )
    .run();

  await markDelivery(event.deliveryId, "completed", env);

  if (shouldNotify(previous?.status ?? null, status)) {
    await sendDiscordSummary(event, status, reasons, compare, scopeViolations, env);
  }
}

async function fetchCompare(
  repoFullName: string,
  baseSha: string,
  headSha: string,
  token: string,
): Promise<GitHubCompare> {
  const [owner, repo] = repoFullName.split("/", 2);
  if (!owner || !repo) {
    throw new Error("invalid repository name");
  }

  const endpoint = `https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/compare/${encodeURIComponent(baseSha)}...${encodeURIComponent(headSha)}`;
  const response = await fetch(endpoint, {
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "User-Agent": "github-readiness-sentinel/0.1",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });

  if (!response.ok) {
    const body = (await response.text()).slice(0, 300);
    throw new Error(`GitHub compare failed (${response.status}): ${body}`);
  }

  return (await response.json()) as GitHubCompare;
}

async function markDelivery(
  deliveryId: string,
  status: "completed" | "ignored",
  env: Env,
): Promise<void> {
  await env.DB.prepare(
    `UPDATE webhook_deliveries
     SET status = ?, completed_at = ?, last_error = NULL
     WHERE delivery_id = ?`,
  )
    .bind(status, new Date().toISOString(), deliveryId)
    .run();
}

async function sendDiscordSummary(
  event: ReadinessEvent,
  status: ReadinessStatus,
  reasons: string[],
  compare: GitHubCompare,
  scopeViolations: number,
  env: Env,
): Promise<void> {
  if (!env.DISCORD_WEBHOOK_URL) {
    return;
  }

  const reasonText = reasons.length > 0 ? reasons.join("; ") : "deterministic checks passed";
  const content = [
    `**Branch readiness changed: ${status}**`,
    `Repository: \`${event.repoFullName}\``,
    `Branch: \`${event.branchName}\``,
    `Head: \`${event.headSha.slice(0, 12)}\``,
    `Ahead/behind: ${compare.ahead_by}/${compare.behind_by}`,
    `Changed paths: ${(compare.files ?? []).length}; scope violations: ${scopeViolations}`,
    `Reason: ${reasonText}`,
  ].join("\n");

  const response = await fetch(env.DISCORD_WEBHOOK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: content.slice(0, 1900) }),
  });

  if (!response.ok) {
    throw new Error(`Discord webhook failed (${response.status})`);
  }
}

export function branchFromRef(ref: string | undefined): string | null {
  const prefix = "refs/heads/";
  return ref?.startsWith(prefix) ? ref.slice(prefix.length) : null;
}

export function pathAllowed(path: string, rules: string[]): boolean {
  return rules.some((rule) => {
    if (rule.endsWith("/**")) {
      const prefix = rule.slice(0, -3).replace(/\/$/, "");
      return path === prefix || path.startsWith(`${prefix}/`);
    }
    return path === rule;
  });
}

export function parseAllowedPaths(raw: string): string[] {
  const value = JSON.parse(raw) as unknown;
  if (!Array.isArray(value) || value.some((entry) => typeof entry !== "string")) {
    throw new Error("allowed_paths_json must be a JSON string array");
  }
  return value as string[];
}

export function shouldNotify(previous: ReadinessStatus | null, next: ReadinessStatus): boolean {
  if (previous === next) {
    return false;
  }
  if (previous === null && next === "READY_FOR_VERIFICATION") {
    return false;
  }
  return true;
}

export async function verifyGitHubSignature(
  secret: string,
  rawBody: ArrayBuffer,
  signature: string | null,
): Promise<boolean> {
  if (!secret || !signature?.startsWith("sha256=")) {
    return false;
  }

  const signatureBytes = hexToBytes(signature.slice("sha256=".length));
  if (!signatureBytes) {
    return false;
  }

  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["verify"],
  );

  return crypto.subtle.verify("HMAC", key, signatureBytes, rawBody);
}

function hexToBytes(value: string): Uint8Array | null {
  if (value.length === 0 || value.length % 2 !== 0 || !/^[0-9a-f]+$/i.test(value)) {
    return null;
  }
  const bytes = new Uint8Array(value.length / 2);
  for (let index = 0; index < bytes.length; index += 1) {
    bytes[index] = Number.parseInt(value.slice(index * 2, index * 2 + 2), 16);
  }
  return bytes;
}

function isZeroSha(value: string): boolean {
  return /^0+$/.test(value);
}
