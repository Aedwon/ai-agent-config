import { writeFile } from "node:fs/promises";

const accountId = requireEnv("CLOUDFLARE_ACCOUNT_ID");
const apiToken = requireEnv("CLOUDFLARE_API_TOKEN");

const databaseName = "github-readiness-sentinel";
const queueName = "github-readiness-events";

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
console.log(`Prepared Cloudflare config for D1 ${databaseName} (${database.uuid}) and Queue ${queueName}.`);

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
  const response = await fetch(`https://api.cloudflare.com/client/v4${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${apiToken}`,
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok || !payload?.success) {
    const errors = Array.isArray(payload?.errors)
      ? payload.errors.map((error) => error.message ?? error.code).join("; ")
      : "unknown Cloudflare API error";
    throw new Error(`Cloudflare API ${response.status} for ${path}: ${errors}`);
  }
  return payload;
}

function requireEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing required environment variable ${name}.`);
  }
  return value;
}
