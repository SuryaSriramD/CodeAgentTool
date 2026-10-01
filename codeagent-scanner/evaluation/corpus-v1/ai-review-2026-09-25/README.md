# Corpus technical review — 25 September 2026

**Recommendation: keep the release candidate status and do not freeze this corpus for the quality benchmark.** All 204 entries received an AI technical review: **146 locally supported, 43 needing clarification, and 15 requiring revision**. These counts assess case-local labels and contracts. They are not human approvals or a measurement of scanner/model accuracy.

[Read all case reviews with source](cases.md) · [CSV register](cases.csv) · [Complete structured review](review.json)

The corpus remains byte-for-byte unchanged and all 204 human approvals remain pending. No source snippets were executed, no model benchmark was run, and no rules or prompts were tuned from this material.

## What prevents approval

### CR-001 — The corpus does not establish 204 independent scenarios (blocker)

204 source-distinct entries form exactly 102 language/scenario vulnerable-safe pairs. The 36 Java/Kotlin/Scala entries repeat six API templates across three languages; the 36 C#/Visual Basic/F# entries do the same. Different identifiers and source hashes do not establish conceptual independence.

**Action:** Retain useful snippets as diagnostic cases, then create a new version with independently conceived contexts/trust boundaries and realistic safe alternatives to meet the agreed 204-independent-case requirement. Record derivation groups and keep each group out of tuning data. Do not lower the target or claim an effective independent sample size from hashes.

Local evidence: [corpus.json](../corpus.json), [ai-review-2026-09-25/jvm-swift.json](jvm-swift.json), [ai-review-2026-09-25/dotnet-rust.json](dotnet-rust.json).

### CR-002 — The source set is too small and context-poor to support the intended fix-quality claim (major)

202 cases contain one file; only the Python SQL pair has two files. Total source length is 1 to 9 lines per case. The corpus largely demonstrates individual sink/configuration choices and seldom supplies a consumer, accepted schema, capacity policy, or meaningful multi-file behavior.

**Action:** Add independently designed cases with source-visible trust boundaries, callers, data contracts and representative legitimate inputs/outputs. Include meaningful multi-file evidence and regression traps, rather than expanding snippets with cosmetic boilerplate. Keep any extra context identical for the two AI modes.

Local evidence: [corpus.json](../corpus.json), [../../benchmark.py:296](../../benchmark.py#L296), [../../benchmark.py:379](../../benchmark.py#L379).

### CR-003 — Remediation constraints leave important legitimate behavior undecided (major)

Eval examples do not define the supported expression grammar/transformation; unrestricted shell APIs do not name the legitimate command set; deserialization examples omit the accepted object schema and migration rules. Several C examples discard their only local result. Two C++ buffer-format cases also need additional bounds/whole-text ground truth.

**Action:** Resolve the per-case questions in cases.md before label approval. Define the intended operation and allowed changes in each vulnerable case, with matching source-visible context. Safe siblings are independently evaluated and are not automatic reference fixes; their behavior differences alone are not scoring defects.

Examples: [javascript-calculator-vulnerable](cases.md#javascript-calculator-vulnerable), [csharp-shell-command-vulnerable](cases.md#csharp-shell-command-vulnerable), [java-session-restore-vulnerable](cases.md#java-session-restore-vulnerable), [c-bounded-copy-vulnerable](cases.md#c-bounded-copy-vulnerable), [cpp-buffer-format-safe](cases.md#cpp-buffer-format-safe).

### CR-004 — Runtime and API assumptions affect the ground truth (major)

The three vulnerable BinaryFormatter cases lack a runtime where deserialization is enabled. Generic SQL helpers do not pin driver/placeholder and input-shape semantics. Swift TLS labels need platform, ATS and client-wiring context; bare digest helpers lack the security-sensitive consumer needed for an exploitability label.

**Action:** Declare compatible runtimes, drivers, framework versions, platform policy and trusted setup. Distinguish unsafe-API/configuration observations from demonstrated exploitable flows; do not infer a runtime from another independently scanned case.

Examples: [csharp-state-formatter-vulnerable](cases.md#csharp-state-formatter-vulnerable), [javascript-account-lookup-safe](cases.md#javascript-account-lookup-safe), [go-order-query-safe](cases.md#go-order-query-safe), [swift-session-challenge-vulnerable](cases.md#swift-session-challenge-vulnerable), [go-checksum-authentication-vulnerable](cases.md#go-checksum-authentication-vulnerable).

Primary references: [learn.microsoft.com: binaryformatter-removal](https://learn.microsoft.com/en-us/dotnet/core/compatibility/serialization/9.0/binaryformatter-removal), [github.com: mysql](https://github.com/mysqljs/mysql#escaping-query-values), [go.dev: sql-injection](https://go.dev/doc/database/sql-injection), [developer.apple.com: performing-manual-server-trust-authentication](https://developer.apple.com/documentation/Foundation/performing-manual-server-trust-authentication).

### CR-005 — A target-family negative label is not necessarily an all-findings clean label (major)

ruby-hostname-command-safe removes shell parsing but still lets GNU getent interpret option-like untrusted input. observe() counts any retained finding on a safe case as a false positive. Consequently a true residual issue can pollute false-positive measurements if safety is reviewed only for the paired family. The positive C++ buffer-format case has a second buffer-capacity weakness omitted from expected findings.

**Action:** Review every negative under the complete frozen scan profile and intended threat model, including residual weaknesses. Add explicit ground-truth scope and expected findings; review unexpected detections instead of automatically treating useful extra findings as incorrect. Preserve the agreed false-positive/recall targets.

Examples: [ruby-hostname-command-safe](cases.md#ruby-hostname-command-safe), [cpp-buffer-format-vulnerable](cases.md#cpp-buffer-format-vulnerable).

Local evidence: [../../benchmark.py:184](../../benchmark.py#L184), [../../benchmark.py:203](../../benchmark.py#L203).

### CR-006 — Human approval is bound only to source, not the reviewed case specification (major)

validate_corpus() compares reviewed_content_sha256 with the files-only hash. Before a new freeze, changing rationale, CWE/family or remediation constraints can leave existing approval valid. A label and its expected-findings list can also change together without affecting that source hash. The later whole-corpus freeze hash detects changes after freezing, but does not prove approval of pre-freeze metadata edits.

**Action:** Add a versioned canonical reviewed-case digest covering source, label, expected findings, rationale, remediation constraints, runtime assumptions, provenance and derivation group. Invalidate approval for changes to any reviewed field, then freeze that approved specification. Keep source hashes separately for snapshots.

Local evidence: [../../benchmark.py:58](../../benchmark.py#L58), [../../benchmark.py:90](../../benchmark.py#L90), [../../benchmark.py:94](../../benchmark.py#L94), [../../benchmark.py:420](../../benchmark.py#L420).

### CR-007 — Confidence intervals need a justified independence unit (major)

The current bootstrap correctly keeps each case's three model repetitions together and pairs the modes. It samples case IDs within language/label buckets, however, without accounting for translated templates across languages. This can overstate precision when those cases have correlated outcomes; no numerical bias or model improvement was measured in this review.

**Action:** First meet the independent-corpus requirement. Predeclare derivation/scenario clusters and use a statistically reviewed resampling design that retains mode pairing and repeated-run clustering; retain within-template dependence wherever derivatives remain. Publish a sensitivity analysis. Pair membership alone does not prove each separately stratified metric interval is invalid.

Local evidence: [../../benchmark.py:465](../../benchmark.py#L465), [../../benchmark.py:470](../../benchmark.py#L470), [../../benchmark.py:476](../../benchmark.py#L476).

## Interpretation matters

A safe case is submitted independently. For example, the C/C++ direct `execl` snippets avoid shell interpretation but replace the caller process; they cannot be assumed to preserve the behavior of a separate `system`/`popen` example. That is a context/migration concern, not proof that every safe label is wrong. The benchmark does not use safe siblings as automatic expected fixes. [POSIX exec semantics](https://pubs.opengroup.org/onlinepubs/007904875/functions/exec.html).

Likewise, an unsafe API/configuration label can be supported even when exploitability depends on omitted wiring. Reviewers should agree on which claim is being scored. This packet preserves those distinctions instead of turning every missing entry point into an invalid case.

## Counts by language

| Language | Supported | Clarify | Revise | Total |
|---|---:|---:|---:|---:|
| python | 10 | 2 | 0 | 12 |
| javascript | 9 | 3 | 0 | 12 |
| typescript | 7 | 5 | 0 | 12 |
| java | 9 | 2 | 1 | 12 |
| go | 8 | 4 | 0 | 12 |
| c | 6 | 6 | 0 | 12 |
| cpp | 8 | 2 | 2 | 12 |
| ruby | 10 | 1 | 1 | 12 |
| php | 11 | 1 | 0 | 12 |
| kotlin | 9 | 2 | 1 | 12 |
| scala | 9 | 2 | 1 | 12 |
| swift | 7 | 2 | 3 | 12 |
| rust | 9 | 3 | 0 | 12 |
| bash | 11 | 1 | 0 | 12 |
| csharp | 8 | 2 | 2 | 12 |
| visualbasic | 8 | 2 | 2 | 12 |
| fsharp | 7 | 3 | 2 | 12 |
| **Total** | **146** | **43** | **15** | **204** |

## Cases requiring revision

| Case | Concrete issue codes |
|---|---|
| [java-session-restore-vulnerable](cases.md#java-session-restore-vulnerable) | UNDEFINED_RESTORATION_CONTRACT, OVERSTATED_GADGET_EVIDENCE |
| [cpp-buffer-format-vulnerable](cases.md#cpp-buffer-format-vulnerable) | EXPECTED_FINDINGS_INCOMPLETE, FULL_TEXT_CAPACITY_CONTRACT |
| [cpp-buffer-format-safe](cases.md#cpp-buffer-format-safe) | SAFE_CODE_CONTRADICTS_FULL_TEXT_CONSTRAINT |
| [ruby-hostname-command-safe](cases.md#ruby-hostname-command-safe) | UNTERMINATED_COMMAND_OPTIONS |
| [kotlin-native-state-vulnerable](cases.md#kotlin-native-state-vulnerable) | UNDEFINED_RESTORATION_CONTRACT |
| [scala-job-state-vulnerable](cases.md#scala-job-state-vulnerable) | UNDEFINED_RESTORATION_CONTRACT |
| [swift-archive-import-vulnerable](cases.md#swift-archive-import-vulnerable) | ARCHIVE_CONTRACT_UNSPECIFIED |
| [swift-archive-file-vulnerable](cases.md#swift-archive-file-vulnerable) | ARCHIVE_CONTRACT_UNSPECIFIED |
| [swift-path-selection-vulnerable](cases.md#swift-path-selection-vulnerable) | DOCUMENT_ID_CONTRACT_MISSING |
| [csharp-shell-command-vulnerable](cases.md#csharp-shell-command-vulnerable) | SHELL_OPERATION_CONTRACT_UNSPECIFIED |
| [csharp-state-formatter-vulnerable](cases.md#csharp-state-formatter-vulnerable) | BINARYFORMATTER_RUNTIME_LABEL, SERIALIZATION_MIGRATION_CONTRACT_UNSPECIFIED |
| [visualbasic-diagnostic-shell-vulnerable](cases.md#visualbasic-diagnostic-shell-vulnerable) | SHELL_OPERATION_CONTRACT_UNSPECIFIED |
| [visualbasic-import-formatter-vulnerable](cases.md#visualbasic-import-formatter-vulnerable) | BINARYFORMATTER_RUNTIME_LABEL, SERIALIZATION_MIGRATION_CONTRACT_UNSPECIFIED |
| [fsharp-support-process-vulnerable](cases.md#fsharp-support-process-vulnerable) | SHELL_OPERATION_CONTRACT_UNSPECIFIED |
| [fsharp-binary-state-vulnerable](cases.md#fsharp-binary-state-vulnerable) | BINARYFORMATTER_RUNTIME_LABEL, SERIALIZATION_MIGRATION_CONTRACT_UNSPECIFIED |

## Path to a reviewable benchmark

1. Create a new corpus version that meets the independence/realism requirements; keep this version as an unchanged audit reference.
2. Resolve the 58 case-local clarification/revision records and review negative cases for all relevant weaknesses. Add explicit runtime, trust-boundary, operation and migration contracts.
3. Bind approval to the complete reviewed specification and predeclare statistically defensible derivation groups. Source-hash uniqueness alone is insufficient.
4. Have the designated independent human reviewer approve the revised labels and constraints. This AI packet can assist that review but cannot sign it off.
5. Freeze the approved inputs, then run the recorded local-model comparisons and blinded proposal review. Keep the existing quality targets unchanged; do not claim improvement before measurements pass them.

## Audit evidence

- Corpus version: `heldout-1.0.0-candidate`.
- Original and post-review file SHA-256: `f04ead225f76197128a356ee83111e17ea8485ba884661ec447c0c8d9306f378`.
- Every corpus ID appears exactly once in the combined review; all 204 source hashes match.
- The JSON review additionally records a hash of each complete case specification excluding its human-review field.
- Per-language balance remains six proposed vulnerable and six proposed safe cases.
- 102 language/scenario pairs; 202 single-file entries and two entries with two files; source length 1–9 lines per entry.
- Four AI review slices were reconciled by the coordinating reviewer. This is not independent human validation.
- Technical conclusions are based on source inspection and selected primary documentation. Parsing, scanner behavior, builds, exploitation and model results were not established by this review.
