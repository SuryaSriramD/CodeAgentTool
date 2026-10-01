"""Planning-register integrity tests; these are not corpus or model observations."""
import copy
import csv
import io
import json
from collections import Counter

import pytest

from evaluation.replacement_register import (
    CHECKLIST, CORPUS, DESTINATION, LANGUAGES, REVIEW, build_register,
    check_packet, legacy_review_spec_hash, load_verified_inputs, packet_files, sha256,
)


def write_inputs(tmp_path, corpus=None, review=None):
    corpus = json.loads(CORPUS.read_text()) if corpus is None else corpus
    review = json.loads(REVIEW.read_text()) if review is None else review
    corpus_path, review_path = tmp_path / "corpus.json", tmp_path / "review.json"
    corpus_path.write_text(json.dumps(corpus))
    review["corpus_file_sha256"] = sha256(corpus_path.read_bytes())
    review_path.write_text(json.dumps(review))
    return corpus_path, review_path


def test_committed_packet_has_all_balanced_slots_and_is_not_runnable():
    before = (CORPUS.read_bytes(), REVIEW.read_bytes())
    counts = check_packet()
    register = build_register()
    assert counts == register["counts"]
    assert counts["priority_local_fixes"] == 58
    assert counts["source_ai_verdicts"] == {"supported": 146, "needs_clarification": 43, "revise": 15}
    assert counts["authored"] == counts["human_approved"] == 0
    assert not register["runnable"] and "cases" not in register
    assert not (DESTINATION / "corpus.json").exists()
    assert len({slot["slot_id"] for slot in register["slots"]}) == 204
    assert len({slot["source_case_id"] for slot in register["slots"]}) == 204
    balance = Counter((slot["language"], slot["planned_label"]) for slot in register["slots"])
    assert all(balance[(language, label)] == 6 for language in LANGUAGES for label in ("vulnerable", "safe"))
    for slot in register["slots"]:
        assert slot["status"] == "planned_not_authored" and slot["owner"] is None
        assert slot["authored_case_id"] is None and slot["authored_case_spec_sha256"] is None
        assert slot["human_review"]["status"] == "pending"
        assert slot["human_review"]["reviewer"] is None
        assert slot["replacement_brief"]["new_provenance"] is None
        assert slot["replacement_brief"]["new_derivation_group"] is None
        assert {item["id"] for item in slot["acceptance_checklist"]} == set(CHECKLIST)
        assert all(item["status"] == "pending" and item["evidence"] is None
                   for item in slot["acceptance_checklist"])
        assert {"CR-001", "CR-002"} <= set(slot["required_review_findings"])
    assert before == (CORPUS.read_bytes(), REVIEW.read_bytes())


def test_ai_issues_assumptions_and_hashes_survive_every_handoff():
    register = build_register()
    corpus, review, _ = load_verified_inputs()
    cases = {case["id"]: case for case in corpus["cases"]}
    decisions = {decision["case_id"]: decision for decision in review["cases"]}
    for slot in register["slots"]:
        case, decision = cases[slot["source_case_id"]], decisions[slot["source_case_id"]]
        assert slot["source_content_sha256"] == case["content_sha256"]
        assert slot["source_legacy_review_spec_sha256"] == legacy_review_spec_hash(case)
        assert slot["ai_review"]["issues"] == decision["issues"]
        assert slot["replacement_brief"]["prior_assumptions_to_resolve"] == decision["assumptions"]
        assert slot["replacement_brief"]["prior_constraints_to_resolve"] == case["remediation_constraints"]
        assert decision["independence_group"] in slot["source_derivation_groups"]
        assert all(issue["recommendation"] in slot["replacement_brief"]["case_specific_requirements"]
                   for issue in decision["issues"])


def test_priority_views_are_exactly_the_58_flagged_cases():
    register = build_register()
    views = packet_files(register)
    all_rows = list(csv.DictReader(io.StringIO(views["replacement-register.csv"])))
    priority = list(csv.DictReader(io.StringIO(views["priority-fixes.csv"])))
    assert len(all_rows) == 204 and len(priority) == 58
    expected = {slot["source_case_id"] for slot in register["slots"] if slot["ai_review"]["verdict"] != "supported"}
    assert {row["source_case_id"] for row in priority} == expected
    assert sum(row["ai_verdict"] == "revise" for row in priority) == 15
    assert views["PRIORITY_FIXES.md"].count("\n## ") == 58
    assert all(row["owner"] == "" and row["human_review_status"] == "pending" for row in priority)


@pytest.mark.parametrize("mutation", ["metadata", "source", "review_hash", "language", "label", "duplicate", "missing"])
def test_stale_or_inconsistent_review_inputs_fail_closed(tmp_path, mutation):
    corpus = json.loads(CORPUS.read_text())
    review = json.loads(REVIEW.read_text())
    if mutation == "metadata": corpus["cases"][0]["rationale"] += " changed"
    if mutation == "source": corpus["cases"][0]["files"]["app.py"] += "# changed\n"
    if mutation == "review_hash": review["cases"][0]["case_spec_sha256"] = "0" * 64
    if mutation == "language": review["cases"][0]["language"] = "go"
    if mutation == "label": review["cases"][0]["proposed_vulnerable"] = False
    if mutation == "duplicate": review["cases"][1] = copy.deepcopy(review["cases"][0])
    if mutation == "missing": review["cases"].pop()
    paths = write_inputs(tmp_path, corpus, review)
    with pytest.raises(ValueError):
        build_register(*paths)


def test_exact_original_bytes_remain_required(tmp_path):
    corpus_path, review_path = tmp_path / "corpus.json", tmp_path / "review.json"
    corpus_path.write_bytes(CORPUS.read_bytes() + b"\n")
    review_path.write_bytes(REVIEW.read_bytes())
    with pytest.raises(ValueError, match="bytes differ"):
        build_register(corpus_path, review_path)


@pytest.mark.parametrize("name", ["replacement-register.json", "replacement-register.csv", "priority-fixes.csv", "PRIORITY_FIXES.md"])
def test_changed_generated_view_is_rejected(tmp_path, name):
    for path, content in packet_files(build_register()).items():
        (tmp_path / path).write_bytes(content.encode())
    path = tmp_path / name
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="differs from verified inputs"):
        check_packet(tmp_path)


def test_packet_cannot_masquerade_as_authored_benchmark(tmp_path):
    for path, content in packet_files(build_register()).items():
        (tmp_path / path).write_bytes(content.encode())
    (tmp_path / "corpus.json").write_text('{"cases": []}')
    with pytest.raises(ValueError, match="must not contain"):
        check_packet(tmp_path)


def test_legacy_hash_encoding_is_explicit_and_not_human_approval():
    case = {"id": "synthetic-é", "files": {"app.py": "# π\n"}, "human_review": {"status": "pending"}}
    expected = sha256(json.dumps({key: value for key, value in case.items() if key != "human_review"}, sort_keys=True).encode())
    assert legacy_review_spec_hash(case) == expected
    case["human_review"]["status"] = "approved"
    assert legacy_review_spec_hash(case) == expected
    case["rationale"] = "Changed specification"
    assert legacy_review_spec_hash(case) != expected
