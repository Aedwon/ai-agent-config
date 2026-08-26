import { createHash } from "node:crypto";
import { writeFile } from "node:fs/promises";

const accountId = requireEnv("CLOUDFLARE_ACCOUNT_ID");
const apiToken = requireEnv("CLOUDFLARE_API_TOKEN");

const databaseName = "github-readiness-sentinel";
const queueName = "github-readiness-events";

const workersSubdomain = await findOrCreateWorkersDevSubdomain();
const database = await findOrCreateD1(databaseName);
await findOrCreateQueue(queueName);

const config = {
  $schema: "node_modules/wrangler/config-schema.json",
  name: "github-readiness-sentinel",
  main: "src/index.ts",
  compatibility_date: "2026-08-01",
  d1_databases: [
    {
      binding: "DB",
      database_name: databaseName,
      database_id: database.uuid,
      migrations_dir: "migrations",
    },
  ],
  queues: {
    producers: [{ binding: "EVENTS", queue: queueName }],
    consumers: [
      {
        queue: queueName,
        max_batch_size: 10,
        max_batch_timeout: 5,
        max_retries: 5,
      },
    ],
  },
  observability: { enabled: true },
};

await writeFile("wrangler.ci.json", `${JSON.stringify(config, null, 2)}\n`, "utf8");
console.log(
  `Prepared Cloudflare config for workers.dev subdomain ${workersSubdomain}, D1 ${databaseName} (${database.uuid}), and Queue ${queueName}.`,
);

async function findOrCreateWorkersDevSubdomain() {
  const path = `/accounts/${accountId}/workers/subdomain`;
  const existing = await cloudflareRaw(path);
  if (existing.response.ok && existing.payload?.success && existing.payload.result?.subdomain) {
    console.log(`Reusing workers.dev subdomain ${existing.payload.result.subdomain}.`);
    return existing.payload.result.subdomain;
  }

  const fallback = createHash("sha256").update(accountId).digest("hex").slice(0, 8);
  const candidates = ["aedwon", "aedwon-dev", `aedwon-dev-${fallback}`];
  const errors = [];

  for (const subdomain of candidates) {
    const created = await cloudflareRaw(path, {
      method: "PUT",
      body: JSON.stringify({ subdomain }),
    });
    if (created.response.ok && created.payload?.success && created.payload.result?.subdomain) {
      console.log(`Created workers.dev subdomain ${created.payload.result.subdomain}.`);
      return created.payload.result.subdomain;
    }

    errors.push(`${subdomain}: ${formatErrors(created.payload)}`);
    if (![400, 409].includes(created.response.status)) {
      throw new Error(
        `Cloudflare could not create a workers.dev subdomain (${created.response.status}): ${formatErrors(created.payload)}`,
      );
    }
  }

  throw new Error(`Cloudflare could not allocate a workers.dev subdomain: ${errors.join(" | ")}`);
}

async function findOrCreateD1(name) {
  const listed = await cloudflare(
    `/accounts/${accountId}/d1/database?name=${encodeURIComponent(name)}&per_page=100`,
  );
  const exact = listed.result?.find((entry) => entry.name === name);
  if (exact?.uuid) {
    console.log(`Reusing D1 database ${name}.`);
    return exact;
  }

  const created = await cloudflare(`/accounts/${accountId}/d1/database`, {
    method: "POST",
    body: JSON.stringify({ name }),
  });
  if (!created.result?.uuid) {
    throw new Error(`Cloudflare created D1 ${name} without returning a UUID.`);
  }
  console.log(`Created D1 database ${name}.`);
  return created.result;
}

async function findOrCreateQueue(name) {
  const listed = await cloudflare(`/accounts/${accountId}/queues`);
  const exact = listed.result?.find((entry) => entry.queue_name === name);
  if (exact?.queue_id) {
    console.log(`Reusing Queue ${name}.`);
    return exact;
  }

  const created = await cloudflare(`/accounts/${accountId}/queues`, {
    method: "POST",
    body: JSON.stringify({ queue_name: name }),
  });
  if (!created.result?.queue_id) {
    throw new Error(`Cloudflare created Queue ${name} without returning an ID.`);
  }
  console.log(`Created Queue ${name}.`);
  return created.result;
}

async function cloudflare(path, init = {}) {
  const { response, payload } = await cloudflareRaw(path, init);
  if (!response.ok || !payload?.success) {
    throw new Error(`Cloudflare API ${response.status} for ${path}: ${formatErrors(payload)}`);
  }
  return payload;
}

async function cloudflareRaw(path, init = {}) {
  const response = await fetch(`https://api.cloudflare.com/client/v4${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${apiToken}`,
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });
  const payload = await response.json().catch(() => null);
  return { response, payload };
}

function formatErrors(payload) {
  return Array.isArray(payload?.errors)
    ? payload.errors.map((error) => error.message ?? error.code).join("; ")
    : "unknown Cloudflare API error";
}

function requireEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing required environment variable ${name}.`);
  }
  return value;
}
