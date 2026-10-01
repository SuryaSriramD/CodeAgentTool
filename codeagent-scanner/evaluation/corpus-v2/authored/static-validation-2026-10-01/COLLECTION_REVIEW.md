# Corpus-v2 coverage repair collection — 2026-10-01

**All 204 cases have saved scanner reports: 155 complete and 49 incomplete.**
Complete coverage increased from 126 to 155: 29 previously incomplete cases now
complete, and all 126 previously complete cases remain complete. This is coverage
evidence, not an accuracy measurement or a release-quality result.

[Case results](README.md) · [Summary](summary.json) · [Full journal](state.json) ·
[Original collection](../static-validation-2026-09-25/COLLECTION_REVIEW.md) ·
[Implementation and tests](../../../../../docs/coverage-repair.md)

## Coverage by language

| Language | Original complete | New complete | New incomplete |
| --- | ---: | ---: | ---: |
| bash | 0 | 0 | 12 |
| c | 5 | 11 | 1 |
| cpp | 7 | 12 | 0 |
| csharp | 12 | 12 | 0 |
| fsharp | 12 | 12 | 0 |
| go | 10 | 11 | 1 |
| java | 1 | 10 | 2 |
| javascript | 12 | 12 | 0 |
| kotlin | 5 | 5 | 7 |
| php | 12 | 12 | 0 |
| python | 4 | 4 | 8 |
| ruby | 12 | 12 | 0 |
| rust | 10 | 10 | 2 |
| scala | 12 | 12 | 0 |
| swift | 0 | 0 | 12 |
| typescript | 0 | 8 | 4 |
| visualbasic | 12 | 12 | 0 |

## What changed and what remains unresolved

- Every latest snapshot matches the exact authored file inventory and hashes,
  including all 12 Bash cases under `bin/`. The corpus specifications, security
  rules, and model prompts are unchanged.
- Pinned Semgrep metadata is audited separately from native syntax diagnostics.
  Twenty-nine cases recovered complete coverage without weakening unknown-node
  checks or tuning rules to these examples.
- Four Bash cases retain native syntax diagnostics. Another 45 cases contain
  constructs outside the independently verified AST policy; four of those also
  have extension-count reconciliation gaps. These categories are not proof that
  the sources are invalid or that every rule missed a vulnerability. Their full
  parser/check coverage is unresolved, so their outcomes remain incomplete.
- The 49 incomplete cases retain findings and precise per-file diagnostics.
  They cannot count as clean scans or satisfy the all-language release gate.

The latest server outcomes are **155 completed, 16 partial, and 33 failed**.
All have saved scanner evidence. No latest snapshot has an inventory mismatch.

## Recovery incident and retained attempts

Two original attempts (JavaScript vulnerable-06 and Kotlin safe-01) failed with
HTTP 409 during recovery after an 81-second host maintenance sleep. Their expired
leases were reclaimed while the old scanner requests were still cleaning up.
Both were explicitly retried after reaching terminal states. The JavaScript case
completed; the Kotlin case produced its genuine incomplete parser/check evidence.
The journal retains both failed attempts, giving **206 report artifacts** for
204 cases. Nothing was silently retried or erased.

The subsequent lifecycle correction gives every scanner dispatch a unique UUID
and directs cancellation to that invocation. A regression against the actual
internal ASGI service verifies simultaneous old/new attempts, cancellation
isolation, and stale-owner fencing. Scanner profiles and corpus sources were not
changed by this correction.

## Unapproved-label observations

| Observation | Cases |
| --- | ---: |
| matches_proposed_labels | 119 |
| expected_not_observed | 80 |
| unexpected_findings | 4 |
| missing_and_unexpected | 1 |

These are not false-positive, recall, or fix-quality estimates. All 204 human
reviews remain pending; missing and additional findings require independent
semantic review. No label, source, rule, or prompt was changed to improve these
observations. No model calls, proposals, source execution, builds of submitted
code, or human approvals were produced.

## Frozen identities

Corpus specification set SHA-256: `f9f38c8c54f7ddf4546b97646c2e7128db6e0649af084798e00d4cd8d80bbe1a`.

Collector implementation SHA-256: `98099d8bcf5cf36abb03488264686888c1ea334ef39a83add607624b2ee79f39`.

Source profile SHA-256: `221377c54607dc61fe0f2097c0a4f8f87557847ed2ee877cd743a889a9c82d21`.

Dependency profile SHA-256: `825b4d8e4f90e37819584a9154b18670e4dfe7eb6982164e688fad910cc20d36`.

Each current and prior report hash was verified against the journal. The
original 204-case specification identities and 210 original corpus/history files
were checked unchanged. A final resume reused the same 204 job/report records without new submissions.
The collector correctly exits **2**, because 49 cases remain operationally incomplete. The release remains a **candidate**. Address
remaining parser/AST coverage using independent development controls, then obtain
human corpus approval before the frozen comparative local-model benchmark.
