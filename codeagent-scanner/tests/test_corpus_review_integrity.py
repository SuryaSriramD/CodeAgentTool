"""Synthetic approval records exercise integrity; they are never human sign-off.

The real held-out corpus is read only. Approved records exist only in memory or
pytest's temporary directory so no benchmark evidence is manufactured.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

from evaluation import benchmark
from evaluation.corpus_review import (
    REVIEW_SCHEMA_VERSION,
    approval_summary,
    case_review_digest,
    review_errors,
    review_manifest,
)


CORPUS = Path(__file__).parents[1] / "evaluation/corpus-v1/corpus.json"


def synthetic_corpus():
    return json.loads(CORPUS.read_text())


def approve_fixture(corpus, case):
    """Create a clearly synthetic record for a test, never persist to corpus."""
    case["human_review"] = {
        "status": "approved",
        "reviewer_kind": "human",
        "reviewer": "synthetic-unit-test-reviewer",
        "reviewed_at": "2000-01-01T00:00:00+00:00",
        "review_schema_version": REVIEW_SCHEMA_VERSION,
        "reviewed_content_sha256": case["content_sha256"],
        "reviewed_case_sha256": case_review_digest(corpus, case),
    }
    return case


def approved_fixture():
    corpus = synthetic_corpus()
    for case in corpus["cases"]:
        approve_fixture(corpus, case)
    return corpus


def test_complete_case_approval_is_valid_and_pending_corpus_stays_readable():
    corpus = synthetic_corpus()
    assert REVIEW_SCHEMA_VERSION == "2.0"
    assert len(benchmark.validate_corpus(corpus, require_approved=False)) == 204
    assert review_errors(corpus, corpus["cases"][0])
    for case in corpus["cases"]:
        approve_fixture(corpus, case)
    assert not review_errors(corpus, corpus["cases"][0])
    assert len(benchmark.validate_corpus(corpus)) == 204
    assert approval_summary(corpus)["valid_human_approvals"] == 204


@pytest.mark.parametrize("field,changed", [
    ("rationale", "Changed trust boundary without modifying any source."),
    ("remediation_constraints", ["Deleting the protected operation is acceptable."]),
    ("runtime_assumptions", {"framework": "incompatible-major-version"}),
    ("derivation", {"parent": "a-known-training-example"}),
    ("provenance", {"origin": "Copied from rule development fixtures"}),
    ("id", "replacement-case-identity"),
    ("scenario", "Different security contract"),
    ("independence_group", "translated-template-1"),
    ("future_security_relevant_field", {"allowed_destination": "http://internal.invalid"}),
])
def test_same_source_metadata_mutation_invalidates_full_case_approval(field, changed):
    corpus = synthetic_corpus()
    case = approve_fixture(corpus, corpus["cases"][0])
    source_hash = case["content_sha256"]
    before = case_review_digest(corpus, case)
    case[field] = changed
    assert case["content_sha256"] == source_hash
    assert case_review_digest(corpus, case) != before
    assert review_errors(corpus, case)


def test_changing_label_and_expected_findings_together_cannot_reuse_approval():
    corpus = approved_fixture()
    case = next(case for case in corpus["cases"] if case["vulnerable"])
    case["vulnerable"] = False
    case["expected_findings"] = []
    # This mutation remains internally consistent, but changes the reviewed
    # ground truth even though its source bytes and source digest are unchanged.
    assert case["human_review"]["reviewed_content_sha256"] == case["content_sha256"]
    assert review_errors(corpus, case)
    with pytest.raises(ValueError, match="approval"):
        benchmark.validate_corpus(corpus)


@pytest.mark.parametrize("field,value", [
    ("cwe", "CWE-999"),
    ("family", "different-security-family"),
    ("path", "different-file.py"),
])
def test_expected_finding_identity_is_bound_to_approval(field, value):
    corpus = synthetic_corpus()
    case = approve_fixture(corpus, next(case for case in corpus["cases"] if case["vulnerable"]))
    case["expected_findings"][0][field] = value
    assert review_errors(corpus, case)


@pytest.mark.parametrize("field,value", [
    ("version", "heldout-2.0.0-candidate"),
    ("schema_version", "future-schema-version"),
    ("approval_policy", {"allow_automated_approvals": True}),
    ("future_scope_policy", {"include_cross_file_vulnerabilities": False}),
])
def test_corpus_review_context_cannot_change_under_existing_approvals(field, value):
    corpus = synthetic_corpus()
    case = approve_fixture(corpus, corpus["cases"][0])
    corpus[field] = value
    assert review_errors(corpus, case)


def test_dictionary_order_and_human_notes_do_not_change_reviewed_identity():
    corpus = synthetic_corpus()
    case = approve_fixture(corpus, corpus["cases"][0])
    before = case_review_digest(corpus, case)

    def reordered(value):
        if isinstance(value, dict):
            return {key: reordered(value[key]) for key in reversed(list(value))}
        if isinstance(value, list):
            return [reordered(entry) for entry in value]
        return value

    reordered_corpus = reordered(corpus)
    reordered_case = next(entry for entry in reordered_corpus["cases"] if entry["id"] == case["id"])
    assert case_review_digest(reordered_corpus, reordered_case) == before
    case["human_review"]["notes"] = ["Administrative note appended after review."]
    assert case_review_digest(corpus, case) == before
    assert not review_errors(corpus, case)


def test_lists_and_security_relevant_literals_are_not_normalized_away():
    corpus = synthetic_corpus()
    case = corpus["cases"][0]
    case["remediation_constraints"] = ["Preserve output.", "Reject untrusted URLs."]
    case["runtime_assumptions"] = {"allowed_origin": "https://trusted.invalid:443"}
    approve_fixture(corpus, case)
    original = case_review_digest(corpus, case)
    case["remediation_constraints"].reverse()
    assert case_review_digest(corpus, case) != original
    case["remediation_constraints"].reverse()
    assert case_review_digest(corpus, case) == original
    case["runtime_assumptions"]["allowed_origin"] = "http://trusted.invalid:443"
    assert case_review_digest(corpus, case) != original
    assert review_errors(corpus, case)


@pytest.mark.parametrize("field,value", [
    ("status", "pending"),
    ("reviewer_kind", "ai"),
    ("reviewer_kind", None),
    ("reviewer", "   "),
    ("reviewed_at", "unit-test-time"),
    ("reviewed_at", "2026-02-30T00:00:00+00:00"),
    ("reviewed_at", None),
    ("review_schema_version", "1.0"),
    ("reviewed_content_sha256", "0" * 64),
    ("reviewed_case_sha256", "0" * 64),
])
def test_incomplete_or_nonhuman_attestations_fail_closed(field, value):
    corpus = synthetic_corpus()
    case = approve_fixture(corpus, corpus["cases"][0])
    case["human_review"][field] = value
    assert review_errors(corpus, case)


def test_legacy_source_only_approval_cannot_freeze_but_remains_auditable():
    corpus = approved_fixture()
    case = corpus["cases"][0]
    case["human_review"] = {
        "status": "approved",
        "reviewer": "synthetic-legacy-reviewer",
        "reviewed_at": "2000-01-01T00:00:00+00:00",
        "reviewed_content_sha256": case["content_sha256"],
    }
    assert len(benchmark.validate_corpus(corpus, require_approved=False)) == 204
    assert review_errors(corpus, case)
    summary = approval_summary(corpus)
    assert summary["valid_human_approvals"] == 203
    assert summary["legacy_source_only_approvals"] == 1
    assert summary["stale_or_invalid_approvals"] == 1
    assert summary["pending_human_reviews"] == 0
    with pytest.raises(ValueError, match="approval"):
        benchmark.freeze(corpus, {"provider": "ollama", "model": "synthetic-model"}, {})


def test_summary_distinguishes_pending_stale_legacy_and_valid():
    corpus = synthetic_corpus()
    approved = approve_fixture(corpus, corpus["cases"][0])
    stale = approve_fixture(corpus, corpus["cases"][1])
    stale["rationale"] += " Changed after approval."
    legacy = corpus["cases"][2]
    legacy["human_review"] = {
        "status": "approved", "reviewer": "synthetic-legacy-reviewer",
        "reviewed_at": "2000-01-01", "reviewed_content_sha256": legacy["content_sha256"],
    }
    assert not review_errors(corpus, approved)
    assert approval_summary(corpus) == {
        "valid_human_approvals": 1,
        "pending_human_reviews": 201,
        "stale_or_invalid_approvals": 2,
        "legacy_source_only_approvals": 1,
    }


def test_freeze_rejects_stale_approval_before_environment_or_model_access(monkeypatch):
    corpus = approved_fixture()
    corpus["cases"][0]["rationale"] += " Changed after approval."

    def forbidden(*args, **kwargs):
        pytest.fail("Stale approvals must fail before environment/model work")

    monkeypatch.setattr(benchmark, "environment_identity", forbidden)
    with pytest.raises(ValueError, match="approval"):
        benchmark.freeze(corpus, {"provider": "ollama", "model": "synthetic-model"}, {})


def test_run_rejects_stale_approval_before_any_api_request(tmp_path):
    corpus = approved_fixture()
    corpus["cases"][0]["rationale"] += " Changed after approval."

    class ForbiddenAPI:
        def request(self, *args, **kwargs):
            pytest.fail("Stale approvals must fail before any API request")

    with pytest.raises(ValueError, match="approval"):
        benchmark.run(corpus, {}, tmp_path / "never-created", ForbiddenAPI())
    assert not (tmp_path / "never-created").exists()


@pytest.mark.parametrize("command", ["freeze", "run"])
def test_cli_preflight_rejects_stale_approval_before_constructing_api(monkeypatch, tmp_path, command):
    corpus = approved_fixture()
    corpus["cases"][0]["remediation_constraints"].append("An unreviewed change.")
    corpus_file = tmp_path / "synthetic-stale-corpus.json"
    corpus_file.write_text(json.dumps(corpus))
    output = tmp_path / "no-benchmark-output"
    flag = "--config" if command == "freeze" else "--freeze"
    # These files intentionally do not exist: approval preflight must happen first.
    monkeypatch.setattr(sys, "argv", ["benchmark", "--corpus", str(corpus_file), command,
                                      flag, str(tmp_path / "absent.json"), "--output", str(output)])

    def forbidden(*args, **kwargs):
        pytest.fail("Stale approvals must fail before an API client is created")

    monkeypatch.setattr(benchmark, "API", forbidden)
    with pytest.raises(ValueError, match="approval"):
        benchmark.main()
    assert not output.exists()


def test_review_manifest_is_unsigned_deterministic_and_does_not_approve_input():
    corpus = synthetic_corpus()
    before = copy.deepcopy(corpus)
    manifest = review_manifest(corpus)
    assert manifest == review_manifest(corpus)
    assert corpus == before
    serialized = json.dumps(manifest, sort_keys=True)
    for case in corpus["cases"]:
        assert case["id"] in serialized
        assert case["content_sha256"] in serialized
        assert case_review_digest(corpus, case) in serialized
    assert '"approved"' not in serialized
    assert approval_summary(corpus)["valid_human_approvals"] == 0
    with pytest.raises(ValueError, match="approval"):
        benchmark.validate_corpus(corpus)


def test_manifest_never_copies_attestations_from_previously_approved_input():
    corpus = approved_fixture()
    before = copy.deepcopy(corpus)
    manifest = review_manifest(corpus)
    assert corpus == before
    assert len(manifest["cases"]) == 204
    by_id = {case["id"]: case for case in corpus["cases"]}
    for entry in manifest["cases"]:
        case = by_id[entry["case_id"]]
        assert entry["content_sha256"] == case["content_sha256"]
        assert entry["case_spec_sha256"] == case_review_digest(corpus, case)
        assert entry["specification"] == {key: value for key, value in case.items() if key != "human_review"}
        review = entry["human_review"]
        assert review["status"] == "pending"
        assert review["review_schema_version"] == REVIEW_SCHEMA_VERSION
        assert all(review[field] is None for field in (
            "reviewer_kind", "reviewer", "reviewed_at", "reviewed_content_sha256", "reviewed_case_sha256",
        ))


def test_matching_case_digest_cannot_hide_stale_source_snapshot_hash():
    corpus = synthetic_corpus()
    case = approve_fixture(corpus, corpus["cases"][0])
    path = next(iter(case["files"]))
    case["files"][path] += "\n# Unreviewed source change.\n"
    # Even if someone updates the full-case digest, the separate source anchor
    # must still be recomputed from actual bytes, not trusted from metadata.
    case["human_review"]["reviewed_case_sha256"] = case_review_digest(corpus, case)
    errors = review_errors(corpus, case)
    assert any("source" in error for error in errors)
    assert approval_summary(corpus)["valid_human_approvals"] == 0


@pytest.mark.parametrize("review", [None, "approved", [], {"status": "approved", "reviewer": 42}])
def test_malformed_review_records_are_reported_without_crashing(review):
    corpus = synthetic_corpus()
    case = corpus["cases"][0]
    case["human_review"] = review
    errors = review_errors(corpus, case)
    assert errors and all(isinstance(error, str) and error.strip() for error in errors)
    assert approval_summary(corpus)["valid_human_approvals"] == 0


def test_manifest_cli_is_offline_and_cannot_overwrite_human_work(monkeypatch, tmp_path, capsys):
    output = tmp_path / "review" / "unsigned-packet.json"
    original_corpus_bytes = CORPUS.read_bytes()
    monkeypatch.setattr(sys, "argv", ["benchmark", "--corpus", str(CORPUS), "review-manifest",
                                      "--output", str(output)])

    def forbidden(*args, **kwargs):
        pytest.fail("Review manifests must not create API clients or model requests")

    monkeypatch.setattr(benchmark, "API", forbidden)
    benchmark.main()
    manifest = json.loads(output.read_text())
    assert len(manifest["cases"]) == 204
    assert all(entry["human_review"]["status"] == "pending" for entry in manifest["cases"])
    assert json.loads(capsys.readouterr().out)["status"] == "unsigned_pending_human_review"

    manifest["cases"][0]["human_review"]["notes"] = "Human work in progress: preserve this note."
    output.write_text(json.dumps(manifest))
    human_work = output.read_bytes()
    with pytest.raises(FileExistsError):
        benchmark.main()
    assert output.read_bytes() == human_work
    assert CORPUS.read_bytes() == original_corpus_bytes
