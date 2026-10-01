# Authored corpus-v2 candidates

This is the candidate authoring and review packet for `heldout-2.0.0-candidate`. Every case is AI-authored and awaits independent human review. Labels, runtime assumptions, remediation contracts and conceptual independence are proposed, not established ground truth. The release remains a candidate.

The assembled packet contains **204 cases across 17 languages**, with **102 proposed vulnerable and 102 proposed safe labels**, **54 multi-file cases**, and **3,198 source lines**. These are authoring counts, not approved independent observations.

[Full candidate](corpus.json) · [Authoring register](authoring-register.csv) · [Unsigned review manifest](unsigned-review-manifest.json) · [Structural audit](audit.json) · [Latest static results](static-validation-2026-10-01/COLLECTION_REVIEW.md) · [Original static results](static-validation-2026-09-25/COLLECTION_REVIEW.md)

Static evidence collection finished for all **204 cases**: **126 complete and 78 incomplete**. The incomplete cases include **12 Bash snapshots excluded under `bin/`** and **66 native parser/check-coverage failures**. The collector correctly returned exit code 2, and a resume reused all saved results. These findings need investigation before benchmarking; no sources, labels or scanner rules were changed to improve the outcomes.

The **2026-10-01** repair collection retains these original observations and
records **155 complete and 49 incomplete cases**. All source inventories now
match, including `bin/` scripts. Twenty-nine cases recovered complete coverage
after correcting verified parser metadata handling. Native syntax diagnostics
and constructs outside the audited AST policy remain incomplete. Two failed
worker-recovery attempts are preserved alongside explicit retries. The release
and human-review gates remain unmet; these counts are not accuracy measurements.

The source files are data embedded in JSON and quoted in review sheets. Do not execute them. Trusted scanner collection uses the existing API, durable worker and isolated scanner service; it does not install case dependencies, build repositories, execute case tests or make model requests. Read actual parser and coverage results separately from label agreement. Passing a parser does not establish type correctness, reachability, a working deployment, or safe behavior.

## Review batches

Each language has six proposed vulnerable and six proposed safe cases. Safe cases are separate scenarios, not supplied reference fixes. These source files were authored without consulting detection results or using the held-out cases to tune rules/prompts.

| Language | Review sheet |
| --- | --- |
| Python | [12 cases](review/python.md) |
| JavaScript | [12 cases](review/javascript.md) |
| TypeScript | [12 cases](review/typescript.md) |
| Java | [12 cases](review/java.md) |
| Go | [12 cases](review/go.md) |
| C | [12 cases](review/c.md) |
| C++ | [12 cases](review/cpp.md) |
| Ruby | [12 cases](review/ruby.md) |
| PHP | [12 cases](review/php.md) |
| Scala | [12 cases](review/scala.md) |
| Kotlin | [12 cases](review/kotlin.md) |
| Swift | [12 cases](review/swift.md) |
| C# | [12 cases](review/csharp.md) |
| F# | [12 cases](review/fsharp.md) |
| Visual Basic | [12 cases](review/visualbasic.md) |
| Rust | [12 cases](review/rust.md) |
| Bash | [12 cases](review/bash.md) |

Every specification includes its source, proposed findings, rationale, runtime/setup assumptions, legitimate inputs and expected outputs, permitted/forbidden remediations, regression traps, scoped residual risks, provenance and derivation rationale. The `replacement_trace` links the historical planning slot; it is not a reference repair or evidence that v1 source was a template. The original v1 corpus and planning register are preserved.

## Independent human review

1. Review each complete specification, including source semantics, active callers, concrete library assumptions, legitimate behavior, all relevant expected findings and safe-case residual risks. A matching scanner result is supporting evidence, not ground truth.
2. Resolve authoring mistakes and incomplete parser/check outcomes. Make semantic revisions in a new corpus version, preserve previous evidence, regenerate complete-specification hashes and collect new static evidence. Do not alter a valid label or tune rules/prompts to improve held-out detection scores.
3. Compare derivation groups **across all languages**. Unique hashes, scenario names and author-written independence rationales do not prove independence. Translations and related variants cannot count as independent cases; any discovered relationship must be declared and resolved before approval. Review the statistical resampling assumptions as well. The corpus-level `review_concerns` explicitly flags SQL ordering cases, shared Swift ATS configuration, broader-than-rulepack weaknesses and corpus-wide independence/statistical assumptions.
4. Resolve each corpus-level concern with the actual independent human's `reviewer`, `reviewer_kind: "human"`, ISO `reviewed_at`, substantive `resolution`, and `status: "resolved"`. This is a human task, not fields for automation to manufacture. Those resolutions change the hashed corpus context, so finalize them and generate a new review packet **before** approving individual case hashes. A freeze refuses unresolved concerns even if individual case approvals exist.
5. Record the actual human review in the candidate using [review protocol 2.0](../../README.md#audit-approve-freeze). Bind approval to the exact `content_sha256` and `case_spec_sha256` inspected. Automation has not supplied a human name, date or approval. The unsigned packet is not automatically imported.

Do not rerun assembly over human work. The assembler refuses to overwrite nonempty review notes, identities, dates, decisions or approval hashes, or altered generated Markdown/CSV/JSON artifacts. `artifact-manifest.json` records generated file hashes. `candidate_corpus check` verifies the generated pre-review packet against the authoring fragments; it is not an approval checker. Use `evaluation.benchmark audit` for approval validity after human review.

## Reproduce static evidence

Run from `codeagent-scanner` in the locked Python environment, with the existing Compose stack healthy:

```sh
python -m evaluation.candidate_corpus check
python -m evaluation.static_validation \
  --output evaluation/corpus-v2/authored/static-validation-2026-10-01
python -m evaluation.benchmark --corpus evaluation/corpus-v2/authored/corpus.json audit
```

The collector pins the complete source/specification set, collector implementation and effective scanner profiles, stores job IDs before polling, and retains exact reports and hashes. A nonblocking output lock prevents concurrent collectors from double-submitting. Resume reuses recorded results. Use a new evidence directory if the specification, implementation or scanner/profile changes. Canceled attempts are retained; an explicit `--retry-case CASE_ID` may start a new attempt only after reconciling any uncertain submission and verifying the previous job has stopped.

## Remaining release conditions

No human approvals, model comparisons, accepted fixes or measured quality gains are created by this packet. After approval and a reviewed independence/statistical plan, freeze the model, prompts, profiles and configuration. Then collect the static baseline and three repetitions each of single-agent and multi-agent review, and obtain blinded human proposal judgments. The original 10-percentage-point fix improvement, 20% relative false-positive reduction, no-lower-recall and statistical-evidence requirements remain unchanged.
