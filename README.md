# CodeAgent

CodeAgent scans a GitHub repository or ZIP archive and turns selected security findings into reviewed patch proposals. It is designed for one workstation or a small team sharing one host. Static analysis works without an AI account. Optional multi-agent review supports an explicitly selected OpenAI model or a local Ollama model.

Start the application with Docker Compose:

```sh
docker compose up --build -d
```

Open <http://localhost:3000>. The initial build downloads the pinned scanning tools and the vulnerability advisory database. The default deployment listens only on localhost and needs no password or API credentials. See [Quick start](QUICK_START.md) for provider setup, team access, operating commands, and local development.

On macOS external drives where Docker rejects AppleDouble file attributes, use `python3 scripts/compose.py up --build -d`. It stages clean build contexts and uses the same deployment and data volumes.

## What the application does

1. Creates an immutable source snapshot with a recorded source identity and file hashes.
2. Runs pinned static engines in an isolated scanner service and reports findings alongside actual coverage, failures, and skipped files.
3. Optionally asks a security analyst to triage findings, an author to propose precise edits, an isolated scanner to validate them in a disposable copy, and a separate reviewer to assess the evidence. An author gets at most one revision and revalidation.
4. Shows accepted, rejected, and unresolved proposals with source evidence and downloadable diffs. A failed deterministic check blocks validated status. Source files are never changed, and uploaded repositories are never built or executed.
5. Tracks findings across named ZIP projects and GitHub branch streams, with human decisions, append-only notes, conservative comparisons, saved JSON/SARIF exports, and an API-client CLI for CI.

Jobs, events, reports, and agent checkpoints persist in SQLite and local volumes. Scan and review runs are separate; reviewing an existing report does not repeat static analysis. Cancellation, retry, and rerun have separate meanings. A worker restart preserves completed work, and interrupted model calls require an explicit retry.

## Coverage

The checked-in rulepack covers Python, JavaScript, TypeScript, Java, Kotlin, Scala, Go, C, C++, Ruby, PHP, Swift, Rust, Bash, C#, Visual Basic .NET, and F#. It also includes checks for YAML, JSON, XML, HTML, and Dockerfiles. Semgrep supplies the baseline rules, Bandit adds Python checks, and Roslyn/FSharp.Compiler.Service implement four security checks for each .NET language. Trivy audits supported dependency inventories against an offline advisory database.

Language support means the documented checks have positive and safe-negative regression fixtures; it does not imply comprehensive vulnerability detection. The default `security-v1` profile remains available. The opt-in `security-v2` candidate adds 38 language/family combinations across all 17 languages, with 228 additional positive/negative fixtures. Coverage and dependency-resolution limitations are described in [the rulepack documentation](codeagent-scanner/rules/README.md). A partial scan or an unsupported manifest is visible in the report and must not be interpreted as a clean scan.

## Project map

| Directory | Purpose |
|---|---|
| `codeagent-scanner/api` | HTTP API and isolated scanner RPC |
| `codeagent-scanner/pipeline` | Durable jobs, reports, retention, and orchestration |
| `codeagent-scanner/integration` | Typed analyst/author/reviewer workflow and providers |
| `codeagent-scanner/analyzers`, `rules`, `dotnet-analyzer` | Static engine adapters and owned rules |
| `codeagent-scanner-ui` | Next.js UI, same-origin API proxy, generated API types |
| `codeagent-scanner/tests`, `fixtures` | Current runtime and engine regression tests |
| `codeagent-scanner/evaluation` | Human-gated 204-case corpus and resumable static/single-agent/multi-agent benchmark; separate synthetic metric tests |
| `research/legacy-tests`, `codeagent-scanner/camel`, `codeagent-scanner/codeagent` | Retired tests and historical agent experiments; outside the product runtime |

[Runtime architecture](docs/runtime-architecture.md) explains trust boundaries, state transitions, and extension points. Older setup documents and root agent scripts describe historical prototypes; use this README and the quick start for the supported runtime.

## Verification

CI runs the API/workflow tests, strict UI type checking and build, generated-contract drift checks, browser interaction tests, real pinned-engine fixtures in a container without network access, and an ephemeral Compose CLI scan with SARIF export. Real engine tests fail if a required tool or advisory database is missing.

See [candidate improvements and verification](docs/improvements-vnext.md) for current results and release limits, and [baseline verification](docs/verification.md) for the original implementation. With Compose running, `npm run test:live` in `codeagent-scanner-ui` exercises a real browser ZIP upload, scanner job, report, and export without using a model.

The candidate cannot be promoted on infrastructure tests alone. [Independent corpus review](codeagent-scanner/evaluation/corpus-v1/REVIEW.md) and the [recorded local benchmark](codeagent-scanner/evaluation/README.md) must establish the agreed fix-quality and false-positive improvements without reduced recall. All 204 proposed corpus labels currently await human review. A proposal that passes static validation remains unapplied and runtime-untested.
