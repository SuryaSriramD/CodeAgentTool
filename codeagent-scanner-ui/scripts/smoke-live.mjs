// Acceptance check against an already running local Compose workspace.
// The tiny ZIP contains synthetic Python/JS findings and requests==2.19.1.
// Nothing in the archive is executed, installed, or sent to a model.
import assert from "node:assert/strict";
import { mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "@playwright/test";

const base = process.env.CODEAGENT_TEST_URL || "http://localhost:3000";
const output = resolve("test-results/live");
const archive = Buffer.from("UEsDBBQAAAAAALdqOV1MkWa2YQAAAGEAAAALAAAAZGVtby9hcHAucHlpbXBvcnQgc3VicHJvY2VzcwoKZGVmIHJ1bl91c2VyX2NvbW1hbmQoY29tbWFuZCk6CiAgICByZXR1cm4gc3VicHJvY2Vzcy5ydW4oY29tbWFuZCwgc2hlbGw9VHJ1ZSkKUEsDBBQAAAAAALdqOV2u+UjEMwAAADMAAAALAAAAZGVtby9hcHAuanNmdW5jdGlvbiBwYXJzZUlucHV0KGlucHV0KSB7IHJldHVybiBldmFsKGlucHV0KTsgfQpQSwMEFAAAAAAAt2o5XRgUTD4RAAAAEQAAABUAAABkZW1vL3JlcXVpcmVtZW50cy50eHRyZXF1ZXN0cz09Mi4xOS4xClBLAQIUAxQAAAAAALdqOV1MkWa2YQAAAGEAAAALAAAAAAAAAAAAAACAAQAAAABkZW1vL2FwcC5weVBLAQIUAxQAAAAAALdqOV2u+UjEMwAAADMAAAALAAAAAAAAAAAAAACAAYoAAABkZW1vL2FwcC5qc1BLAQIUAxQAAAAAALdqOV0YFEw+EQAAABEAAAAVAAAAAAAAAAAAAACAAeYAAABkZW1vL3JlcXVpcmVtZW50cy50eHRQSwUGAAAAAAMAAwC1AAAAKgEAAAAA", "base64");
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, baseURL: base });
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
try {
  await page.goto(base, { waitUntil: "networkidle" });
  if (process.env.CODEAGENT_TEST_PASSWORD) {
    await page.getByLabel("Workspace password").fill(process.env.CODEAGENT_TEST_PASSWORD);
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
  }
  await page.getByRole("button", { name: "ZIP archive", exact: true }).click();
  await page.getByLabel("New project name").fill(`Live acceptance ${new Date().toISOString()}`);
  await page.getByRole("button", { name: "Create project", exact: true }).click();
  await page.waitForFunction(() => document.querySelector("#zip-project")?.value);
  await page.locator("#source-file").setInputFiles({ name: "acceptance-fixture.zip", mimeType: "application/zip", buffer: archive });
  await page.getByRole("button", { name: "Start scan", exact: true }).click();
  await page.waitForURL(/\/jobs\/[a-f0-9-]+$/, { timeout: 30000 });
  const jobId = page.url().split("/").pop();
  await page.getByRole("link", { name: "View report", exact: true }).waitFor({ timeout: 180000 });
  await page.getByRole("link", { name: "View report", exact: true }).click();
  await page.getByRole("heading", { name: "Source findings", exact: true }).waitFor();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export report", exact: true }).click();
  const exportedPath = resolve(output, "report.json");
  await (await download).saveAs(exportedPath);
  const exported = JSON.parse(await readFile(exportedPath, "utf8"));
  assert.equal(exported.job_id, jobId);
  assert.equal(exported.status, "completed");
  assert.ok(exported.summary.high > 0);
  assert.ok(exported.coverage.some((entry) => entry.tool === "depcheck" && entry.status === "completed"));
  assert.equal(exported.ai_analysis ?? null, null);
  assert.deepEqual(errors, []);
  await page.screenshot({ path: resolve(output, "report.png"), fullPage: true });
  console.log(JSON.stringify({ passed: true, jobId, status: exported.status, summary: exported.summary, artifacts: output }));
} catch (error) {
  await page.screenshot({ path: resolve(output, "failure.png"), fullPage: true });
  throw error;
} finally {
  await browser.close();
}
