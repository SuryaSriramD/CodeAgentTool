# Corpus-v2 static collection review — 2026-09-25

**All 204 static jobs are recorded. 126 have complete reported parser/check coverage; 78 are incomplete.** The collector exits with code 2 because operational evidence is incomplete. Collection itself finished. All labels and conceptual-independence judgments remain pending human review.

[Per-case reports and errors](README.md) · [Summary JSON](summary.json) · [Complete journal](state.json) · [Human review packet](../README.md)

## Coverage by language

| Language | Complete | Incomplete |
| --- | ---: | ---: |
| bash | 0 | 12 |
| c | 5 | 7 |
| cpp | 7 | 5 |
| csharp | 12 | 0 |
| fsharp | 12 | 0 |
| go | 10 | 2 |
| java | 1 | 11 |
| javascript | 12 | 0 |
| kotlin | 5 | 7 |
| php | 12 | 0 |
| python | 4 | 8 |
| ruby | 12 | 0 |
| rust | 10 | 2 |
| scala | 12 | 0 |
| swift | 0 | 12 |
| typescript | 0 | 12 |
| visualbasic | 12 | 0 |

Server job states were **126 completed, 26 partial, and 52 failed**. The 78 non-complete jobs remain operationally incomplete in the collector; recorded findings from those jobs are retained but do not establish full coverage.

## What blocked complete coverage

- **12 Bash cases:** the current ingestion policy excludes the `bin/` directory containing their scripts. Their scanned source inventory differs from the authored snapshot, and no source check completed. These are not clean scans.
- **66 cases:** Semgrep 1.178.0 reported that one or more source files could not be fully parsed/translated. They span C, C++, Go, Java, Kotlin, Python, Rust, Swift and TypeScript. The journal retains the affected file paths and incomplete outcomes. It records no missing-engine, timeout or scanner-crash diagnostic as the cause of these results.
- The saved native-parser messages do not distinguish syntax errors from AST translation limitations. Do not infer that every affected source file is invalid.

Read-only source inspection found feature correlations worth investigating: the 12 incomplete C/C++ cases use standard `unsigned` declarations/casts; the two incomplete Go cases have ordinary struct tags; most affected Java files have `throws` clauses, with another using `String.class`; most affected Kotlin files have generic types. These are hypotheses from source/report comparison, not proven root causes or a compiler/typecheck result. No case was executed or built, and no scanner checks were relaxed.

## Proposed-label observations

| Observation | All 204 cases | Only 126 operationally complete cases |
| --- | ---: | ---: |
| matches_proposed_labels | 118 | 70 |
| expected_not_observed | 81 | 51 |
| unexpected_findings | 4 | 4 |
| missing_and_unexpected | 1 | 1 |

These are **not accuracy, false-positive or recall estimates**: the labels are unapproved. Agreement from an incomplete safe-case scan cannot establish a correct negative. Matching uses the proposed family/CWE, path and optional source span. A mismatch may reflect a real detection miss, an incorrect proposed label/anchor, or additional findings needing semantic review. No case was relabeled to improve these counts.

## Evidence and next steps

1. Investigate excluded source directories and native parser/AST coverage using separate development controls and detailed trusted-tool diagnostics. Preserve these original observations. Do not rename held-out files, weaken parser checks or tune rules/prompts to make this candidate pass.
2. Independently review every complete case specification and the corpus-level review concerns, including conceptual independence, runtime assumptions, all expected findings and acceptable fixes. Resolve semantic changes in a new version and recollect evidence as needed.
3. Once coverage and human approval gates are satisfied, freeze the model, prompts, profiles and configuration before the comparative local-model evaluation. No static-only observation here satisfies the multi-agent quality gate.

All 204 human reviews remain pending. The collector requested **zero model calls** and produced **zero human approvals**. Proposals, runtime tests and comparative model measurements were not part of this run. The release remains a **candidate**.

Corpus specification-set SHA-256: `f9f38c8c54f7ddf4546b97646c2e7128db6e0649af084798e00d4cd8d80bbe1a`.

Collector implementation SHA-256: `d0f13be4d657b6559d7fbcf8798db0cb7f598f303ef6e1604f5f5e9271453a2b`.

Source profile digest: `addb5891684c529093e5e3dbb181becb30ba3db4909989a95666609a2fbd076e`.

Dependency profile digest: `b2a78d8167fb4b467bc3674bccf022ff4ed6923e17e86ffa68b5921f4312644b`.

Each saved report is bound to its persisted job and report version. `report_sha256` is SHA-256 of canonical JSON (sorted keys, compact separators, UTF-8 with non-ASCII preserved); source hashes and generated review-artifact hashes are recorded separately. Resuming the collection reused the same 204 job/report records without submitting new scans.
