"""Offline identities for human corpus review; never creates an approval.

The digest detects changes to the reviewed specification. It is an attestation
record, not a signature or proof of a reviewer's identity or independence.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import date, datetime

REVIEW_SCHEMA_VERSION = "2.0"
REVIEW_DOMAIN = "codeagent.corpus-case-review"


def source_digest(files):
    """Preserve the original snapshot-hash encoding for historical reports."""
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def corpus_review_context(corpus):
    # Status is administrative. Unknown future fields are bound by default so
    # new runtime defaults or evaluation policies cannot bypass prior reviews.
    return {key: value for key, value in corpus.items() if key not in {"cases", "status"}}


def case_review_digest(corpus, case):
    payload = {
        "domain": REVIEW_DOMAIN,
        "review_schema_version": REVIEW_SCHEMA_VERSION,
        "corpus_context": corpus_review_context(corpus),
        "case": {key: value for key, value in case.items() if key != "human_review"},
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _review_date(value):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        return False
    try:
        # A calendar review date or an ISO timestamp is valid review metadata.
        if len(value) == 10:
            date.fromisoformat(value)
        else:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def review_errors(corpus, case):
    """Explain why this exact specification lacks a current human approval."""
    review = case.get("human_review")
    if not isinstance(review, dict):
        return ["independent human approval is missing"]
    errors = []
    if review.get("status") != "approved":
        errors.append("independent human approval is pending")
    if review.get("reviewer_kind") != "human":
        errors.append("reviewer_kind must explicitly attest human review")
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        errors.append("a named independent human reviewer is required")
    if not _review_date(review.get("reviewed_at")):
        errors.append("reviewed_at must be an ISO review date or timestamp")
    if review.get("review_schema_version") != REVIEW_SCHEMA_VERSION:
        errors.append("review schema 2.0 is required; legacy source-only approvals need re-review")
    current_source = source_digest(case.get("files") or {})
    if case.get("content_sha256") != current_source:
        errors.append("source content does not match the recorded snapshot hash")
    if review.get("reviewed_content_sha256") != current_source:
        errors.append("reviewed source hash is missing or stale")
    if review.get("reviewed_case_sha256") != case_review_digest(corpus, case):
        errors.append("reviewed case specification hash is missing or stale; human re-review is required")
    return errors


def approval_summary(corpus):
    result = {"valid_human_approvals": 0, "pending_human_reviews": 0,
              "stale_or_invalid_approvals": 0, "legacy_source_only_approvals": 0}
    for case in corpus.get("cases", []):
        review = case.get("human_review") or {}
        if not isinstance(review, dict) or review.get("status") != "approved":
            result["pending_human_reviews"] += 1
        elif review_errors(corpus, case):
            result["stale_or_invalid_approvals"] += 1
            if not review.get("review_schema_version") and not review.get("reviewed_case_sha256"):
                result["legacy_source_only_approvals"] += 1
        else:
            result["valid_human_approvals"] += 1
    return result


def review_manifest(corpus):
    """Prepare a deterministic unsigned packet without copying approvals."""
    result = {
        "review_schema_version": REVIEW_SCHEMA_VERSION,
        "status": "unsigned_pending_human_review",
        "corpus_context": copy.deepcopy(corpus_review_context(corpus)),
        "instructions": (
            "Inspect every case's complete specification and independence. The identity fields below "
            "are not approval. Only the independent human reviewer may record an approval, name, "
            "date and reviewed hashes. Do not put runtime assumptions or remediation requirements "
            "inside human_review notes; those belong in the hashed specification."
        ),
        "checklist": [
            "Verify source semantics, trust boundary, label and all expected findings.",
            "Verify runtime/driver assumptions and legitimate input/output behavior.",
            "Verify acceptable remediation and migration constraints.",
            "Verify provenance, derivation groups and conceptual independence.",
            "Resolve all corpus-wide release blockers before approving a benchmark freeze.",
        ],
        "cases": [],
    }
    for case in corpus.get("cases", []):
        result["cases"].append({
            "case_id": case["id"], "content_sha256": source_digest(case["files"]),
            "case_spec_sha256": case_review_digest(corpus, case),
            "specification": copy.deepcopy({key: value for key, value in case.items()
                                            if key != "human_review"}),
            "human_review": {"status": "pending", "reviewer_kind": None,
                             "reviewer": None, "reviewed_at": None, "notes": None,
                             "review_schema_version": REVIEW_SCHEMA_VERSION,
                             "reviewed_content_sha256": None, "reviewed_case_sha256": None},
        })
    return result
