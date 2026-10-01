import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';
import type { Report } from '../lib/types';

const projectId = 'project-one';
const aiSettings = { provider: 'ollama', model: 'local-model', min_severity: 'high', max_model_calls: 60, max_total_tokens: 100000, timeout_sec: 900, max_findings: 20, max_context_chars: 60000, max_output_tokens: 4000 };
const scanId = '11111111-1111-4111-8111-111111111111';
const reviewId = '22222222-2222-4222-8222-222222222222';
const capabilities = { ready: true, worker_online: true, auth_required: false,
  analyzers: [{ name: 'semgrep', available: true, version: '1.0', languages: ['Python', 'JavaScript'] }],
  languages: ['Python', 'JavaScript'], providers: { ollama: { available: true, models: ['local-model'] }, openai: { available: true, models: ['cloud-model'] } },
};
const scan = { job_id: scanId, kind: 'scan', status: 'partial', progress: { phase: 'report', percent: 100 }, submitted_at: '2026-01-01T10:00:00Z', source: { source: 'github', url: 'https://github.com/team/private-repo', commit: 'abc123' }, config: { mode: 'static' }, steps: [{ key: 'acquire', status: 'completed' }], latest_review_id: reviewId };
const review = { ...scan, job_id: reviewId, kind: 'review', parent_job_id: scanId, status: 'completed', config: { provider: 'ollama', model: 'local-model' }, latest_review_id: null, steps: [{ key: 'analyst', role: 'Security analyst', status: 'completed' }, { key: 'author', role: 'Patch author', status: 'completed' }, { key: 'reviewer', role: 'Independent reviewer', status: 'completed' }] };
const report: Report = { job_id: scanId, schema_version: '2.0', meta: { repo: { source: 'github', url: 'https://github.com/team/private-repo', commit: 'abc123' }, generated_at: '2026-01-01T10:00:00Z', snapshot: { digest: 'source-digest-123', warnings: ['Submodules were not included'] } }, summary: { critical: 0, high: 1, medium: 0, low: 0 }, files: [{ path: 'app.py', issues: [{ id: 'finding-1', tool: 'semgrep', type: 'SQL injection', message: 'Untrusted input reaches a SQL query', severity: 'high', file: 'app.py', line: 12, rule_id: 'sql-injection', suggestion: 'Use parameterized queries' }] }], coverage: [{ tool: 'semgrep', status: 'partial', files_discovered: 3, files_scanned: 2, files_skipped: 1, errors: ['One file failed to parse'], languages: ['Python'] }] };
const enhanced: Report = { ...report, review_run_id: reviewId, ai_analysis: { status: 'completed', triage: { verdict: 'review_required' }, proposals: [{ id: 'proposal-1', finding_ids: ['finding-1'], related_finding_ids: ['context-finding'], diff: '--- a/app.py\n+++ b/app.py\n- query(user)\n+ query("?", (user,))', explanation: 'Parameterize the input.', status: 'review_accepted', review: { decision: 'review_accepted', comments: ['Review complete; execution was not performed.'] }, checks: { valid_diff: true } }], errors: [] } };

async function mockAPI(page: Page, options: { auth?: boolean; localReady?: boolean; interrupted?: boolean } = {}) {
  let authenticated = !options.auth;
  const currentReview = options.interrupted ? { ...review, status: 'interrupted', error: 'Provider response was interrupted', steps: [{ key: 'finding:finding-1:analyst:0', role: 'Security analyst', status: 'completed', output: { disposition: 'confirmed' }, usage: { effective_model: 'actual-model-snapshot', total_tokens: 123 } }, { key: 'finding:finding-1:reviewer:0', role: 'Independent reviewer', status: 'interrupted', error: { code: 'interrupted', message: 'Explicit retry required' } }] } : { ...review };
  const calls: { path: string; method: string; body: string | null }[] = [];
  await page.route('**/api/backend/**', async (route) => {
    const request = route.request(); const url = new URL(request.url()); const path = url.pathname.replace('/api/backend', '');
    calls.push({ path, method: request.method(), body: request.postData() });
    let body: unknown; let status = 200;
    if (path === '/auth/status') body = { required: Boolean(options.auth), authenticated };
    else if (path === '/auth/login') { authenticated = true; body = { required: true, authenticated: true }; }
    else if (path === '/capabilities') body = options.localReady === false ? { ...capabilities, providers: { ...capabilities.providers, ollama: { available: false, models: [] } } } : capabilities;
    else if (path === '/config/ai') body = request.method() === 'PATCH' ? { ...aiSettings, ...request.postDataJSON() } : aiSettings;
    else if (path === '/projects') body = request.method() === 'POST' ? { id: projectId, name: request.postDataJSON().name, kind: 'zip' } : { items: [{ id: projectId, name: 'Payments service', kind: 'zip' }], total: 1, page: 1, limit: 100 };
    else if (path === `/reports/${scanId}/comparison`) body = { has_baseline: false, items: [], counts: {} };
    else if (path === `/reports/${scanId}/export`) body = { ...report, ai_analysis: undefined };
    else if (path === `/reviews/${reviewId}/export`) body = { ...enhanced, review_run_id: reviewId };
    else if (path === '/analyze-async') { body = { job_id: scanId, status: 'queued' }; status = 202; }
    else if (path === '/jobs') { const items = [scan, review].filter((item) => !url.searchParams.get('status') || item.status === url.searchParams.get('status')); body = { items, page: 1, limit: 20, total: items.length }; }
    else if (path === `/jobs/${scanId}`) body = scan;
    else if (path === `/jobs/${reviewId}`) body = currentReview;
    else if (path === `/jobs/${reviewId}/retry`) { currentReview.status = 'queued'; body = { job_id: reviewId, status: 'queued' }; status = 202; }
    else if (path === `/reviews/${reviewId}`) body = { ...enhanced, review_run_id: reviewId };
    else if (path === '/reports') body = { items: [{ job_id: scanId, repo_url: report.meta.repo.url, summary: report.summary, generated_at: report.meta.generated_at }], total: 1, page: 1, limit: 20 };
    else if (path === `/reports/${scanId}`) body = report;
    else if (path === `/reports/${scanId}/enhanced`) body = enhanced;
    else if (path === `/reports/${scanId}/enhance`) { body = { job_id: reviewId, run_id: reviewId, status: 'queued' }; status = 202; }
    else if (path.startsWith('/events/')) { await route.fulfill({ contentType: 'text/event-stream', body: `id: 1\nevent: update\ndata: ${JSON.stringify({ seq: 1, job_id: scanId, event: 'job.updated', data: { status: 'partial' } })}\n\n` }); return; }
    else { body = { error: { message: 'Unexpected mocked endpoint' } }; status = 404; }
    await route.fulfill({ status, json: body });
  });
  return calls;
}

test('ZIP selection enables a static scan and submits without provider fields', async ({ page }) => {
  const calls = await mockAPI(page); await page.goto('/dashboard');
  await page.getByRole('button', { name: 'ZIP archive' }).click();
  await expect(page.getByRole('button', { name: 'Start scan' })).toBeDisabled();
  await page.getByLabel('ZIP project', { exact: true }).selectOption(projectId);
  await page.getByLabel('Drop a ZIP archive here, or choose a file').setInputFiles({ name: 'source.zip', mimeType: 'application/zip', buffer: Buffer.from('PK-test-archive') });
  await expect(page.getByRole('button', { name: 'Start scan' })).toBeEnabled();
  await page.getByRole('button', { name: 'Start scan' }).click();
  await expect(page).toHaveURL(`/jobs/${scanId}`);
  const submitted = calls.find((call) => call.path === '/analyze-async');
  expect(submitted?.body).toContain('name="mode"'); expect(submitted?.body).toContain('static'); expect(submitted?.body).not.toContain('name="provider"');
});

test('local provider unavailable does not silently choose cloud', async ({ page }) => {
  const calls = await mockAPI(page, { localReady: false }); await page.goto('/dashboard');
  await page.getByRole('radio', { name: /Multi-agent review/ }).check();
  await expect(page.getByLabel('AI provider')).toHaveValue('ollama');
  await expect(page.getByText('Ollama is not ready.', { exact: false })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Start scan' })).toBeDisabled();
  await page.getByLabel('AI provider').selectOption('openai');
  await expect(page.getByText('Selected source snippets are sent to OpenAI.', { exact: false })).toBeVisible();
  await expect(page.getByLabel('Model', { exact: true })).toHaveValue('cloud-model');
  expect(calls.filter((call) => call.method === 'POST')).toHaveLength(0);
});

test('real run status filtering and one shared event subscription', async ({ page }) => {
  const calls = await mockAPI(page); await page.goto('/jobs');
  await page.getByLabel('Filter runs by status').selectOption('partial');
  await expect(page.getByRole('row').filter({ hasText: 'private-repo' })).toHaveCount(1);
  await page.getByRole('link', { name: 'https://github.com/team/private-repo' }).click();
  await expect(page.getByRole('heading', { name: 'Static scan' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Multi-agent review' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Independent reviewer' })).toBeVisible();
  expect(calls.filter((call) => call.path.startsWith('/events/'))).toHaveLength(1);
});

test('report renders source messages, partial coverage and unapplied proposal evidence', async ({ page }) => {
  const calls = await mockAPI(page); await page.goto(`/reports/${scanId}`);
  await expect(page.getByText('Untrusted input reaches a SQL query', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('One file failed to parse', { exact: false })).toBeVisible();
  await expect(page.getByText('source-digest-123', { exact: true })).toBeVisible();
  await expect(page.getByText('Not applied · Not executed', { exact: true })).toBeVisible();
  await expect(page.getByText('Not run', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Download proposal' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'context-finding', exact: true })).toHaveAttribute('href', '#finding-context-finding');
  await page.getByLabel('Report version').selectOption('enhanced');
  const downloaded = page.waitForEvent('download'); await page.getByRole('button', { name: 'Export report', exact: true }).click();
  const file = await downloaded; const content = JSON.parse(readFileSync((await file.path())!, 'utf8'));
  expect(content.ai_analysis.proposals[0].id).toBe('proposal-1');
  expect(calls.filter((call) => call.path.endsWith('/enhance'))).toHaveLength(0);
});

test('password gate hides private source until authenticated', async ({ page }) => {
  const calls = await mockAPI(page, { auth: true }); await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Sign in to your scanner' })).toBeVisible();
  expect(calls.some((call) => call.path === '/jobs')).toBeFalsy();
  await page.getByLabel('Workspace password').fill('test-password');
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Overview', exact: true })).toBeVisible();
  expect(calls.filter((call) => call.body?.includes('test-password')).map((call) => call.path)).toEqual(['/auth/login']);
});

test('exports use server-produced bytes and findings render untrusted markup as text', async ({ page }) => {
  await mockAPI(page);
  const unsafe = { ...report, files: [{ path: 'x.py', issues: [{ ...report.files[0].issues[0], message: '<script>window.injected=true</script>' }] }] };
  await page.route(`**/api/backend/reports/${scanId}`, (route) => route.fulfill({ json: unsafe }));
  await page.route(`**/api/backend/reports/${scanId}/export?*`, (route) => route.fulfill({ contentType: 'text/csv', body: '"Server produced","escaped bytes"\r\n' }));
  await page.goto(`/reports/${scanId}`);
  await expect(page.getByText('<script>window.injected=true</script>', { exact: true }).first()).toBeVisible();
  expect(await page.evaluate(() => 'injected' in window)).toBeFalsy();
  await page.getByLabel('Export format').selectOption('csv');
  const downloading = page.waitForEvent('download'); await page.getByRole('button', { name: 'Export report', exact: true }).click();
  const downloaded = await downloading;
  expect(readFileSync((await downloaded.path())!, 'utf8')).toBe('"Server produced","escaped bytes"\r\n');
});


test('interrupted review exposes saved checkpoint, actual model and explicit retry', async ({ page }) => {
  const calls = await mockAPI(page, { interrupted: true }); await page.goto(`/jobs/${reviewId}`);
  await expect(page.getByText('Completed stage outputs are retained below.', { exact: false })).toBeVisible();
  await expect(page.getByText('actual-model-snapshot', { exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Related source finding →' }).first()).toHaveAttribute('href', `/reports/${scanId}#finding-finding-1`);
  await page.getByText('Stage output', { exact: true }).click();
  await expect(page.getByText('"disposition": "confirmed"', { exact: false })).toBeVisible();
  await page.getByRole('button', { name: 'Retry incomplete stages' }).click();
  await expect(page.getByText('queued', { exact: true })).toBeVisible();
  expect(calls.filter((call) => call.path === `/jobs/${reviewId}/retry` && call.method === 'POST')).toHaveLength(1);
});

test('workspace remains usable on desktop and mobile', async ({ page }, testInfo) => {
  await mockAPI(page); await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'New security scan' })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('desktop.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole('button', { name: 'Start scan' })).toBeEnabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.screenshot({ path: testInfo.outputPath('mobile.png'), fullPage: true });
});


test('selected review exports its saved run instead of the latest review', async ({ page }) => {
  const calls = await mockAPI(page); await page.goto(`/reports/${scanId}?review=${reviewId}`);
  await expect(page.getByText(`review ${reviewId.slice(0, 12)}`, { exact: true })).toBeVisible();
  expect(calls.some((call) => call.path === `/reviews/${reviewId}`)).toBeTruthy();
  expect(calls.some((call) => call.path === `/reports/${scanId}/enhanced`)).toBeFalsy();
  expect(calls.some((call) => call.path === `/reports/${scanId}`)).toBeFalsy();
  const downloaded = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export report', exact: true }).click();
  const saved = await downloaded;
  const content = JSON.parse(readFileSync((await saved.path())!, 'utf8'));
  expect(content.ai_analysis).toBeUndefined();
  expect(content.files[0].issues[0].message).toBe('Untrusted input reaches a SQL query');
});


test('guided setup saves budgets without a model call and accepts exact OpenAI IDs', async ({ page }) => {
  const calls = await mockAPI(page); await page.goto('/setup');
  await expect(page.getByRole('heading', { name: '2. Set your review defaults' })).toBeVisible();
  await page.getByLabel('AI provider').selectOption('openai');
  await page.getByLabel('Model', { exact: true }).fill('my-exact-provider-model');
  await page.getByLabel('Maximum model calls').fill('12');
  await page.getByLabel('Total token budget').fill('20000');
  await page.getByRole('button', { name: 'Save defaults' }).click();
  await expect(page.getByText('Default model and budgets saved.', { exact: false })).toBeVisible();
  const saved = JSON.parse(calls.find((call) => call.path === '/config/ai' && call.method === 'PATCH')!.body!);
  expect(saved.model).toBe('my-exact-provider-model'); expect(saved.max_model_calls).toBe(12); expect(saved.max_total_tokens).toBe(20000);
  expect(calls.filter((call) => call.method === 'POST')).toHaveLength(0);
});

test('provider test is explicit, shows all verification states, and sample scan stays static', async ({ page }) => {
  const calls = await mockAPI(page);
  await page.route('**/api/backend/config/ai/test', (route) => route.fulfill({ status: 202, json: { job_id: 'provider-check', status: 'queued' } }));
  await page.route('**/api/backend/jobs/provider-check', (route) => route.fulfill({ json: { ...scan, job_id: 'provider-check', kind: 'provider_check', status: 'completed', steps: [{ key: 'provider_check', status: 'completed', output: { configured: true, reachable: true, schema_test_passed: true, model: 'local-model' } }] } }));
  await page.goto('/setup');
  await expect(page.getByRole('button', { name: 'Test connection' })).toBeEnabled();
  expect(calls.some((call) => call.path === '/config/ai/test')).toBeFalsy();
  await page.getByRole('button', { name: 'Test connection' }).click();
  await expect(page.getByText('Schema test passed', { exact: true })).toBeVisible();
  await expect(page.getByText('passed', { exact: true })).toHaveCount(3);
  await page.getByRole('button', { name: 'Run sample scan' }).click();
  await expect(page).toHaveURL(`/jobs/${scanId}`);
  const submitted = calls.find((call) => call.path === '/analyze-async')!;
  expect(submitted.body).toContain('name="project_id"'); expect(submitted.body).toContain('security-v1'); expect(submitted.body).not.toContain('name="provider"');
});

test('ZIP project and candidate profile are explicit and persisted in submission', async ({ page }) => {
  const calls = await mockAPI(page); await page.goto('/dashboard');
  await page.getByRole('button', { name: 'ZIP archive' }).click();
  await page.getByLabel('Drop a ZIP archive here, or choose a file').setInputFiles({ name: 'different-name.zip', mimeType: 'application/zip', buffer: Buffer.from('PK-fixture') });
  await expect(page.getByRole('button', { name: 'Start scan' })).toBeDisabled();
  await page.getByLabel('New project name').fill('Payments service');
  await page.getByRole('button', { name: 'Create project', exact: true }).click();
  await expect(page.getByLabel('ZIP project', { exact: true })).toHaveValue(projectId);
  await page.getByLabel('Security rule profile').selectOption('security-v2');
  await page.getByRole('button', { name: 'Start scan' }).click();
  await expect(page).toHaveURL(`/jobs/${scanId}`);
  const submitted = calls.find((call) => call.path === '/analyze-async')!;
  expect(submitted.body).toContain('security-v2'); expect(submitted.body).toContain(projectId);
});

test('human dismissal requires a reason and stale revisions surface a conflict', async ({ page }) => {
  await mockAPI(page); let patched: unknown;
  await page.route(`**/api/backend/projects/${projectId}/findings?*`, (route) => route.fulfill({ json: { items: [{ id: 'logical-1', fingerprint: 'fingerprint', file: 'app.py', rule_id: 'sql', message: 'SQL reaches database', severity: 'high', assessment: { classification: 'resolved', reason: 'Relevant file was successfully checked', stream: 'main', job_id: scanId }, triage: { status: 'open', revision: 3 }, notes: [] }], page: 1, limit: 20, total: 1 } }));
  await page.route(`**/api/backend/projects/${projectId}/findings/logical-1/triage`, (route) => { patched = route.request().postDataJSON(); return route.fulfill({ status: 409, json: { detail: 'Finding changed; refresh and review the latest revision' } }); });
  await page.goto(`/projects?project=${projectId}`);
  await page.getByText('SQL reaches database', { exact: true }).click();
  await expect(page.getByText('Latest scan assessment: resolved', { exact: true })).toBeVisible();
  await expect(page.getByLabel('Finding status')).toHaveValue('open');
  await page.getByLabel('Finding status').selectOption('dismissed');
  await expect(page.getByRole('button', { name: 'Save triage' })).toBeDisabled();
  await page.getByLabel('Dismissal reason (required)').fill('Input is validated by the documented caller');
  await page.getByLabel('Dismissal category').selectOption('false_positive');
  await page.getByRole('button', { name: 'Save triage' }).click();
  await expect(page.getByRole('alert').filter({ hasText: 'Finding changed' })).toBeVisible();
  expect(patched).toEqual({ status: 'dismissed', expected_revision: 3, reason: 'Input is validated by the documented caller', category: 'false_positive' });
});

test('comparison preserves not-assessed state and exports SARIF from the server', async ({ page }) => {
  const calls = await mockAPI(page);
  await page.route(`**/api/backend/reports/${scanId}/comparison?*`, (route) => route.fulfill({ json: { has_baseline: true, status: 'partial', counts: { not_assessed: 1 }, comparability_reasons: ['Parser failure prevents resolution'], items: [{ classification: 'not_assessed', finding: report.files[0].issues[0], reason: 'The affected file did not parse' }] } }));
  await page.goto(`/reports/${scanId}`);
  await expect(page.getByText('Parser failure prevents resolution')).toBeVisible();
  await expect(page.getByText('not assessed', { exact: true })).toBeVisible();
  await page.getByLabel('Export format').selectOption('sarif');
  const download = page.waitForEvent('download'); await page.getByRole('button', { name: 'Export report', exact: true }).click(); await download;
  expect(calls.some((call) => call.path === `/reports/${scanId}/export`)).toBeTruthy();
});

test('combined proposals require review and static validation and reject selected conflicts', async ({ page }) => {
  await mockAPI(page);
  const good = { ...enhanced.ai_analysis!.proposals![0], status: 'reviewed', review: { decision: 'approve' }, validation: { status: 'passed' }, conflicts: ['proposal-2'] };
  const second = { ...good, id: 'proposal-2', conflicts: ['proposal-1'] };
  const failed = { ...good, id: 'proposal-failed', validation: { status: 'failed', errors: ['Syntax check failed'] }, conflicts: [] };
  await page.route(`**/api/backend/reports/${scanId}/enhanced`, (route) => route.fulfill({ json: { ...enhanced, ai_analysis: { status: 'completed', proposals: [good, second, failed] } } }));
  await page.goto(`/reports/${scanId}`);
  await page.getByLabel('Select proposal-1 for combined download', { exact: true }).check();
  await expect(page.getByRole('button', { name: 'Download selected proposals (1)' })).toBeEnabled();
  await page.getByLabel('Select proposal-2 for combined download', { exact: true }).check();
  await expect(page.getByRole('button', { name: 'Download selected proposals (2)' })).toBeDisabled();
  await expect(page.getByLabel('Select proposal-failed for combined download', { exact: false })).toBeDisabled();
});


test('ordinary review explicitly selects multi-agent mode over saved evaluation defaults', async ({ page }) => {
  const calls = await mockAPI(page);
  await page.route('**/api/backend/config/ai', (route) => route.fulfill({ json: { ...aiSettings, workflow_mode: 'single_agent' } }));
  await page.goto(`/reports/${scanId}`);
  await page.getByRole('button', { name: 'Start another review', exact: true }).click();
  await expect(page).toHaveURL(`/jobs/${reviewId}`);
  const submitted = JSON.parse(calls.find((call) => call.path === `/reports/${scanId}/enhance`)!.body!);
  expect(submitted).toEqual({ provider: 'ollama', model: 'local-model', workflow_mode: 'multi_agent' });
});
