# Source coverage repair — 2026-10-01

This change repairs ingestion and parser-evidence handling identified by the
first corpus-v2 static collection. It does not change security rules, model
prompts, corpus sources, proposed labels, or human approvals.

## Source inventory

Snapshot ingestion and scanner inventories now share source policy version 3.
Source and dependency files under `bin/` are included. Generated directories,
compiled artifacts, credential files, symlinks, binary-content checks, and archive
limits remain excluded or enforced. Existing immutable snapshots are not rewritten.
The source and dependency profile digests include the ingestion implementation.

## Native parser evidence

Semgrep 1.178.0's `untranslated_node_count` counts generic AST extension nodes and
raw trees; it is not a syntax-error count. Its own interface describes the count
as a shallow estimate that needs careful interpretation. The original adapter
treated every nonzero count as a parse failure and discarded the distinction.

The repaired adapter validates the native parser's per-file statistics and keeps
syntax errors incomplete. For nonzero translation counts it obtains the generic
AST from the same trusted parser. Only independently verified metadata forms are
eligible for a completed outcome: JavaScript/TypeScript exports, C/C++ sized type
metadata, Java declared exception metadata, and Go struct tags. The policy is
specific to the pinned engine, validates payload shapes, examines nested nodes,
and reconciles the count. Unknown or executable extension nodes and raw trees
remain incomplete. An allowlisted wrapper cannot conceal an unsupported child.

Each file retains compact parser diagnostics in its report. A successful native
parse is still insufficient by itself: the scanner must also report that it
checked the file without a corresponding error. Parser subprocesses share the
analyzer deadline and cancellation handling. The source profile hashes the
parser-evidence policy, adapters, and proposal-validation implementation.

Primary implementation references, pinned to Semgrep 1.178.0:

- [AST statistics counting](https://github.com/semgrep/semgrep/blob/v1.178.0/src/parsing/tests/AST_stat.ml#L64-L74)
- [Statistics interpretation caveat](https://github.com/semgrep/semgrep/blob/v1.178.0/interfaces/Parsing_stats.atd#L41-L50)
- [Intermediate-language translation of unsupported expressions](https://github.com/semgrep/semgrep/blob/v1.178.0/src/analyzing/AST_to_IL.ml#L1200-L1212)

## Proposal validation

Both the original and edited disposable sources must have unique, successful
per-file evidence from every selected scanner. Inventories, counts, scanned
paths, and parser diagnostics must agree. Missing, duplicated, contradictory,
or incomplete coverage cannot pass because of an aggregate success flag.
Edited and targeted source paths remain required even if an inventory exclusion
would otherwise omit them. Validation checkpoints include the trusted validator
implementation identity so an older cached success cannot bypass these checks.
Analyst and author prompts remain unchanged. Proposals remain unapplied and
runtime-untested.

## Evidence preservation

The [original static collection](../codeagent-scanner/evaluation/corpus-v2/authored/static-validation-2026-09-25/COLLECTION_REVIEW.md)
remains historical evidence: 126 complete and 78 incomplete cases. A fresh
collection uses a separate directory and records the new implementation and
profile identities. Incomplete results remain visible and cannot count as clean
scans. No parser or rule exception is derived from the held-out candidate cases.

Corpus labels and conceptual independence still require independent human
review. Static coverage checks alone do not satisfy the comparative model-quality
release gate.

## Regression verification

The final complete backend suite passed **815 tests with zero failures or skips**
in 65.28 seconds, with the pinned actual scanners required, a read-only source
mount, and network access disabled. One existing Starlette/httpx deprecation
warning remains. This includes the original rule/dependency fixtures plus
ingestion/CLI regressions, parser-statistics and AST-audit boundaries, independent
real-engine metadata/taint/syntax controls, proposal-coverage checks, profile
invalidation, and validation-checkpoint reuse/invalidation.

A host maintenance sleep during collection exposed an additional lifecycle race:
expired leases were reclaimed while previous scanner requests still occupied
reservations under the same durable job ID. Remote scans now use an independent
UUID for each invocation and cancel that invocation only. An actual ASGI/SQLite
regression verifies overlapping recovered attempts, cancellation isolation, and
stale-owner fencing. Worker lease recovery and uncertain model-call handling are
unchanged. The final API/worker images include this correction.

The locked Compose API, worker, and scanner images were rebuilt. All three
services became healthy; the frontend remains on its existing image. Deployment
preserved the runtime and source volumes, prior reports, and advisory database.
The prior images are retained as `codeagent-api:coverage-before-20261001` and
`codeagent-scanner:coverage-before-20261001`.

## Recollected corpus

The [new collection](../codeagent-scanner/evaluation/corpus-v2/authored/static-validation-2026-10-01/COLLECTION_REVIEW.md)
contains all **204** cases: **155 complete, 49 incomplete**, compared with the
original 126 complete and 78 incomplete. Twenty-nine cases recovered complete
coverage; none of the original complete cases regressed. Every latest snapshot
matches the authored source inventory and hashes. Both failed recovery attempts
are retained alongside their explicit retries, for 206 report artifacts.

The remaining cases need investigation: four have native syntax diagnostics,
45 contain constructs outside the verified AST policy, and four of those 45 also
have extension-count reconciliation gaps. These are conservative coverage limits,
not proof that every source is invalid. The collector exits 2 and the all-language
release gate remains unmet. Labels are unapproved; no model calls or human
approvals were created.
