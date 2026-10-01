# CodeAgent security workspace

The Next.js UI provides static scans, explicit OpenAI or Ollama review selection, durable run history, analyzer coverage, source findings, and reviewed patch proposals. Proposals are never applied or executed. Trusted parsers and scanners can validate disposable proposal copies. Repository builds and runtime tests remain unexecuted.

## Start locally

Use Node.js 22 and an installed backend environment. From this directory:

```sh
npm ci
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. `API_URL` is a **server-only** upstream address, defaulting to `http://127.0.0.1:8000`. In Compose use `http://backend:8080`. The browser calls the same-origin `/api/backend` proxy; no public API base URL or browser-stored credentials are required.

Start the backend API and worker before submitting a scan. The Setup page shows analyzer availability and advisory freshness, saves provider/model defaults and budgets, starts explicit synthetic connection tests through the worker, and offers a bundled static sample. Static analysis does not need AI credentials. OpenAI keys, GitHub tokens, and local-model configuration belong on the backend. Selecting Ollama never falls back to OpenAI or downloads a model.

A workspace password configured on the backend enables the login screen. Without authentication, keep the workspace bound to localhost. The proxy forwards the HTTP-only session cookie and rejects browser writes outside `PUBLIC_ORIGIN`, a comma-separated list defaulting to `http://localhost:3000,http://127.0.0.1:3000`. Set this to the actual public UI origins when using another host or port; the internal container address is not the browser origin.

## What the UI reports

- ZIP uploads select or create a named project; GitHub scans group by repository identity and branch. Projects retain human triage, required dismissal reasons/categories, append-only notes, and decision history.
- New scans default to stable `security-v1`. Candidate `security-v2` is explicitly selectable while its release gates are pending.
- Scan, review, and provider connection checks are separate runs. The Runs page includes queued, partial, failed, canceled, and interrupted runs.
- Completed agent checkpoints remain visible when later stages fail. Retry is explicit; completed matching checkpoints can be reused by the worker.
- Reports show immutable source identity and per-analyzer discovered, checked, and skipped file counts. Zero findings do not establish complete coverage.
- Findings retain tool messages, rules, source locations, and IDs; proposal and agent-stage links point back to those findings.
- Per-stage usage shows the actual returned model when available. Requested settings remain visible in the run record.
- Baseline comparisons show new, existing, resolved, not-assessed, and ambiguous findings. Incomplete coverage never establishes resolution.
- Export downloads already-saved report data from the server in JSON, SARIF, CSV, Markdown, or HTML. Export never launches AI analysis. HTML output is escaped; CSV cells guard against formula execution.
- Proposal panels separate independent review, deterministic static validation, and unexecuted runtime tests. Individual downloads preserve their status; combined downloads require explicitly selected, accepted, statically validated, compatible proposals.

## Verification

```sh
npm run typecheck
npm run build
npx playwright install --with-deps chromium
npm test
npm audit
```

Playwright starts a test UI at `127.0.0.1:3107`. Tests mock backend responses and make no paid model calls or model downloads. On macOS, an installed Google Chrome is used when available. Tests cover source upload, provider choice, login, run status, SSE/session proxying, partial results, explicit retry, server exports, setup defaults and explicit connection tests, named ZIP projects, candidate profile selection, stale triage revisions, incomplete comparison evidence, proposal eligibility/conflicts, and responsive layouts. Production build and tests should run sequentially because both Next processes use `.next`.

`GET /api/health` checks UI liveness. Backend/worker readiness is available through `GET /api/backend/capabilities`.

## API type generation

The checked-in `lib/generated/api.d.ts` is generated from the backend OpenAPI document without starting a server. Install backend dependencies first, then run:

```sh
PYTHON=/path/to/backend-venv/bin/python npm run api:generate
PYTHON=/path/to/backend-venv/bin/python npm run api:check
```

`api:check` fails when public API schemas drift. `BACKEND_DIR` can override the default sibling `../codeagent-scanner` location. Core run, finding, and submission types use the generated contracts; view-specific projections describe the report's dynamic metadata.

Against an already running workspace, `npm run test:live` uploads the bundled synthetic ZIP into a new named project, waits for its report, and verifies server-side JSON download. It does not request AI review. Set `CODEAGENT_TEST_URL` and `CODEAGENT_TEST_PASSWORD` when needed. Artifacts are written to ignored `test-results/live`.
