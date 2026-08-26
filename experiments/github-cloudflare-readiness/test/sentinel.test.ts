import { describe, expect, it } from "vitest";
import {
  branchFromRef,
  parseAllowedPaths,
  pathAllowed,
  shouldNotify,
  verifyGitHubSignature,
} from "../src/index";

describe("branchFromRef", () => {
  it("accepts branch refs only", () => {
    expect(branchFromRef("refs/heads/feature/test")).toBe("feature/test");
    expect(branchFromRef("refs/tags/v1.0.0")).toBeNull();
  });
});

describe("pathAllowed", () => {
  it("supports exact paths and recursive directory scopes", () => {
    const rules = ["README.md", "src/control/**"];
    expect(pathAllowed("README.md", rules)).toBe(true);
    expect(pathAllowed("src/control/check.ts", rules)).toBe(true);
    expect(pathAllowed("src/other/check.ts", rules)).toBe(false);
  });
});

describe("parseAllowedPaths", () => {
  it("requires an array of strings", () => {
    expect(parseAllowedPaths('["src/**"]')).toEqual(["src/**"]);
    expect(() => parseAllowedPaths('{"src": true}')).toThrow();
    expect(() => parseAllowedPaths('[1]')).toThrow();
  });
});

describe("shouldNotify", () => {
  it("suppresses initial healthy state and repeated states", () => {
    expect(shouldNotify(null, "READY_FOR_VERIFICATION")).toBe(false);
    expect(shouldNotify("BLOCKED", "BLOCKED")).toBe(false);
    expect(shouldNotify(null, "BLOCKED")).toBe(true);
    expect(shouldNotify("BLOCKED", "READY_FOR_VERIFICATION")).toBe(true);
  });
});

describe("verifyGitHubSignature", () => {
  it("verifies GitHub HMAC SHA-256 signatures", async () => {
    const secret = "test-secret";
    const body = new TextEncoder().encode('{"hello":"world"}');
    const key = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"],
    );
    const digest = new Uint8Array(await crypto.subtle.sign("HMAC", key, body));
    const signature = `sha256=${Array.from(digest, (byte) => byte.toString(16).padStart(2, "0")).join("")}`;
    const rawBody = body.buffer.slice(body.byteOffset, body.byteOffset + body.byteLength) as ArrayBuffer;

    await expect(verifyGitHubSignature(secret, rawBody, signature)).resolves.toBe(true);
    await expect(verifyGitHubSignature("wrong-secret", rawBody, signature)).resolves.toBe(false);
  });
});
