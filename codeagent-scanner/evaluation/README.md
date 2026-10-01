# Recorded quality evaluation

`benchmark.py` collects static, single-agent, and multi-agent observations through the ordinary API and durable worker. It never executes corpus source, installs repository dependencies, or launches repository tests. Both AI modes receive the same immutable scan, model, source-access tools, absolute budgets, static proposal validator, and one revision allowance. The single-agent baseline retains one conversation for triage, authoring, and self-review; the multi-agent reviewer receives a fresh conversation.

The release stays a **candidate**. `corpus-v1/corpus.json` contains **204 distinct originally authored source cases**, six vulnerable and six safe cases for each of the 17 advertised languages. They are proposed benchmark material, not independently verified ground truth. Every label is currently **pending human review**. An independent maintainer must verify the source semantics, vulnerability rationale, safe behavior, remediation constraints, provenance, and case independence. A content hash only detects exact duplicates; it cannot establish conceptual independence. Revise questionable cases and publish a new corpus version before approval.

The six-case `corpus.json` and `compare.py` remain synthetic metric-calculation examples for old tests. They cannot satisfy the release benchmark gate and must never be published as live model results.

The [AI corpus review](corpus-v1/ai-review-2026-09-25/README.md) found 43 cases needing clarification and 15 requiring revision, plus corpus-wide independence and realism problems. The [corpus-v2 replacement register](corpus-v2/README.md) preserves the **204-slot historical plan**, including the 146 locally supported cases. Subsequent [authored v2 candidates](corpus-v2/authored/README.md) have their own source, full-specification hashes, authoring register and unsigned human-review packet. Neither authoring nor scanner observations establish approved ground truth or conceptual independence. Preserve v1 and the planning snapshot as audit evidence.

## Authoring and static evidence

From `codeagent-scanner`, assemble or verify the authored fragments without executing source or calling a model:

```sh
python -m evaluation.candidate_corpus assemble
python -m evaluation.candidate_corpus check
```

Assembly enforces the 17-language, six-safe/six-vulnerable quotas, source in each declared language, contained noncolliding paths, unique exact source hashes, expected-finding locations, operation contracts and provenance. It produces readable review sheets per language and a protocol-2.0 unsigned manifest. These structural checks do not prove semantic validity or independence. Assembly refuses to overwrite recorded human review work or edited generated artifacts; preserve revisions in a new version and directory.

Collect trusted scanner evidence for the pending candidates through the existing API/worker:

```sh
python -m evaluation.static_validation \
  --output /absolute/path/candidate-static-evidence
```

The default is `corpus-v2/authored/corpus.json`, the explicit `security-v2` profile, two static jobs at a time, and a 120-second scan budget. There are no AI calls, builds, dependency installations or executions of case source/tests. The journal pins every complete case specification and scanner/profile identity; saved report artifacts are checked before reuse. A changed specification or engine/profile requires a new evidence directory. Stop with Ctrl-C to request cancellation of active jobs, then resume the same command to collect their final states. Completed results are reused. An uncertain submission is never silently retried: reconcile the saved job or server jobs before explicitly using `--retry-case CASE_ID`.

`state.json`, `summary.json` and the saved reports distinguish parser/check coverage, operational completion, and agreement with **proposed** labels. An unobserved expected finding does not make vulnerable source safe. An extra finding is not automatically a false positive. Missing tools, parser failures, failed scans and incompatible source/profile evidence remain incomplete. Use `--limit-cases N` for a checkpointed pilot; rerun without it for the entire set. Exit code 2 means collection or operational evidence is incomplete. These observations cannot pass a release-quality gate, manufacture approvals, or authorize tuning rules/prompts against held-out source.

## Audit, approve, freeze

Run commands from `codeagent-scanner` with the locked Python environment:

```sh
python -m evaluation.benchmark audit
```

The audit distinguishes valid current human approvals, pending reviews, and stale/invalid approvals. The legacy `human_approved` count now includes only valid current approvals. Historical source-only records remain readable, but cannot authorize a new freeze, resumed run, or score.

Prepare an **unsigned offline review packet** for a fully authored candidate corpus:

```sh
python -m evaluation.benchmark --corpus /absolute/path/candidate/corpus.json \
  review-manifest --output /absolute/path/review/unsigned-manifest.json
```

This command includes each complete case specification, corpus context, checklist, source hash and versioned case hash. It makes no API or model request and leaves every review pending, even if the input contains an old approval. It refuses to overwrite an existing packet. A packet for v1 is useful only for auditing its rejected candidate material; it does not resolve the recorded corpus-wide blockers.

After inspection and resolution of all blockers, the independent human reviewer records these fields in the candidate case's `human_review` object:

```json
{
  "status": "approved",
  "reviewer_kind": "human",
  "reviewer": "Actual independent reviewer's name",
  "reviewed_at": "2026-09-25",
  "review_schema_version": "2.0",
  "reviewed_content_sha256": "Copy the exact source hash inspected",
  "reviewed_case_sha256": "Copy the exact case_spec_sha256 inspected",
  "notes": "Record the review evidence and resolved concerns"
}
```

These are instructions for a human attestation, not a template that automation may populate as approved. The packet is not automatically imported. If source or metadata changed after the packet was prepared, generate a new packet and re-review the changed specification; do not refresh approval hashes mechanically.

Review protocol `2.0` hashes a domain-separated canonical JSON payload containing **every case field except `human_review`**, plus all corpus-level fields except `cases` and administrative `status`. It binds labels, expected findings/CWEs, rationale, remediation constraints, provenance, runtime assumptions, derivation metadata, future fields and corpus version/policy. Dictionary ordering does not matter; list ordering and security-relevant string contents do. Source hashing retains its historical encoding and is checked separately. Review notes and administrative status changes do not change the case identity; semantic requirements must live in the specification rather than review notes. The AI review's earlier `case_spec_sha256` audit annotation uses a different encoding and is **not** a protocol-2.0 approval hash.

Legacy approvals must be independently re-reviewed under this protocol. Unapproved, source-changed or metadata-changed specifications fail before freeze/run reaches the API. A candidate with `review_concerns` also requires named independent human resolutions of every corpus-wide concern before freeze. Finalize those semantic resolutions before approving the individual case hashes, because corpus context is included in each hash. Hashes detect stale review records; they are not signatures or proof of reviewer identity or independence. Keep held-out cases out of rule and prompt tuning. The automation never approves its own labels.

Create a review configuration JSON with an explicit provider/model and the shared budgets:

```json
{
  "provider": "ollama",
  "model": "gemma3:4b",
  "min_severity": "low",
  "max_model_calls": 60,
  "max_total_tokens": 100000,
  "timeout_sec": 900,
  "max_findings": 20,
  "max_context_chars": 60000,
  "max_output_tokens": 4000
}
```

The model must already be installed. Freeze against the running API; this command does not start model requests:

```sh
python -m evaluation.benchmark --url http://localhost:8000 freeze \
  --config /absolute/path/review-config.json --output /absolute/path/benchmark/frozen.json
```

Pass the same `--corpus /absolute/path/candidate/corpus.json` global option to freeze, run, blind and score when using a revised corpus. The default remains the historical v1 file for read-only audit convenience; its pending approvals prohibit evaluation.

The freeze records corpus, workflow/prompt, configuration, scanner versions, source/dependency profile digests, and the installed Ollama model digest. A model, rulepack, advisory database, source, prompt, or configuration change requires a new freeze; corpus revisions require new human approval. Hosted benchmarks require an explicit dated OpenAI model snapshot and `--allow-cloud` on **both** freeze and run. No hosted provider is used as a local fallback. Credentials come only from the running server, with `CODEAGENT_TOKEN` or `CODEAGENT_PASSWORD` used in process memory to authenticate this client; they are not stored in benchmark files.

## Collect and resume

```sh
python -m evaluation.benchmark --url http://localhost:8000 run \
  --freeze /absolute/path/benchmark/frozen.json --output /absolute/path/benchmark/run
```

Collection creates a named benchmark project, submits each source case once, and runs three repetitions of each AI mode. Static results are reused as the common baseline for each repetition. Review job IDs are saved before waiting; resume uses those same jobs and completed records. Interrupted model calls stay interrupted and count as unsuccessful observations. The runner never automatically retries them. Stop with Ctrl-C and rerun the same command to resume. `--limit-cases N` checkpoints after a subset; an incomplete collection cannot pass the quality gate. Artifacts include the exact report, actual provider/model and usage, operational errors, source/report hashes, and server execution latency. Static rows repeated for pairing do not represent three independent scanner executions.

A full local run is deliberately not launched automatically. It comprises 1,224 AI reviews (204 cases × two modes × three repetitions), subject to each review's configured budgets and the existing one-request local-model concurrency limit.

## Blinded human proposal review

```sh
python -m evaluation.benchmark blind --records /absolute/path/benchmark/run/observations.json \
  --output /absolute/path/benchmark/human-review
```

Give `blinded-review-sheets.json` to an independent reviewer. It includes original source, remediation constraints, proposed diff, and deterministic validation, without provider or agent-mode labels. Keep `private-review-map.json` separate until scoring; it is written with owner-only permissions. Each proposed change needs `accepted` or `rejected`, reviewer, date, and rationale. Reject behavior regressions and changes that merely delete the intended operation. Missing/invalid proposals do not get invented review entries: they already count as unsuccessful. Do not regenerate an existing map because that breaks recorded human decisions.

```sh
python -m evaluation.benchmark score --freeze /absolute/path/benchmark/frozen.json \
  --records /absolute/path/benchmark/run/observations.json \
  --mapping /absolute/path/benchmark/human-review/private-review-map.json \
  --sheets /absolute/path/benchmark/human-review/blinded-review-sheets.json \
  --output /absolute/path/benchmark/quality-report.json
```

## Gate and interpretation

The gate requires all observations and independently scored proposals, at least a **10 percentage point increase** in accepted statically validated fixes, **20% relative reduction** in false positives, and no decreased vulnerability recall. Zero single-agent false positives makes the reduction comparison inconclusive. A fix only qualifies when it addresses an expected finding, passes the trusted static validator, has an approved model review, and is independently accepted by the human reviewer. Missing, malformed, rejected, interrupted, timed-out and incomplete results are unsuccessful. Unresolved triage preserves original scanner findings.

The report publishes per-mode false positives/negatives, recall, successful-fix rate, median and 95th percentile latency, actual reported tokens and usage completeness, failures, and paired 95% confidence intervals. A fixed-seed, language/label-stratified case-cluster bootstrap keeps a case's three repetitions together. Both improvement confidence intervals must exclude zero. Operationally incomplete evidence keeps the release a candidate. There is no relative latency/token ceiling, but absolute run budgets remain enforced.

The current bootstrap does not account for translated-template dependence between different case IDs. The corpus review records this as an unresolved evaluation-protocol concern. The replacement register does not establish independence or fix the resampling design. Before any release comparison, satisfy the independent-case requirement and have the derivation groups and resampling assumptions reviewed. Infrastructure or approval-integrity tests cannot satisfy the quality gate.

These are case-level metrics on the frozen corpus, not estimates of every repository or vulnerability. Passing static validation is not runtime testing or proof of security. Publish actual results and limitations even when the gate fails; do not weaken thresholds after looking at held-out results.
