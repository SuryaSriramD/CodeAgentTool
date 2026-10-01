# Quick start

## Start a local workspace

Install Docker with Compose support, then run from the repository root:

```sh
docker compose up --build -d
docker compose ps
```

Open <http://localhost:3000>. The API is available at <http://localhost:8000/docs>. The initial build and advisory database download need internet access; subsequent repository scanning runs in a separate service with no external network access. The scanner never restores packages, builds repositories, or executes submitted source code.

Choose **ZIP archive** or enter an HTTPS GitHub repository URL. Leave **Static analysis** selected for a scan without a model. The job page shows progress, events, tool coverage, and cancellation. The report shows findings even when some engines fail. Use **Setup** to inspect scanner readiness, choose an installed local model or exact hosted model ID, save provider and budget defaults, explicitly test structured output, and submit a sample scan. Saving configuration does not contact a model.

The default is a local workspace: both published ports bind to `127.0.0.1`, and no login is required. All data is stored in named Docker volumes. `docker compose down` stops the application and preserves that data. `docker compose down -v` deletes its stored jobs, source snapshots, reports, and advisory cache.

If Docker reports `failed to xattr .../._...: operation not permitted` on a macOS external drive, use the included wrapper from this Git checkout:

```sh
python3 scripts/compose.py up --build -d
```

It copies tracked and unignored source files into temporary build contexts without filesystem metadata, excluding `.env` files and build outputs, then invokes the same canonical Compose configuration with the original `.env`, project name, ports, and named volumes. It creates no separate deployment configuration. AppleDouble metadata is excluded from application snapshots and build contexts, but some Docker/macOS versions inspect those attributes before applying ignore rules. Ordinary Compose commands still manage the resulting stack.

## Enable multi-agent review

Copy the environment example to configure the server:

```sh
cp .env.example .env
```

Select a provider and exact model in **Setup**. The selected provider is the only destination for that review; there is no automatic cloud fallback. You can select multi-agent review for a new scan or start a review from an existing retained static report. This creates a child review run and keeps the original scan report available.

### OpenAI

Set `OPENAI_API_KEY` in `.env` and restart the API and worker:

```sh
docker compose up -d --force-recreate backend worker
```

Choose `openai` and enter an exact model ID available to your account that supports structured output through the Responses API. A configured key does not prove model access. Setup separates configuration, reachability, and the most recent explicit schema-test result. The **Test connection** action creates a queued provider check using synthetic input; for OpenAI this is a billable request. Review sends selected source context and findings to OpenAI and uses your account's API billing. Secrets remain server-side.

### Local Ollama

Run Ollama on the host, make the intended model available yourself, and make its HTTP service reachable from Docker. The Compose default URL is `http://host.docker.internal:11434`; set `OLLAMA_BASE_URL` if your service is elsewhere. Choose `ollama` and the installed completion model in **Setup**. The adapter uses Ollama's native structured JSON schema API. CodeAgent does not download models or fall back to OpenAI when a local model is unavailable. Model schema support and instruction following vary, so malformed or incomplete responses remain visible failures.

### Review limits and outcomes

The default review selects up to 20 findings of high or critical severity, with limits of 60 model calls, 100,000 reported tokens, 15 minutes, bounded 60,000-character source contexts, and 4,000 requested output tokens per call. Choose provider, model, severity, and absolute budgets in Setup or through `PATCH /config/ai`. Limits stop further work; they do not certify provider billing totals after a network interruption.

The workflow is analyst → author → trusted static validation → independent reviewer, with at most one author revision and revalidation. Edits must match immutable source hashes and exact original text. Validation applies anchored edits only to a disposable copy and reruns trusted parsers/scanners. Missing tools, parsing failures, unchanged targets, and new findings cannot receive a passed validation status. The report separates approved, rejected, unresolved, failed-validation and incomplete proposals. Download individual proposals with their status; combined diffs require an explicit compatible, reviewed and statically validated selection. Original files remain unchanged and repository tests do not run.

## Sources and retention

GitHub scans record the resolved commit. For private repositories, set a server-side `GITHUB_TOKEN` with read access to the intended repository; never put credentials in a URL. Submodules and Git LFS objects are not fetched. Select or create an explicitly named project for ZIP uploads; the archive digest identifies a particular source snapshot within that project. Repeated uploads share history only through that project choice. Archive traversal, links, excessive expansion, and unsupported special files are rejected. Default upload limits are 50 MiB compressed, 500 MiB expanded, and 10,000 files.

ZIP paths are preserved as uploaded, so filters such as `src/**` match that archive layout. Only GitHub's transport wrapper directory is removed. UTF-16 originals are retained and supported by the .NET static analyzer; engines that cannot parse them report incomplete coverage. AI context retrieval currently requires UTF-8 text, so reviewing a finding in UTF-16 source produces an explicit context error.

Include/exclude patterns narrow the snapshot; the report records exclusions and actual tool coverage. `.git`, common dependency/build directories, and macOS AppleDouble metadata are excluded. Dependency analysis requires supported resolved inventories: CodeAgent does not install packages to reconstruct them.

Source snapshots are retained for 7 days and reports for 30 days by default (`JOB_RETENTION_DAYS`, `REPORT_RETENTION_DAYS`). Inputs needed by queued, running, or interrupted reviews are protected from cleanup. After a source snapshot expires, its report can remain readable but review/retry that needs the source is unavailable. Keep independent backups if you need longer retention; SQLite and artifacts, including frozen input report versions, live in `runtime-data`, sources in `source-snapshots`.

## Operate the worker and scanner

```sh
docker compose logs -f backend worker scanner
docker compose restart worker
docker compose run --rm advisory-db
```

The last command refreshes the advisory cache using the separate network-enabled provisioner. The scanner reads that cache without network access. Reports record the engine versions and advisory database update time.

**Cancel** requests cancellation and stops subsequent stages; an in-flight external request may already have been processed by its provider. **Retry** resumes a failed/interrupted run with the same source and reuses valid completed checkpoints. A model call interrupted after submission requires this explicit retry and may incur a second charge if the first response was lost. **Rerun** creates a fresh scan job and does not pretend to reuse a review. Progress/events persist across page reloads and process restarts.

## Small-team access

For shared access, set `TEAM_MODE=true`, a strong `WORKSPACE_PASSWORD`, and a random `SESSION_SECRET` of at least 32 characters. For example, generate the secret with `python3 -c 'import secrets; print(secrets.token_hex(32))'`. Configure a TLS reverse proxy to the loopback UI, set `COOKIE_SECURE=true` and `PUBLIC_ORIGIN` to its exact HTTPS origin, and keep the backend port private. For a different local UI port, update `PUBLIC_ORIGIN` to match that origin as well. Restart backend and worker after changing environment settings.

This is a shared workspace login, not individual accounts or tenant isolation. Anyone with access can see retained source/report data and operate jobs. Password login can also be enabled for a local workspace simply by setting `WORKSPACE_PASSWORD` and `SESSION_SECRET`. `PUBLIC_ORIGIN` is shared by the UI proxy and API; recreate frontend, backend, and worker after changing it.

## Development and checks

The backend requires Python 3.12. Install its hash-locked development dependencies and run the current tests:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r codeagent-scanner/requirements-dev.txt
python -m pytest -q codeagent-scanner/tests
python codeagent-scanner/evaluation/compare.py
```

Real engine tests skip when tools are absent unless `CODEAGENT_REQUIRE_REAL_TOOLS=1` is set. The full container gate provisions the DB before testing with no network:

```sh
docker build --target scanner-test -t codeagent-scanner-test codeagent-scanner
docker run --rm -v codeagent-test-advisories:/var/cache/trivy codeagent-scanner-test trivy image --download-db-only --cache-dir /var/cache/trivy --no-progress
docker run --rm --network none --cap-drop ALL --security-opt no-new-privileges -e CODEAGENT_REQUIRE_REAL_TOOLS=1 -v codeagent-test-advisories:/var/cache/trivy:ro codeagent-scanner-test python -m pytest -q tests
```

For UI development use Node.js 22, `npm ci`, and `API_URL=http://localhost:8000 npm run dev` in `codeagent-scanner-ui`. Run `npm run typecheck`, `npm run build`, and `npm test` (install Playwright Chromium with `npx playwright install chromium` first). The API types are generated from the current Python OpenAPI contract: `PYTHON=../.venv/bin/python npm run api:generate` updates them, and `npm run api:check` detects drift.

With Compose running, run `npm run test:live` from `codeagent-scanner-ui` for the real browser ZIP → static scan → report → JSON export check. It creates a named synthetic scan and makes no model calls. Set `CODEAGENT_TEST_URL` for another local origin or `CODEAGENT_TEST_PASSWORD` for a workspace requiring login. Reports and screenshots are written under `test-results/live`. See [implementation verification](docs/verification.md) for recorded checks, counts, and unverified external integrations.

The development Compose overlay mounts backend source and enables API reload:

```sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

Restart the worker after editing Python worker code. Native entry points are `python run.py api`, `python run.py scanner`, and `python run.py worker` from `codeagent-scanner`; native scanner operation requires the pinned engines, compiled trusted .NET analyzer, and provisioned Trivy DB. Compose is the supported isolated deployment.

## Candidate security profile and finding history

`security-v1` remains the production default. Choose `security-v2` explicitly to
exercise the candidate's 38 additional language/family checks across all 17
languages. Its 228 regression fixtures are separate from the proposed evaluation
corpus. See [rule coverage and limitations](codeagent-scanner/rules/README.md).
Fixture success does not promote the candidate or establish improved accuracy.

New submissions pin effective engine/rule/database digests. Reruns preserve
those pins and fail explicitly if that profile is no longer available; submit
a new scan to select the current profile. Historical jobs without effective
pins are labeled unverified. Existing scanner binaries/databases are not
automatically archived for future reproduction.

Projects keep human finding statuses, dismissal reasons and append-only notes.
Compare saved report versions to see new, existing, resolved, not-assessed and
ambiguous findings. Only successfully assessed compatible coverage can establish
resolution; parser failures, exclusions and incompatible advisory profiles do
not make findings disappear. Human dismissals remain independent of AI triage.

## CLI and continuous integration

Use the API-client CLI with the running Compose API. Give local-directory scans
an explicit ZIP project name (or an existing `--project` ID):

```sh
python codeagent-scanner/cli.py --server http://localhost:8000 scan /path/to/source \
  --project-name "My application" --profile security-v1 --severity high \
  --format sarif --output /path/to/artifacts/codeagent.sarif
```

The CLI packages local source with the same credential/build exclusions and
archive limits, submits to the durable worker, waits, and downloads the existing
report. It does not execute source or create another scanner implementation.
For an authenticated workspace, set `CODEAGENT_TOKEN` in the process environment
to the configured shared workspace password; the CLI sends it as a bearer credential.
Do not put it in command arguments or generated reports. `--github https://github.com/owner/repository --ref main` submits a
GitHub source instead; private GitHub credentials stay on the server.

Exit codes are `0` for policy passed, `1` for qualifying findings, `2` for
operational/incomplete/incomparable results and `130` for cancellation. Static
scanning is the default. AI requires `--review --provider ollama --model <id>`
(or an explicitly selected OpenAI model).

`--policy new` compares against the pinned baseline and requires an explicit
`--initialize-baseline` on a first scan. A persistent server keeps project
history; a freshly created CI stack has no prior baseline. Specify
`--baseline-run-id` and `--baseline-hash` when selecting an explicit saved
version. Subcommands also expose `wait`, `cancel`, `compare`, and `export`;
`--help` documents their arguments.

The opt-in [GitHub Actions example](.github/workflows/codeagent-example.yml)
starts an ephemeral Compose API/worker/scanner, scans the checkout statically,
uploads the saved SARIF to GitHub code scanning, and then enforces the captured
policy exit code. It runs only through `workflow_dispatch`; no hosted model or
PR-writing action is configured. GitHub requires code-scanning support for the
repository and `security-events: write` permission. See [GitHub's SARIF upload
documentation](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file).

For measured quality evaluation, follow [the benchmark guide](codeagent-scanner/evaluation/README.md).
The 204 proposed cases need independent human approval before freezing/running.
The code never approves its own benchmark labels, and the release remains a
candidate until actual blinded review and comparative quality gates pass.
