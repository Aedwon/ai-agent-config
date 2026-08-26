import { writeFile } from "node:fs/promises";

const protectedBaseSha = requireEnv("READINESS_TEST_BASE_SHA");
const repo = "Aedwon/ai-agent-config";
const branch = "experiment/github-cloudflare-readiness-sentinel";
const allowedPaths = [
  "experiments/github-cloudflare-readiness/**",
  ".github/workflows/readiness-sentinel-experiment.yml",
  ".github/workflows/cloudflare-readiness-deploy.yml",
];

const sql = `INSERT INTO repo_policies (
  repo_full_name,
  branch_glob,
  protected_base_sha,
  allowed_paths_json,
  priority,
  enabled
) VALUES (
  ${sqlString(repo)},
  ${sqlString(branch)},
  ${sqlString(protectedBaseSha)},
  ${sqlString(JSON.stringify(allowedPaths))},
  100,
  1
)
ON CONFLICT(repo_full_name, branch_glob) DO UPDATE SET
  protected_base_sha = excluded.protected_base_sha,
  allowed_paths_json = excluded.allowed_paths_json,
  priority = excluded.priority,
  enabled = excluded.enabled;\n`;

await writeFile("policy.ci.sql", sql, "utf8");
console.log(`Prepared read-only test policy for ${repo}:${branch} at base ${protectedBaseSha.slice(0, 12)}.`);

function sqlString(value) {
  return `'${String(value).replaceAll("'", "''")}'`;
}

function requireEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing required environment variable ${name}.`);
  }
  return value;
}
