# Baseline implementation verification — 2026-09-25

This records the initial product baseline. See [candidate improvement verification](improvements-vnext.md) for the subsequent rules, validation, history, setup, evaluation, and CI work.

The subsequent [coverage and recovery repair](coverage-repair.md) passed **815
backend tests** and recollected the unchanged 204-case candidate corpus: **155
complete, 49 incomplete**. Its remaining limitations and preserved attempts are
documented separately from these historical baseline results.

These are implementation and integration checks, not a claim of comprehensive
vulnerability detection or a measured advantage from using multiple agents.

The final Linux scanner-test container passed **all 168 tests, with zero skips**,
in 127.83 seconds with `--network none` and
`CODEAGENT_REQUIRE_REAL_TOOLS=1`. This combines the 98 application checks and
70 real-engine cases described below.

## Application and recovery

The current runtime, workflow, ingestion-boundary, and run-identity suites passed
**98 tests** with the hash-locked Python development environment. They exercise
archive limits and containment, token handling, shared-workspace authentication,
transactional queue limits, unique claim tokens, cancellation, restart recovery,
completed-step reuse, frozen report versions, event replay, provider contracts,
budgets, bounded context retrieval, reviewer objections, and credential masking.

The production Compose stack was built and started on this machine. Its API,
worker, isolated scanner, and frontend health checks passed. Actual operations
verified a static ZIP scan, public GitHub commit resolution, worker restart during
analysis with a completed analyzer reused, and cancellation without publishing a
completed report. Private GitHub access and expired-token behavior were tested
with controlled HTTP responses; no live private-repository token was supplied.

The scanner was checked as a nonroot process with a read-only source mount and
root filesystem, no application credentials or runtime database, dropped Linux
capabilities, and blocked external network access. Advisory data is provisioned
separately. The metadata-free Compose wrapper supports this macOS external-drive
workspace; it preserves frontend routes, required lockfiles, and readable file
modes while excluding credentials, runtime data, links, and generated files.

## Scanner fixtures

The pinned engine suite passed **70 tests**. Positive and safe-negative fixtures
cover all 17 advertised source languages and five configuration groups. .NET
fixtures cover all four implemented checks in C#, Visual Basic, and F#, including
aliases, local receivers, shadowed identifiers, and UTF-16 LE/BE source. XML that
the engine cannot parse is explicitly incomplete.

Twenty dependency formats across eleven ecosystems have actual offline Trivy
inventory and vulnerable/patched fixture checks. Tests also cover nested inputs,
malformed locks, missing engines, parser failures, process-group cancellation,
and timeouts. Binary Bun locks and npm-shrinkwrap inputs are explicitly unresolved.
The owned rulepack is intentionally small; see the exact supported checks and
limitations in [the rulepack documentation](../codeagent-scanner/rules/README.md).

## Browser and provider checks

The dashboard passed strict TypeScript checking, the production Next.js build,
OpenAPI contract drift checking, and **12 Playwright tests**. The browser tests
cover source selection, real run states, provider selection, interrupted-review
retry, source coverage, proposals, selected-review exports, authentication,
escaping, responsive layouts, and the production proxy's origin checks.

A separate live browser acceptance check uploaded a synthetic ZIP through the
running Compose frontend, watched its job, opened nine actual scanner findings,
and downloaded the existing JSON report without starting AI review. Reproduce it
after starting Compose with `npm run test:live` in `codeagent-scanner-ui`.
It leaves a clearly named synthetic scan in the workspace and writes its report
and screenshot under the ignored `test-results/live` directory. Set
`CODEAGENT_TEST_URL` for another local origin; an authenticated workspace can use
`CODEAGENT_TEST_PASSWORD` from the environment.

A live local `gemma3:4b` check produced validated analyst, author, and reviewer
handoffs. The reviewer requested a revision; an invalid revision response produced
a partial result with the prior proposal retained. It made four model calls in
50.51 seconds, changed no source, and used the local Ollama adapter. The later
correction that retains token usage from invalid provider responses is covered
by deterministic provider tests. This single synthetic run is not a quality
benchmark or a guarantee that the same model will complete every review.

A second live check used the final Compose API and worker with a deliberately
small five-call budget. `gemma3:4b` completed five validated calls, including an
author revision, in 123.18 seconds and reported 5,797 tokens. Additional context
would have required another call, so the persisted result remained partial with
one unresolved proposal and an explicit budget error. Duplicate submissions
returned the same review run. The review retained its frozen input version, and
the original static report was unchanged. This verifies persistence and bounded
failure handling; it is not an accepted or tested fix.

OpenAI success, refusal, malformed output, interruption, and usage handling have
contract tests; no live OpenAI credentials were supplied. The evaluation harness
accepts recorded observations but its bundled comparison is explicitly synthetic.
A reviewed real-world corpus and measured static/single-agent/multi-agent
comparison remain necessary before making accuracy or proposal-quality claims.

## Reproduce the checks

Use the commands in [Quick start](../QUICK_START.md). For the full engine gate,
provision the advisory database first and run the scanner-test container with
`--network none` and `CODEAGENT_REQUIRE_REAL_TOOLS=1`; missing tools must fail the
gate. The CI workflow uses this mode. Ordinary Python unit runs may skip the real
engine cases when the pinned executables or advisory database are absent.

## Corpus approval integrity and v2 preparation — 2026-09-25

The focused evaluation suites passed **79 tests** after introducing review
protocol 2.0 and the corpus-v2 planning register:

```sh
python -m pytest codeagent-scanner/tests/test_evaluation_v3.py \
  codeagent-scanner/tests/test_corpus_review_integrity.py \
  codeagent-scanner/tests/test_corpus_replacement_register.py -q
python3 codeagent-scanner/evaluation/replacement_register.py --check
```

These checks cover changes to labels, expected findings, rationale, constraints,
runtime assumptions, provenance, derivation metadata and future semantic fields;
legacy approval compatibility; rejection before API access; unsigned review
packets; preservation of existing human work; and deterministic register views.
They use synthetic approval records only in test memory/temporary directories.

The live offline audit reported **0 valid human approvals and 204 pending
reviews**. The register checker verified **204 planned slots**, including
**58 priority briefs** (15 revisions and 43 clarifications), with **0 authored
replacements and 0 approvals**. All 204 slots require independent authoring.
The original corpus remains unchanged at SHA-256
`f04ead225f76197128a356ee83111e17ea8485ba884661ec447c0c8d9306f378`.

This is verification of review infrastructure and preparation, not a new scanner,
browser or model-quality benchmark. No model calls or human sign-offs were made.
The release remains a candidate; independent corpus authoring, human review,
reviewed statistical assumptions and measured comparative quality gates remain
outstanding. See the [replacement register](../codeagent-scanner/evaluation/corpus-v2/README.md)
and [approval workflow](../codeagent-scanner/evaluation/README.md).

## Corpus-v2 authoring and static-evidence tooling — 2026-09-25

The evaluation, approval-integrity, planning-register and new candidate-authoring
suites passed **120 tests** together:

```sh
python -m pytest codeagent-scanner/tests/test_evaluation_v3.py \
  codeagent-scanner/tests/test_corpus_review_integrity.py \
  codeagent-scanner/tests/test_corpus_replacement_register.py \
  codeagent-scanner/tests/test_corpus_authoring_v2.py -q
```

The 40 new authoring-tool checks cover candidate contracts and source containment, duplicate
source and invalid finding anchors, preservation of human review notes,
source/profile/report integrity, incomplete parser/scanner evidence, uncertain
submission outcomes, reuse after restart, cancellation and exclusive collection
locks, preservation of edited review sheets, safe Markdown fences and invalidation
after collector implementation changes. An additional evaluation test rejects
unresolved corpus-wide review concerns and requires fresh case approvals after
human resolutions change corpus context. Synthetic inputs exist only in infrastructure tests; they are not corpus
cases or benchmark observations.

The [authored candidate packet](../codeagent-scanner/evaluation/corpus-v2/authored/README.md)
is separate from the immutable planning register. Its static collector submits
source-only ZIPs using `mode=static` and the explicit `security-v2` profile through
the existing API and worker. It never requests AI analysis, executes case code,
installs case dependencies, builds repositories or runs case tests. Actual
operational/parser results and proposed-label observations are retained in the
[static evidence journal](../codeagent-scanner/evaluation/corpus-v2/authored/static-validation-2026-09-25/README.md).

These tests and scanner observations create no human approvals and make no
model-quality or conceptual-independence claim. All original comparative-quality
release gates remain in force.

The final authored packet contains **204 cases across 17 languages**, balanced
102/102 by proposed label, with **54 multi-file cases and 3,198 source lines**.
The offline approval audit reports **0 valid approvals, 204 pending reviews and
0 stale/invalid approvals**. Original v1 bytes and the historical planning
register still pass their integrity checks.

The live API/worker collection recorded **204 separate static jobs** using the
pinned `security-v2` profile. **126 have complete reported coverage; 78 are
incomplete** (12 Bash cases excluded under `bin/`, plus 66 native parser/AST
coverage failures). Server statuses are 126 completed, 26 partial and 52 failed.
The collector exits **2** for incomplete evidence rather than reporting success.
All 204 saved report hashes were verified, and a subsequent resume reused those
same records. No AI-review jobs, source execution, builds or dependency installs
were initiated by the collector.

Full results, per-language counts, unapproved-label observations and diagnostic
limitations are in the [collection review](../codeagent-scanner/evaluation/corpus-v2/authored/static-validation-2026-09-25/COLLECTION_REVIEW.md).
These are actual scanner observations, not accuracy measurements or a completed
comparative benchmark. In particular, missing findings were retained; labels,
source paths and rules were not changed to make this collection pass.
