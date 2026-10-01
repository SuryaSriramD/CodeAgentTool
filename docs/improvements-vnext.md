# Candidate improvements and verification — 2026-09-25

CodeAgent now includes the six improvement areas and SARIF/CI integration. The
`security-v2` profile remains an explicit **release candidate**; `security-v1`
remains the default. Infrastructure checks cannot promote it without the agreed
independent quality benchmark.

## Implemented workflow

| Area | Delivered behavior |
|---|---|
| Detection | 38 additional language/family combinations across all 17 source languages, 228 positive/negative fixtures, versioned owned profiles, scoped .NET tracking, effective digests and per-file outcomes. Existing configuration/dependency gates remain. |
| Proposal validation | Anchored edits in one disposable scanner workspace; syntax and before/after checks; dependency analysis when relevant; a 120-second ceiling within the review deadline; cancellation and cleanup. Failed or incomplete validation cannot be overridden by a model. |
| Context and agents | Cached bounded lexical index, evidence-first retrieval, groups of at most five with one triage decision per ID, independent reviewer conversations, one revision, model/profile/prompt-aware checkpoints. |
| Setup | Persisted provider/model/budget controls, completion-capable local models, exact OpenAI IDs, explicit worker-backed synthetic connection checks, separate configuration/reachability/schema states, advisory freshness, and a static sample scan. |
| History | Named ZIP projects, canonical GitHub repository/branch identity, preserved occurrence IDs, separate logical IDs/fingerprints, conservative baselines and comparisons, optimistic human triage and append-only notes. |
| CI and exports | Saved-version JSON/SARIF and document exports, official SARIF 2.1.0 schema checks, explicit compatible validated-proposal downloads, API-client CLI, severity/new-finding policies, and an opt-in GitHub Actions example. |
| Evaluation | Separate 204-case proposed held-out corpus, human approval before freeze, API-driven resumable collection, equal single-/multi-agent budgets and validation, blinded review sheets, and paired quality metrics. |

Scanner results describe implemented checks, not universal vulnerability
detection. Lexical context matches are candidates, not cross-file proofs.
Proposals remain `applied=false` and runtime-untested. Repositories are never
built, dependencies are never installed, and repository tests are never run.

The pinned Semgrep generic AST reports an untranslated export directive for
some valid JavaScript module syntax, including `export function`. These files
remain incomplete coverage even when the engine emits findings. That guard is
preserved; see [parser limitations](../codeagent-scanner/rules/README.md). CI
infrastructure acceptance uses supported plain-function syntax and does not
establish complete coverage of every language construct.

Submissions pin effective source/dependency profiles. Reruns retain those pins;
if the matching engine/rules/database are unavailable, the job fails with an
actionable error instead of silently changing the profile. Historical jobs
without pins are labeled unverified. Archived scanner binaries and advisory
databases are not automatically downloaded or retained. Source comparisons are
separate from dependency database identity; advisory age alone is not identity.

## Verification

The final Linux scanner-test container passed **539 tests with zero skips** in
416.84 seconds, with network access disabled, a read-only advisory database and
`CODEAGENT_REQUIRE_REAL_TOOLS=1`. This retains the original 168 checks and includes
all 228 new rule fixtures. The additional checks cover model identity, validation
handoffs, project matching, reconfirmation, optimistic triage, baseline retention,
CLI policies, provider checks, export consistency, official SARIF schema
validation, evaluation gates, and version-probe process cleanup. One upstream
Starlette/httpx deprecation warning remains; no test failed.

The frontend passed **19 Playwright tests**, strict TypeScript, generated-contract
drift checking and the production build. Targeted reruns covered the final
textarea/history presentation changes. A live desktop/mobile browser flow saved
and reloaded settings, explicitly tested local Gemma structured output, completed
a named-project candidate ZIP scan with nine findings, recorded triage and a
note, and downloaded JSON/SARIF. The actual SARIF conformed to the official schema.
Original AI defaults were restored afterward; no default model was silently
selected. The live synthetic provider check completed in 17.486 seconds with
45 reported tokens. Final visual checks found no overflow or page errors.

The final API, worker, isolated scanner and frontend are healthy, and all 11
pre-upgrade jobs remain accessible. The version-probe timeout/process leak found
during verification was fixed and regression tested. Readiness returned all four
pinned engines in 0.325 seconds in the final check. A new candidate CLI scan
recorded source/dependency pins exactly matching its saved report.

A separate fresh Compose project, new volumes and no provider credentials passed
the actual CI workflow: vulnerable static scan exit **1**, clean follow-up with
one evidence-based resolution exit **0**, first new-findings policy without
initialization exit **2**, and explicit baseline initialization exit **0**. All
four saved SARIF exports passed the schema. There were no model requests; all
ephemeral containers and volumes were removed, preserving the main workspace.
The separate JavaScript export-syntax probe correctly produced incomplete
coverage and exit **2**; its limitation was not suppressed to pass CI.

The original implementation's historical checks remain in
[baseline verification](verification.md).

A live local `gemma3:4b` development check used two grouped findings and the
trusted native scanners. Both triage IDs were validated. Static validation
detected a newly introduced Bandit finding, and the independent reviewer
requested revision. A 180-second deadline interrupted a later call, preserving
the unresolved proposal and completed checkpoints without modifying source.
The run recorded five dispatched model calls and 13,486 known tokens;
`usage_complete=false` because the interrupted call's actual usage was unknown.
An earlier malformed grouped response was rejected without inventing a fix.
These are development-fixture observations, not held-out quality measurements
or accepted fixes. No live OpenAI request was made.

## Human review and promotion

All **204 proposed corpus labels remain pending independent human review**.
Use the [review register](../codeagent-scanner/evaluation/corpus-v1/REVIEW.md) and
[editable CSV](../codeagent-scanner/evaluation/corpus-v1/review-register.csv) to
review source semantics, labels, remediation constraints, provenance and case
independence. Distinct hashes do not prove independent scenarios. The tool does
not approve its own benchmark labels.

After approval, follow the [benchmark guide](../codeagent-scanner/evaluation/README.md)
to freeze the exact corpus/model/prompts/profiles and run three repetitions of
both AI modes against the same static inputs. The gate requires at least a
10-percentage-point increase in independently accepted, statically validated
proposals, at least a 20% relative false-positive reduction, no lower recall,
and paired confidence intervals establishing improvement beyond sampling noise.
A zero-false-positive single-agent baseline is inconclusive for the reduction
comparison. Missing, failed, invalid, unresolved and timed-out proposals count
as unsuccessful; abstention retains original static findings.

Publish actual latency, reported tokens, incomplete usage, failures, model
configuration and quality results even if the candidate fails. There is no
relative cost ceiling, and the absolute budgets remain enforced. The candidate
has **not** passed this comparative quality gate and makes no superiority claim.
