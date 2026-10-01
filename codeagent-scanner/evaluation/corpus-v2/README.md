# Corpus v2 replacement planning packet

**This directory preserves the original planning register.** Its 204 slots remain an immutable snapshot of the pre-authoring plan, with no approvals. The subsequent [authored candidate and review packet](authored/README.md) lives separately under `authored/`; it does not overwrite this historical register. The original corpus and its AI review remain unchanged.

[Complete register](replacement-register.json) · [CSV working view](replacement-register.csv) · [58 priority briefs](PRIORITY_FIXES.md) · [Priority CSV](priority-fixes.csv)

The intended destination is `heldout-2.0.0-candidate`: six vulnerable and six safe cases for each of the 17 advertised languages. These are **planning quotas**, not established ground truth. Every historical slot has status `planned_not_authored`, no owner, no authored case or hash, and pending human review; consult the separate [authoring register](authored/authoring-register.csv) for subsequent work. The 58 priority slots trace the 15 revision and 43 clarification decisions from the [AI review](../corpus-v1/ai-review-2026-09-25/README.md). The other 146 cases are locally supported under assumptions, but **all 204 require genuinely independent new authoring** to address CR-001 and CR-002.

## How to use the register

1. Assign authors and independently conceive the new contexts before writing source. Use the old case only to understand its review problems and planned coverage area. Do not rename, translate, lengthen or pair templates and call them independent scenarios.
2. Record the actual operation, trust boundary, runtime/driver/platform, legitimate inputs and outputs, and a meaningful regression trap. The case-specific briefs retain reviewed assumptions, remediation questions and issue references. They do not prescribe a replacement source or invent provenance.
3. Declare every derivation relationship across all languages and any relationship to development fixtures. The original derivation groups are minimum known relationships, not proof that no others exist. The future group is unassigned: a unique slot ID is not evidence of independence. A safe slot is not an automatic reference fix for a vulnerable slot.
4. Author the separate corpus with source-visible callers/consumers and meaningful multi-file context where appropriate. Keep ground truth, remediation constraints and provenance separate from model inputs. Review every safe case for residual findings under the complete planned scan profile.
5. Record trusted parser/scanner results without installing case dependencies, building repositories or executing case source/tests. Resolve missing tools, parser failures and unreachable setup as incomplete validation, never security success.
6. Have an independent human review the complete versioned case specification, conceptual independence and all acceptance evidence. Bind approval to the new complete-specification digest, not the historical hashes in this register. Only then create and freeze a runnable corpus version with its own approvals and reviewed statistical plan.

The per-slot checklist deliberately remains pending. It covers independence, actual derivation, source-visible behavior, runtime/setup, meaningful context, regression traps, comprehensive ground truth, trusted static validation, provenance, held-out separation and human approval. Neither this packet nor the AI technical review satisfies those checks.

## Input identity and deterministic verification

The JSON records the exact SHA-256 hashes of the original corpus and complete structured AI review. Each slot also records:

- The unchanged v1 case ID and files-only `content_sha256`.
- `source_legacy_review_spec_sha256`, the historical AI review-input hash: SHA-256 of Python `json.dumps(case_without_human_review, sort_keys=True)` using its default separators and ASCII escaping. This includes the old source hash and case metadata. **It is not a human-approval digest.**
- The prior AI verdict, rationale, assumptions, issues/references and known derivation group.

From the repository root, verify the committed packet using only the Python standard library:

```sh
python3 codeagent-scanner/evaluation/replacement_register.py --check
```

To reproduce its four generated files from the original inputs:

```sh
python3 codeagent-scanner/evaluation/replacement_register.py --write
```

The generator checks original bytes, per-case source/specification hashes, matching IDs/languages/labels, and 204-case balance before generating anything. The checker compares JSON, both CSV views and the priority Markdown against those verified inputs, so stale or fabricated approvals, missing slots or changed priorities fail verification. Neither command calls a model, scanner, network service or repository program.

`replacement-register.json`, both CSV files and `PRIORITY_FIXES.md` are generated planning evidence, not an editable approval database. Preserve this version as an audit snapshot. Track actual assignments and authored work in a subsequent register version; do not regenerate over that work or fill this packet with fake completed cases. Corpus approval must use the dedicated complete-specification workflow.

## Remaining release gates

The register prepares authoring; it does not establish 204 independent cases, human approval, parser coverage or model quality. After independent authoring and approval, freeze model/prompts/profiles/configuration, record the static baseline and three repetitions of each AI mode using the selected local model, and obtain blinded human proposal reviews. The original quality targets remain unchanged: at least a 10-percentage-point improvement in independently accepted, statically validated fixes, at least a 20% relative false-positive reduction, no lower recall, and evidence beyond sampling noise. No result is claimed here.
