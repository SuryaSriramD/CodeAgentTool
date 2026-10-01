"""Assemble and audit authored candidates without executing or approving them."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath

from analyzers.common import language_for
from evaluation.corpus_review import case_review_digest, review_manifest, source_digest
from evaluation.replacement_register import LANGUAGES, build_register

ROOT = Path(__file__).resolve().parent / "corpus-v2" / "authored"
VERSION = "heldout-2.0.0-candidate"
SCHEMA_VERSION = "2.0"
MAX_CASE_BYTES = 500 * 1024 * 1024
MAX_CASE_FILES = 10000


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def validate_candidate(corpus, *, complete=True):
    cases = corpus.get("cases", [])
    if not isinstance(cases, list) or not cases or (complete and len(cases) != 204):
        raise ValueError("An authored candidate requires 204 cases (or an explicit partial audit)")
    ids, sources, scenarios, counts = set(), set(), set(), Counter()
    for case in cases:
        language = case.get("language")
        if language not in LANGUAGES or type(case.get("vulnerable")) is not bool:
            raise ValueError("Unknown language or non-boolean label")
        label = "vulnerable" if case["vulnerable"] else "safe"
        identity = case.get("id", "")
        if not re.fullmatch(rf"v2-{language}-{label}-0[1-6]", identity) or identity in ids:
            raise ValueError("Candidate IDs must uniquely match their planned language/label slots")
        ids.add(identity)
        counts[(language, label)] += 1
        scenario = case.get("scenario")
        if not isinstance(scenario, str) or not scenario.strip() or scenario in scenarios:
            raise ValueError(f"{identity}: a distinct scenario description is required")
        scenarios.add(scenario)
        files = case.get("files")
        if not isinstance(files, dict) or not files or len(files) > MAX_CASE_FILES:
            raise ValueError(f"{identity}: missing or excessive source inventory")
        total = 0
        for name, source in files.items():
            if not isinstance(name, str) or not isinstance(source, str):
                raise ValueError("Candidate files must be relative text files")
            path = PurePosixPath(name)
            if (not path.parts or name != path.as_posix() or path.is_absolute()
                    or any(part in {".", ".."} for part in path.parts) or "\\" in name or "\x00" in name
                    or re.match(r"^[A-Za-z]:", name)):
                raise ValueError("Candidate file path is not a contained canonical relative path")
            total += len(source.encode("utf-8"))
        if total > MAX_CASE_BYTES:
            raise ValueError("Candidate exceeds source snapshot size limit")
        if any(parent.as_posix() in files for name in files for parent in PurePosixPath(name).parents):
            raise ValueError(f"{identity}: file/ancestor source path collision")
        declared = "vb" if language == "visualbasic" else language
        if not any(language_for(Path(name)) == declared and source.strip() for name, source in files.items()):
            raise ValueError(f"{identity}: no source file in the declared language")
        source_hash = source_digest(files)
        if case.get("content_sha256") != source_hash or source_hash in sources:
            raise ValueError(f"{identity}: source hash mismatch or exact duplicate case")
        sources.add(source_hash)
        expected = case.get("expected_findings")
        if not isinstance(expected, list) or bool(expected) != case["vulnerable"]:
            raise ValueError(f"{identity}: expected findings disagree with label")
        for finding in expected:
            if (not isinstance(finding, dict) or finding.get("path") not in files
                    or not finding.get("family") or not re.fullmatch(r"CWE-\d+", finding.get("cwe", ""))):
                raise ValueError(f"{identity}: invalid expected finding evidence")
            start, end = finding.get("line_start"), finding.get("line_end")
            if start is not None and (type(start) is not int or start < 1
                    or start > len(files[finding["path"]].splitlines())):
                raise ValueError(f"{identity}: expected finding line is outside source")
            if end is not None and (type(end) is not int or end < (start or 1)
                    or end > len(files[finding["path"]].splitlines())):
                raise ValueError(f"{identity}: expected finding end line is outside source")
        for field in ("rationale", "remediation_constraints", "runtime_assumptions", "operation_contract",
                      "regression_traps", "ground_truth_scope", "derivation", "provenance"):
            if not case.get(field):
                raise ValueError(f"{identity}: {field} is required for human review")
        operation = case["operation_contract"]
        if not all(operation.get(key) for key in ("purpose", "trust_boundary", "legitimate_examples", "forbidden_changes")):
            raise ValueError(f"{identity}: incomplete legitimate-operation contract")
        if not isinstance(operation.get("permitted_changes"), list):
            raise ValueError(f"{identity}: permitted changes must be explicit")
        if not all(isinstance(example, dict) and "input" in example and "expected" in example
                   for example in operation["legitimate_examples"]):
            raise ValueError(f"{identity}: legitimate examples need input and expected output")
        derivation = case["derivation"]
        if not all(derivation.get(key) for key in ("group", "origin", "independence_rationale")):
            raise ValueError(f"{identity}: provenance and independence rationale are required")
        if not isinstance(derivation.get("related_case_ids"), list) or case.get("split") != "held_out":
            raise ValueError(f"{identity}: explicit derivation relationships and held-out split required")
        if case["ground_truth_scope"].get("profile") != "security-v2":
            raise ValueError(f"{identity}: declare candidate security-v2 scope")
    if complete and any(counts[(lang, label)] != 6 for lang in LANGUAGES for label in ("safe", "vulnerable")):
        raise ValueError("Every language needs six vulnerable and six safe cases")
    for case in cases:
        if set(case["derivation"]["related_case_ids"]) - ids:
            raise ValueError(f"{case['id']}: unknown related case identity")
    return cases


def assemble(language_dir=ROOT / "languages"):
    register = build_register()
    slots = {entry["slot_id"]: entry for entry in register["slots"]}
    cases = []
    for language in sorted(LANGUAGES):
        fragment = json.loads((Path(language_dir) / f"{language}.json").read_text())
        if fragment.get("language") != language or len(fragment.get("cases", [])) != 12:
            raise ValueError(f"{language}: exactly 12 authored entries required")
        for raw in fragment["cases"]:
            case = copy.deepcopy(raw)
            if case.get("language") != language or case.get("id") not in slots:
                raise ValueError("Authored case does not match replacement register")
            review = case.get("human_review") or {}
            if (review.get("status") != "pending" or review.get("reviewer")
                    or review.get("reviewed_case_sha256") or review.get("reviewed_content_sha256")):
                raise ValueError("Authoring fragments must not contain manufactured approvals")
            case["content_sha256"] = source_digest(case["files"])
            case["replacement_trace"] = {
                "register_version": register["register_version"], "slot_id": case["id"],
                "prior_case_id": slots[case["id"]]["source_case_id"],
                "prior_source_sha256": slots[case["id"]]["source_content_sha256"],
                "relationship": "replacement coverage slot; not a reference fix or source template",
            }
            cases.append(case)
    corpus = {"schema_version": SCHEMA_VERSION, "version": VERSION,
              "status": "awaiting_independent_human_review",
              "description": "204 newly AI-authored candidate cases. Labels, independence and remediation contracts require human review; no measured accuracy claim.",
              "approval_policy": "Require independent human approval of each complete case specification and conceptual independence across all 204 cases; preserve all agreed quality gates.",
              "evaluation_scope": {"profile": "security-v2", "source_execution": "prohibited",
                                   "independence": "unverified_until_human_review",
                                   "safe_cases": "independent scenarios, not reference repairs",
                                   "tuning": "held-out source must not tune prompts or rules"},
              "review_concerns": [
                  {"id": "V2-IND-001", "status": "pending_independent_human_review",
                   "case_ids": ["v2-rust-vulnerable-02", "v2-typescript-vulnerable-05", "v2-visualbasic-vulnerable-01"],
                   "concern": "These cases include SQL ordering/identifier selection. Compare actual operation, dataflow and derivation across languages; distinct APIs or domains alone do not establish independence. Similarity is not proof of copying or dependence."},
                  {"id": "V2-IND-002", "status": "pending_independent_human_review",
                   "case_ids": ["v2-swift-vulnerable-01", "v2-swift-vulnerable-02"],
                   "concern": "These cases share an identical auxiliary Info.plist (ATS configuration). Swift implementations differ. Review the complete contexts before deciding whether shared platform setup creates a dependent scenario."},
                  {"id": "V2-SCOPE-001", "status": "pending_independent_human_review",
                   "concern": "Some candidate weaknesses exceed the current rulepack's documented API/pattern coverage. Preserve scanner misses and proposed labels separately; review full expected-finding scope and case semantics before freeze. Do not tune rules/prompts to these held-out observations."},
                  {"id": "V2-IND-003", "status": "pending_independent_human_review",
                   "concern": "All 204 conceptual-independence judgments and the case-cluster statistical assumptions require review across the corpus. Unique hashes or author-written derivation groups are insufficient. Repeated XML and process APIs warrant particular attention."},
              ],
              "cases": sorted(cases, key=lambda case: case["id"])}
    validate_candidate(corpus)
    return corpus


def audit(corpus):
    cases = validate_candidate(corpus)
    return {"cases": len(cases), "languages": len({c["language"] for c in cases}),
            "proposed_vulnerable": sum(c["vulnerable"] for c in cases),
            "proposed_safe": sum(not c["vulnerable"] for c in cases),
            "multi_file_cases": sum(len(c["files"]) > 1 for c in cases),
            "source_lines": sum(len(s.splitlines()) for c in cases for s in c["files"].values()),
            "independence_status": "pending_human_review", "release_status": "candidate",
            "specification_set_sha256": canonical_digest({c["id"]: case_review_digest(corpus, c) for c in cases})}


def artifacts(corpus):
    rows = []
    output = {"corpus.json": json.dumps(corpus, indent=2, ensure_ascii=False) + "\n",
              "unsigned-review-manifest.json": json.dumps(review_manifest(corpus), indent=2, ensure_ascii=False) + "\n"}
    for language in sorted(LANGUAGES):
        lines = [f"# {language} — authored corpus-v2 candidates", "",
                 "AI-authored, pending independent human review. Static validation is separate evidence, not approval. "
                 "Source is quoted for inspection and must not be executed.", "",
                 "Review the corpus-level context and checklist in the "
                 "[complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.", ""]
        for case in (c for c in corpus["cases"] if c["language"] == language):
            identity = case_review_digest(corpus, case)
            rows.append({"case_id": case["id"], "language": language, "proposed_label": "vulnerable" if case["vulnerable"] else "safe",
                         "scenario": case["scenario"], "status": "authored_pending_human_review",
                         "source_sha256": case["content_sha256"], "case_spec_sha256": identity,
                         "derivation_group": case["derivation"]["group"], "human_review": "pending"})
            lines += [f"## {case['id']} — {case['scenario']}", "",
                      f"Proposed label: **{'vulnerable' if case['vulnerable'] else 'safe'}**. Human review: **pending**.", "",
                      f"Source hash: `{case['content_sha256']}`. Protocol-2.0 case hash: `{identity}`.", "",
                      case["rationale"], ""]
            for path, text in case["files"].items():
                fence = "`" * max(3, 1 + max((len(run) for run in re.findall(r"`+", text)), default=0))
                lines += [f"### {path}", "", fence + language, text.rstrip("\n"), fence, ""]
            rendered = {"id", "language", "vulnerable", "scenario", "files", "content_sha256", "rationale", "human_review"}
            for field in sorted(set(case) - rendered):
                rendered_json = json.dumps(case[field], indent=2, ensure_ascii=False)
                fence = "`" * max(3, 1 + max((len(run) for run in re.findall(r"`+", rendered_json)), default=0))
                lines += [f"### {field.replace('_', ' ').capitalize()}", "", fence + "json",
                          rendered_json, fence, ""]
        output[f"review/{language}.md"] = "\n".join(lines) + "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    output["authoring-register.csv"] = buffer.getvalue()
    output["audit.json"] = json.dumps(audit(corpus), indent=2) + "\n"
    output["artifact-manifest.json"] = json.dumps({name: hashlib.sha256(text.encode("utf-8")).hexdigest()
                                                 for name, text in output.items()}, indent=2) + "\n"
    return output


def write_artifacts(corpus, output):
    output = Path(output)
    generated = artifacts(corpus)
    # Generated packets can become human work products. Refuse to overwrite
    # recorded decisions, even if a caller mistakenly rebuilds from fragments.
    for name in ("corpus.json", "unsigned-review-manifest.json"):
        existing = output / name
        if existing.exists():
            old = json.loads(existing.read_text())
            if any(any(value for key, value in (entry.get("human_review") or {}).items()
                       if key not in {"status", "review_schema_version"})
                   or (entry.get("human_review") or {}).get("status") not in {None, "pending"}
                   for entry in old.get("cases", [])):
                raise ValueError("Existing candidate or packet contains human review work; preserve it and use a new version/directory")
    previous_manifest = output / "artifact-manifest.json"
    if previous_manifest.exists():
        expected = json.loads(previous_manifest.read_text())
        for name in generated:
            existing = output / name
            if name != "artifact-manifest.json" and existing.exists() and (
                    name not in expected or hashlib.sha256(existing.read_bytes()).hexdigest() != expected[name]):
                raise ValueError(f"Modified generated artifact may contain review work: {name}; preserve it and use a new directory")
    elif any((output / name).exists() for name in generated):
        raise ValueError("Existing generated files lack integrity metadata; preserve them and use a new directory")
    for name, text in generated.items():
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["assemble", "check"])
    parser.add_argument("--languages", type=Path, default=ROOT / "languages")
    parser.add_argument("--output", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    corpus = assemble(args.languages)
    if args.command == "assemble":
        write_artifacts(corpus, args.output)
    else:
        for name, expected in artifacts(corpus).items():
            path = args.output / name
            if not path.is_file() or path.read_text() != expected:
                raise ValueError(f"Authored packet differs from source fragments: {name}")
    print(json.dumps(audit(corpus), indent=2))


if __name__ == "__main__":
    main()
