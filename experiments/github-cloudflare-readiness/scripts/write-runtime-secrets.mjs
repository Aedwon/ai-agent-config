import { writeFile } from "node:fs/promises";

const secrets = {
  GITHUB_WEBHOOK_SECRET: requireEnv("READINESS_WEBHOOK_SECRET"),
  GITHUB_READ_TOKEN: requireEnv("READINESS_GITHUB_TOKEN"),
};

const discord = process.env.READINESS_DISCORD_WEBHOOK_URL?.trim();
if (discord) {
  secrets.DISCORD_WEBHOOK_URL = discord;
}

await writeFile("secrets.ci.json", `${JSON.stringify(secrets)}\n`, { mode: 0o600 });
console.log(`Prepared ${Object.keys(secrets).length} Worker secret(s) without printing their values.`);

function requireEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing required environment variable ${name}.`);
  }
  return value;
}
