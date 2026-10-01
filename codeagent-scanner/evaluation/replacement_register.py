"""Build/check a planning packet from the immutable corpus-v1 AI review.

This stdlib-only tool never authors, executes, labels, or approves benchmark
source. The output is deliberately not a runnable corpus. Its hashes describe
historical inputs; they are not the versioned human-approval digest.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus-v1/corpus.json"
REVIEW = ROOT / "corpus-v1/ai-review-2026-09-25/review.json"
DESTINATION = ROOT / "corpus-v2"
LANGUAGES = frozenset({
    "python", "javascript", "typescript", "java", "go", "c", "cpp", "ruby",
    "php", "scala", "kotlin", "swift", "csharp", "fsharp", "visualbasic",
    "rust", "bash",
})
VERDICTS = {"supported", "needs_clarification", "revise", "invalid"}
SCHEMA = "codeagent.corpus-replacement-plan/1"
LEGACY_SPEC_ALGORITHM = "sha256-json-sort_keys-defaults-case-excluding-human_review/1"

CHECKLIST = {
    "independent_conception": "Document a genuinely different scenario, trust boundary and data flow; renamed, translated, or safe/vulnerable variants of the same template do not count as independent cases.",
    "derivation_audit": "Disclose every source, sibling, translation and development-fixture relationship; assign the actual derivation group and have a human assess conceptual independence across all 204 cases.",
    "source_visible_contract": "Include the entry point, caller/consumer, meaningful legitimate inputs and expected outputs, and explicit permitted behavior changes; deleting or replacing the operation is not a successful fix.",
    "runtime_and_setup": "Pin runtime, framework/library/driver/platform assumptions and trusted setup needed for the operation to be reachable; record initialization/schema requirements without executing repository code.",
    "meaningful_context": "Supply imports/declarations and meaningful caller/configuration context. Use multiple files when the flow requires them; adding cosmetic files or lines is not realism.",
    "regression_trap": "Include a case-specific legitimate edge case and acceptance constraint that distinguishes a behavior-preserving remediation from a superficially safe regression.",
    "complete_ground_truth": "Review all relevant findings under the frozen profile and threat model, not only the old target family. State expected findings and scope; a safe label requires review of residual weaknesses.",
    "trusted_static_validation": "Record actual trusted parser/scanner outcomes, tool/profile versions and coverage. Missing tools, parse failures or unreachable setup cannot count as security success; do not install dependencies, build or execute case code.",
    "traceable_provenance": "Record actual author, origin/license, derivation and human/AI contribution. Do not carry the old source hash or invent authorship for replacement content.",
    "held_out_separation": "Keep the authored case and its derivation group out of prompt/rule development and tuning; give both evaluation modes identical source context, tools, parameters and budgets.",
    "human_spec_approval": "Obtain independent human approval of the complete versioned case specification and its approval digest, including source, ground truth, constraints, runtime assumptions, provenance and derivation group.",
}

FAMILY_BRIEFS = {
    "sql-injection": "Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.",
    "path-traversal": "Define the intended file namespace, path/identifier contract, attacker-controlled components, symlink/write permissions and legitimate nested-file behavior.",
    "ssrf": "Define permitted destinations and the user-visible fetch contract, including DNS, redirects, ports/schemes and trust in destination configuration.",
    "command-injection": "Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.",
    "shell-injection": "Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.",
    "code-injection": "Define the legitimate expression or transformation grammar, supported inputs and outputs, and the interpreter trust boundary; printing input is not automatically an equivalent operation.",
    "dynamic-evaluation": "Define the legitimate expression or transformation grammar, supported inputs and outputs, and the interpreter trust boundary; printing input is not automatically an equivalent operation.",
    "unsafe-deserialization": "Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.",
    "tls-validation": "Show the real client/transport wiring and platform trust policy, distinguish peer/hostname checks, and state the legitimate endpoints and certificate/trust-store behavior.",
    "weak-cryptography": "Show the security-sensitive consumer and adversary model, distinguish integrity from authentication, and define output-format/storage/protocol migration constraints.",
    "format-string": "Show attacker control of formatting input and a meaningful output consumer. Define literal percent handling and, for bounded buffers, capacity and truncation/error behavior.",
    "buffer-overflow": "Show actual destination capacity, input length and a consumer of the result. Define ownership, termination, growth/rejection/truncation and caller-visible behavior.",
    "xxe": "Show parser construction, configured entity/resource policy and its consuming parse operation; pin runtime defaults and legitimate document requirements.",
    "unsafe-xml": "Show parser construction, configured entity/resource policy and its consuming parse operation; pin runtime defaults and legitimate document requirements.",
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def source_hash(case: dict) -> str:
    return sha256(json.dumps(case["files"], sort_keys=True).encode())


def legacy_review_spec_hash(case: dict) -> str:
    # This is exactly the encoding used by the 2026-09-25 AI technical review.
    # Do not replace it with the new human-approval digest or reuse it as approval.
    return sha256(json.dumps({key: value for key, value in case.items()
                             if key != "human_review"}, sort_keys=True).encode())


def load_verified_inputs(corpus_path=CORPUS, review_path=REVIEW):
    corpus_bytes = Path(corpus_path).read_bytes()
    review_bytes = Path(review_path).read_bytes()
    corpus = json.loads(corpus_bytes)
    review = json.loads(review_bytes)
    if review.get("reviewer_kind") != "ai":
        raise ValueError("Replacement planning requires the explicitly AI technical review")
    if review.get("corpus_file_sha256") != sha256(corpus_bytes):
        raise ValueError("Corpus bytes differ from the AI review input")
    if review.get("corpus_version") != corpus.get("version"):
        raise ValueError("Corpus/review version mismatch")
    cases, decisions = corpus.get("cases", []), review.get("cases", [])
    if len(cases) != 204 or len(decisions) != 204:
        raise ValueError("Exactly 204 source cases and review decisions are required")
    by_id = {case.get("id"): case for case in cases}
    decisions_by_id = {decision.get("case_id"): decision for decision in decisions}
    if (len(by_id) != 204 or len(decisions_by_id) != 204 or None in by_id
            or set(by_id) != set(decisions_by_id)):
        raise ValueError("Source and review IDs must match exactly and be unique")
    counts = Counter()
    for case in cases:
        decision = decisions_by_id[case["id"]]
        if case.get("language") not in LANGUAGES or type(case.get("vulnerable")) is not bool:
            raise ValueError("Unknown language or non-boolean source label")
        counts[(case["language"], case["vulnerable"])] += 1
        if case.get("content_sha256") != source_hash(case):
            raise ValueError(f"Source hash mismatch for {case['id']}")
        if decision.get("content_sha256") != case["content_sha256"]:
            raise ValueError(f"Review source hash mismatch for {case['id']}")
        if decision.get("case_spec_sha256") != legacy_review_spec_hash(case):
            raise ValueError(f"Review specification hash mismatch for {case['id']}")
        if (decision.get("language") != case["language"]
                or decision.get("proposed_vulnerable") is not case["vulnerable"]):
            raise ValueError(f"Review label/language mismatch for {case['id']}")
        if decision.get("verdict") not in VERDICTS or not decision.get("independence_group"):
            raise ValueError(f"Missing review verdict/derivation evidence for {case['id']}")
    if any(counts[(language, label)] != 6 for language in LANGUAGES for label in (False, True)):
        raise ValueError("Each language requires six vulnerable and six safe source cases")
    return corpus, review, {"corpus_file_sha256": sha256(corpus_bytes),
                            "ai_review_file_sha256": sha256(review_bytes)}


def build_register(corpus_path=CORPUS, review_path=REVIEW):
    corpus, review, hashes = load_verified_inputs(corpus_path, review_path)
    decisions = {entry["case_id"]: entry for entry in review["cases"]}
    families = {(case["language"], case["scenario"]): sorted({
        finding["family"] for finding in case["expected_findings"]})
        for case in corpus["cases"] if case["vulnerable"]}
    ordinals, slots = Counter(), []
    for case in corpus["cases"]:
        decision = decisions[case["id"]]
        label = "vulnerable" if case["vulnerable"] else "safe"
        ordinals[(case["language"], label)] += 1
        slot_id = f"v2-{case['language']}-{label}-{ordinals[(case['language'], label)]:02d}"
        focus = families[(case["language"], case["scenario"])]
        specific = [FAMILY_BRIEFS.get(family,
            f"Define the {family} threat boundary, reachable API behavior and legitimate consumer contract under a pinned runtime.") for family in focus]
        specific += [issue["recommendation"] for issue in decision["issues"]]
        slots.append({
            "slot_id": slot_id, "language": case["language"],
            "planned_label": label, "planned_family_focus": focus,
            "status": "planned_not_authored", "owner": None,
            "source_case_id": case["id"],
            "source_content_sha256": case["content_sha256"],
            "source_legacy_review_spec_sha256": decision["case_spec_sha256"],
            "source_scenario": case["scenario"],
            "source_derivation_groups": [decision["independence_group"],
                                          f"v1-pair:{case['language']}:{case['scenario']}"],
            "ai_review": {key: decision[key] for key in (
                "verdict", "label_assessment", "rationale", "issues", "assumptions", "review_source")},
            "priority": "local_revision" if decision["verdict"] in {"revise", "invalid"}
                        else "local_clarification" if decision["verdict"] == "needs_clarification"
                        else "independence_and_realism_replacement",
            "replacement_brief": {
                "assignment": f"Independently conceive a {label} {case['language']} case in the planned {', '.join(focus)} coverage area. The old {case['scenario']} case is review evidence, not a source template or gold fix. Declare a different scenario and trust boundary before authoring source.",
                "case_specific_requirements": specific,
                "prior_constraints_to_resolve": case["remediation_constraints"],
                "prior_assumptions_to_resolve": decision["assumptions"],
                "new_runtime_assumptions": None,
                "new_operation_contract": None,
                "new_provenance": None,
                "new_derivation_group": None,
                "independence_evidence": None,
            },
            "required_review_findings": ["CR-001", "CR-002", "CR-005", "CR-006", "CR-007"],
            "acceptance_checklist": [{"id": key, "status": "pending", "evidence": None}
                                     for key in CHECKLIST],
            "authored_case_id": None, "authored_case_spec_sha256": None,
            "human_review": {"status": "pending", "reviewer": None, "reviewed_at": None,
                             "reviewed_case_spec_sha256": None},
        })
    verdicts = Counter(slot["ai_review"]["verdict"] for slot in slots)
    return {
        "schema": SCHEMA, "register_version": "2.0.0-plan.1",
        "artifact_kind": "replacement_plan_not_benchmark_corpus",
        "status": "planned_not_authored", "runnable": False,
        "target_corpus_version": "heldout-2.0.0-candidate",
        "created_from_review_date": review["review_date"],
        "input_identity": {"corpus_path": "../corpus-v1/corpus.json",
                           "corpus_version": corpus["version"],
                           "ai_review_path": "../corpus-v1/ai-review-2026-09-25/review.json",
                           "legacy_review_spec_algorithm": LEGACY_SPEC_ALGORITHM,
                           **hashes},
        "counts": {"slots": len(slots), "languages": len(LANGUAGES),
                   "planned_vulnerable": 102, "planned_safe": 102,
                   "independent_authoring_required": len(slots),
                   "priority_local_fixes": sum(value for key, value in verdicts.items() if key != "supported"),
                   "source_ai_verdicts": dict(sorted(verdicts.items())),
                   "authored": 0, "human_approved": 0},
        "derivation_policy": {
            "required_independent_cases": 204,
            "future_groups_unassigned": True,
            "planning_ids_are_not_independence_evidence": True,
            "all_slots_require_independent_conception": True,
            "original_groups_are_minimum_known_relationships_not_exhaustive": True,
            "instruction": "Record actual common origins across all languages. Do not assign a unique group merely because a slot or source hash is unique. Renames, ports and positive/negative siblings cannot silently satisfy the independent-case requirement. Preserve any shared derivation for held-out separation and a reviewed statistical design.",
        },
        "acceptance_definitions": CHECKLIST,
        "slots": slots,
    }


CSV_COLUMNS = ("slot_id", "language", "planned_label", "planned_family_focus", "status",
               "owner", "source_case_id", "source_content_sha256", "source_legacy_review_spec_sha256",
               "source_derivation_groups", "ai_verdict", "priority", "issue_codes", "replacement_requirements",
               "new_derivation_group", "human_review_status")


def csv_view(slots):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for slot in slots:
        row = {key: slot.get(key) for key in CSV_COLUMNS}
        row.update({"planned_family_focus": " | ".join(slot["planned_family_focus"]),
                    "source_derivation_groups": " | ".join(slot["source_derivation_groups"]),
                    "ai_verdict": slot["ai_review"]["verdict"],
                    "issue_codes": " | ".join(issue["code"] for issue in slot["ai_review"]["issues"]),
                    "replacement_requirements": " | ".join(slot["replacement_brief"]["case_specific_requirements"]),
                    "human_review_status": slot["human_review"]["status"]})
        writer.writerow(row)
    return buffer.getvalue()


def priority_markdown(slots):
    lines = ["# Corpus-v2 priority replacement briefs", "",
             "These 58 slots inherit local clarification/revision questions from the AI technical review. "
             "All 204 slots still require independent new authoring. Nothing below is an authored or human-approved case.", ""]
    for slot in slots:
        lines += [f"## {slot['slot_id']} — {slot['source_case_id']}", "",
                  f"Prior AI verdict: **{slot['ai_review']['verdict']}**. Status: planned, owner unassigned, human review pending.", "",
                  slot["ai_review"]["rationale"], "", "Replacement requirements:", ""]
        lines += [f"- {text}" for text in slot["replacement_brief"]["case_specific_requirements"]]
        lines += ["", "Carry into the new operation/runtime specification:", ""]
        lines += [f"- {text}" for text in slot["replacement_brief"]["prior_assumptions_to_resolve"]]
        if not slot["replacement_brief"]["prior_assumptions_to_resolve"]:
            lines += ["- Declare the actual runtime, trust boundary and legitimate input/output contract."]
        lines += [""]
    return "\n".join(lines)


def packet_files(register):
    priority = sorted((slot for slot in register["slots"] if slot["ai_review"]["verdict"] != "supported"),
                      key=lambda slot: (0 if slot["priority"] == "local_revision" else 1, slot["slot_id"]))
    return {"replacement-register.json": json.dumps(register, indent=2, ensure_ascii=False) + "\n",
            "replacement-register.csv": csv_view(register["slots"]),
            "priority-fixes.csv": csv_view(priority),
            "PRIORITY_FIXES.md": priority_markdown(priority)}


def check_packet(directory=DESTINATION, corpus_path=CORPUS, review_path=REVIEW):
    register = build_register(corpus_path, review_path)
    directory = Path(directory)
    if (directory / "corpus.json").exists():
        raise ValueError("A planning packet must not contain a runnable corpus.json")
    for name, expected in packet_files(register).items():
        path = directory / name
        if not path.is_file() or path.read_bytes() != expected.encode():
            raise ValueError(f"Planning packet differs from verified inputs: {name}")
    return register["counts"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Verify committed packet (default)")
    mode.add_argument("--write", action="store_true", help="Regenerate planning views; never author/approve cases")
    parser.add_argument("--output", type=Path, default=DESTINATION)
    args = parser.parse_args(argv)
    if args.write:
        register = build_register()
        args.output.mkdir(parents=True, exist_ok=True)
        if (args.output / "corpus.json").exists():
            parser.error("Refusing to write a planning packet alongside a runnable corpus.json")
        for name, content in packet_files(register).items():
            (args.output / name).write_bytes(content.encode("utf-8"))
    counts = check_packet(args.output)
    print(json.dumps({"verified": True, **counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
