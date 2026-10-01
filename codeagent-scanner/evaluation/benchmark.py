"""Human-gated, resumable evaluation through the ordinary API and worker.

Nothing in this module executes a corpus source file. Held-out labels are kept out
of scan/review inputs. Starting a benchmark requires an approved, frozen corpus.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import random
import statistics
import time
import uuid
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import httpx

from evaluation.corpus_review import (_review_date, approval_summary, review_errors, review_manifest,
                                     source_digest)
from integration.workflow import WORKFLOW_VERSION, ANALYST, AUTHOR, REVIEWER, implementation_digest
from pipeline.contracts import ReviewConfig

LANGUAGES = {"python", "javascript", "typescript", "java", "go", "c", "cpp", "ruby", "php",
             "scala", "kotlin", "swift", "csharp", "fsharp", "visualbasic", "rust", "bash"}
MODES = ("static", "single_agent", "multi_agent")
TERMINAL = {"completed", "partial", "failed", "canceled", "interrupted"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def load_json(path):
    return json.loads(Path(path).read_text())


def corpus_content_hash(files):
    # Matches the corpus provenance encoding, independent of approval metadata.
    return source_digest(files)


def validate_corpus(corpus, *, require_approved=True):
    cases = corpus.get("cases", [])
    if len(cases) != 204:
        raise ValueError("Release corpus requires 204 cases")
    if require_approved:
        for concern in corpus.get("review_concerns", []):
            if (concern.get("status") != "resolved" or concern.get("reviewer_kind") != "human"
                    or not isinstance(concern.get("reviewer"), str) or not concern["reviewer"].strip()
                    or not isinstance(concern.get("resolution"), str) or not concern["resolution"].strip()
                    or not _review_date(concern.get("reviewed_at"))):
                raise ValueError("Corpus-wide review concerns need a named human resolution before case approval and freeze")
    ids, sources, counts = set(), set(), Counter()
    for case in cases:
        if case.get("id") in ids or not case.get("id"):
            raise ValueError("Corpus IDs must be unique")
        ids.add(case["id"])
        if case.get("language") not in LANGUAGES or type(case.get("vulnerable")) is not bool:
            raise ValueError("Unknown language or non-boolean label")
        counts[(case["language"], case["vulnerable"])] += 1
        files = case.get("files") or {}
        if not files:
            raise ValueError("Each case requires source files")
        for name, content in files.items():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or not isinstance(content, str):
                raise ValueError("Corpus source path must be a contained relative text file")
        source_digest = corpus_content_hash(files)
        if source_digest != case.get("content_sha256") or source_digest in sources:
            raise ValueError("Case content hash changed or duplicates another case")
        sources.add(source_digest)
        if not case.get("provenance") or not case.get("rationale") or not case.get("remediation_constraints"):
            raise ValueError("Provenance, rationale and remediation constraints are required")
        if case.get("split") != "held_out":
            raise ValueError("Release corpus must remain held out")
        if bool(case.get("expected_findings")) != case["vulnerable"]:
            raise ValueError("Expected findings disagree with case label")
        if require_approved and (errors := review_errors(corpus, case)):
            raise ValueError(f"Case {case['id']} needs independent human approval of its exact "
                             f"specification: {'; '.join(errors)}")
    if any(counts[(language, state)] != 6 for language in LANGUAGES for state in (True, False)):
        raise ValueError("Each language requires six vulnerable and six safe cases")
    return cases


def environment_identity(capabilities, provider, model, profile):
    implementation = capabilities.get("workflow") or {}
    if implementation.get("version") != WORKFLOW_VERSION or implementation.get("implementation_hash") != implementation_digest():
        raise ValueError("Deployed workflow differs from this benchmark implementation")
    providers = capabilities.get("providers", {})
    selected = providers.get(provider) or {}
    if not selected.get("available"):
        raise ValueError("Selected provider is unavailable")
    if provider == "ollama":
        model_identity = (selected.get("model_digests") or {}).get(model)
        if not model_identity:
            raise ValueError("A concrete installed Ollama model digest is required")
    else:
        # Hosted aliases are not reproducible model identities. Require the
        # operator to select a dated snapshot, recorded with each response model.
        import re
        if not re.search(r"-\d{4}-\d{2}-\d{2}$", model):
            raise ValueError("Cloud benchmarks require a dated model snapshot ID")
        model_identity = model
    tools = capabilities.get("analyzers", [])
    if not tools or not all(tool.get("available") for tool in tools):
        raise ValueError("Every configured scanner must be available before benchmark freeze")
    profiles = capabilities.get("profile_digests") or {}
    profile_identity = profiles.get(profile)
    if not profile_identity:
        for entry in capabilities.get("profiles", []):
            if entry.get("id") == profile:
                profile_identity = entry.get("digests") or entry.get("profile_digests")
    if not profile_identity or not profile_identity.get("source"):
        raise ValueError("Capabilities must expose exact source/dependency profile digests")
    return {"model": model, "provider": provider, "model_identity": model_identity,
            "tools": [{key: tool.get(key) for key in ("id", "name", "version", "rulepack_version")} for tool in tools],
            "profile": profile, "workflow": implementation, "profile_digests": {key: profile_identity.get(key) for key in ("source", "dependency")}}


def freeze(corpus, config, capabilities, *, profile="security-v2", allow_cloud=False):
    validate_corpus(corpus)
    validated = ReviewConfig.model_validate(config).model_dump()
    validated.pop("workflow_mode", None)
    if not validated.get("model"):
        raise ValueError("Select an explicit model")
    if validated["provider"] != "ollama" and not allow_cloud:
        raise ValueError("Cloud evaluation requires --allow-cloud explicitly")
    identity = environment_identity(capabilities, validated["provider"], validated["model"], profile)
    frozen = {"schema_version": "1.0", "corpus_hash": digest(corpus), "corpus_version": corpus["version"],
              "config": validated, "environment": identity, "workflow_version": WORKFLOW_VERSION,
              "prompt_hash": digest([ANALYST, AUTHOR, REVIEWER]), "repetitions": 3,
              "created_at": now(), "origin": "recorded", "held_out": True,
              "model_parameters": {"temperature": 0.1 if validated["provider"] == "ollama" else "provider-default",
                                   "max_output_tokens": validated["max_output_tokens"]}}
    frozen["freeze_hash"] = digest(frozen)
    return frozen


def verify_freeze(corpus, frozen, capabilities, allow_cloud=False):
    validate_corpus(corpus)
    unsigned = {key: value for key, value in frozen.items() if key != "freeze_hash"}
    if digest(unsigned) != frozen.get("freeze_hash") or frozen.get("corpus_hash") != digest(corpus):
        raise ValueError("Frozen corpus/configuration was changed")
    if frozen.get("repetitions") != 3 or frozen.get("workflow_version") != WORKFLOW_VERSION or frozen.get("prompt_hash") != digest([ANALYST, AUTHOR, REVIEWER]):
        raise ValueError("Workflow or prompt identity changed; create a newly reviewed benchmark version")
    config = frozen["config"]
    if config["provider"] != "ollama" and not allow_cloud:
        raise ValueError("Cloud evaluation requires --allow-cloud on every start/resume")
    identity = environment_identity(capabilities, config["provider"], config["model"], frozen["environment"]["profile"])
    if identity != frozen["environment"]:
        raise ValueError("Model, tools, or rule/database profile changed since freeze")


def make_zip(case):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(case["files"].items()):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    return out.getvalue()


def flatten(report):
    return [{**finding, "file": group["path"]} for group in report.get("files", []) for finding in group.get("issues", [])]


def matches_expected(finding, expected):
    cw = finding.get("cwe") or finding.get("cwes") or []
    cw = [cw] if isinstance(cw, (str, int)) else cw
    normalized = {"CWE-" + str(value).removeprefix("CWE-") for value in cw}
    family = finding.get("vulnerability_family") or finding.get("family") or finding.get("type")
    family = {"weak-crypto": "weak-cryptography", "binary-formatter": "unsafe-deserialization", "xml-dtd": "unsafe-xml"}.get(family, family)
    return any(finding.get("file") == target["path"] and
               (target.get("cwe") in normalized or family == target.get("family")) for target in expected)


def observe(case, mode, report, status, latency_ms):
    findings = flatten(report)
    ai = report.get("ai_analysis") or {}
    # Only an explicit evidence-backed false-positive triage can remove a
    # scanner result. Missing/interrupted/needs-context decisions preserve it.
    dismissed = {entry["finding_id"] for entry in ai.get("triage", [])
                 if entry.get("disposition") == "false_positive" and entry.get("evidence")}
    retained = [entry for entry in findings if mode == "static" or entry["id"] not in dismissed]
    matched = [entry for entry in retained if matches_expected(entry, case["expected_findings"])]
    positive = bool(matched) if case["vulnerable"] else bool(retained)
    usage = ai.get("usage") or {}
    return {"positive": positive, "retained_finding_ids": [entry["id"] for entry in retained],
            "matched_finding_ids": [entry["id"] for entry in matched],
            "unrelated_findings": len(retained) - len(matched), "status": status,
            "incomplete": status != "completed" or ai.get("usage_source") == "persisted_model_steps" or any(c.get("status") not in {"completed", "skipped"} for c in report.get("coverage", [])),
            "latency_ms": latency_ms, "tokens": usage.get("total_tokens", 0),
            "usage_complete": usage.get("usage_complete", mode == "static"), "usage": usage,
            "proposals": ai.get("proposals", []), "errors": ai.get("errors", []),
            "report_hash": digest(report), "actual_provider": ai.get("provider"), "actual_model": ai.get("model")}


def checkpoint_analysis(job, config):
    """Preserve known paid usage when a review artifact was never published.

    Step ledgers already include retry attempts; summing each durable model step
    once preserves those costs. Author outputs alone are not validated proposals.
    """
    steps = [step for step in job.get("steps", [])
             if step.get("role") in {"analyst", "author", "reviewer"}]
    usage = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0,
             "total_tokens": 0, "accounted_tokens": 0, "usage_complete": bool(steps)}
    actual_model, actual_provider = config.get("model"), config.get("provider")
    for step in steps:
        ledger = step.get("usage") or {}
        for field in ("input_tokens", "output_tokens", "total_tokens"):
            value = ledger.get(field)
            if type(value) is int and value >= 0:
                usage[field] += value
            else:
                usage["usage_complete"] = False
        calls = ledger.get("model_calls", 1)
        if type(calls) is int and calls >= 0:
            usage["model_calls"] += calls
        else:
            usage["usage_complete"] = False
        accounted = ledger.get("accounted_tokens")
        if type(accounted) is not int or accounted < 0:
            accounted = ledger.get("total_tokens")
        if type(accounted) is not int or accounted < 0:
            accounted = step.get("reserved_tokens", 0)
        if type(accounted) is int and accounted >= 0:
            usage["accounted_tokens"] += accounted
        if ledger.get("usage_complete") is False or step.get("status") in {"running", "interrupted", "cancelled"}:
            usage["usage_complete"] = False
        actual_provider = step.get("provider") or actual_provider
        actual_model = ledger.get("effective_model") or step.get("model") or actual_model
    return {"status": job.get("status", "failed"), "provider": actual_provider, "model": actual_model,
            "usage": usage, "triage": [], "proposals": [],
            "errors": [{"code": "missing_review_artifact", "message": job.get("error") or "No review artifact; usage recovered from saved steps"}],
            "usage_source": "persisted_model_steps"}


class API:
    def __init__(self, base_url):
        headers = {}
        if token := os.getenv("CODEAGENT_TOKEN"):
            headers["Authorization"] = "Bearer " + token
        self.client = httpx.Client(base_url=base_url.rstrip("/"), headers=headers, timeout=90, follow_redirects=False)
        if password := os.getenv("CODEAGENT_PASSWORD"):
            self.request("POST", "/auth/login", json={"password": password})

    def request(self, method, path, **kwargs):
        response = self.client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    def wait(self, job_id):
        while True:
            job = self.request("GET", f"/jobs/{job_id}")
            if job["status"] in TERMINAL:
                return job
            time.sleep(2)


def run(corpus, frozen, output_dir, api, *, allow_cloud=False, limit_cases=None):
    validate_corpus(corpus)  # Reject stale approvals before even requesting capabilities.
    verify_freeze(corpus, frozen, api.request("GET", "/capabilities"), allow_cloud)
    output = Path(output_dir)
    state_path = output / "observations.json"
    state = load_json(state_path) if state_path.exists() else {
        "origin": "recorded", "freeze_hash": frozen["freeze_hash"], "corpus_hash": frozen["corpus_hash"],
        "records": [], "scans": {}, "environment": frozen["environment"], "config": frozen["config"], "created_at": now()}
    if state.get("freeze_hash") != frozen["freeze_hash"]:
        raise ValueError("Output directory belongs to another benchmark")
    if "project_id" not in state:
        project = api.request("POST", "/projects", json={"name": "Benchmark " + frozen["freeze_hash"][:12]})
        state["project_id"] = project.get("id") or project.get("project_id")
        write_json(state_path, state)
    selected = corpus["cases"][:limit_cases] if limit_cases else corpus["cases"]
    for case in selected:
        verify_freeze(corpus, frozen, api.request("GET", "/capabilities"), allow_cloud)
        case_id = case["id"]
        if case_id not in state["scans"]:
            scan = api.request("POST", "/analyze", data={"mode": "static", "profile": frozen["environment"]["profile"],
                               "project_id": state["project_id"], "stream": "evaluation", "timeout_sec": "600"},
                               files={"file": (case_id + ".zip", make_zip(case), "application/zip")})
            state["scans"][case_id] = {"job_id": scan["job_id"], "started_at": now()}
            write_json(state_path, state)
        scan = state["scans"][case_id]
        if "report" not in scan:
            job = api.wait(scan["job_id"])
            try:
                report = api.request("GET", f"/reports/{scan['job_id']}")
            except httpx.HTTPStatusError as error:
                if error.response.status_code != 404:
                    raise
                report = {"files": [], "coverage": [], "errors": [job.get("error") or "Static scan failed"]}
            profile = report.get("profile_digests") or report.get("meta", {}).get("profile_digests")
            expected = frozen["environment"]["profile_digests"]
            if profile and any(profile.get(key) != value for key, value in expected.items()):
                raise ValueError("Scan profile differs from frozen benchmark")
            scan.update(report=report, status=job["status"], report_hash=digest(report),
                        latency_ms=elapsed_ms(job, scan["started_at"]))
            write_json(output / "artifacts" / f"{case_id}-static.json", report)
            write_json(state_path, state)
        for repetition in range(3):
            for mode in MODES:
                identity = (case_id, mode, repetition)
                record = next((r for r in state["records"] if (r["case_id"], r["mode"], r["repetition"]) == identity), None)
                if record and record.get("finished_at"):
                    continue
                if record is None:
                    record = {"case_id": case_id, "mode": mode, "repetition": repetition,
                              "source_hash": case["content_sha256"], "input_report_hash": scan["report_hash"], "started_at": now()}
                    state["records"].append(record)
                    write_json(state_path, state)
                if mode == "static" or scan["status"] not in {"completed", "partial"}:
                    observation = observe(case, mode, scan["report"], scan["status"], scan["latency_ms"])
                    if mode != "static":
                        observation.update(status="failed", incomplete=True, errors=["No usable static report"])
                else:
                    if not record.get("job_id"):
                        body = {**frozen["config"], "workflow_mode": mode}
                        submitted = api.request("POST", f"/reports/{scan['job_id']}/enhance", json=body)
                        record["job_id"] = submitted["job_id"]
                        write_json(state_path, state)  # Persist ID before waiting; resume never submits it twice.
                    job = api.wait(record["job_id"])
                    try:
                        reviewed = api.request("GET", f"/reviews/{record['job_id']}")
                    except httpx.HTTPStatusError as error:
                        if error.response.status_code != 404:
                            raise
                        reviewed = {**scan["report"], "ai_analysis": checkpoint_analysis(job, frozen["config"])}
                    observation = observe(case, mode, reviewed, job["status"], elapsed_ms(job, record["started_at"]))
                    write_json(output / "artifacts" / f"{case_id}-{mode}-{repetition}.json", reviewed)
                if mode != "static":
                    verify_freeze(corpus, frozen, api.request("GET", "/capabilities"), allow_cloud)
                record.update(observation, finished_at=now())
                write_json(state_path, state)
    state["finished_cases"] = len(selected)
    state["collection_complete"] = len(state["records"]) == len(corpus["cases"]) * 9 and all(r.get("finished_at") for r in state["records"])
    write_json(state_path, state)
    return state


def elapsed_ms(job, fallback):
    start = datetime.fromisoformat(job.get("started_at") or fallback)
    end = datetime.fromisoformat(job.get("finished_at") or now())
    return max(0, round((end-start).total_seconds()*1000))


def blind_sheets(corpus, observations, output_dir):
    output = Path(output_dir)
    mapping_file = output / "private-review-map.json"
    if mapping_file.exists():
        raise ValueError("Review mapping exists; preserve it and resume existing human sheets")
    cases = {case["id"]: case for case in corpus["cases"]}
    sheets, mapping = [], {}
    for row in observations["records"]:
        if row["mode"] == "static":
            continue
        for proposal in row.get("proposals", []):
            identifier = str(uuid.uuid4())
            case = cases[row["case_id"]]
            mapping[identifier] = {"case_id": row["case_id"], "mode": row["mode"], "repetition": row["repetition"],
                                   "proposal_id": proposal["id"], "proposal_hash": digest(proposal)}
            sheets.append({"blind_id": identifier, "source": case["files"], "remediation_constraints": case["remediation_constraints"],
                           "diff": proposal.get("diff"), "explanation": proposal.get("explanation"),
                           "validation": proposal.get("validation"), "decision": "pending", "reviewer": None,
                           "reviewed_at": None, "reason": None})
    random.SystemRandom().shuffle(sheets)
    write_json(mapping_file, {"freeze_hash": observations["freeze_hash"], "mapping": mapping})
    mapping_file.chmod(0o600)
    write_json(output / "blinded-review-sheets.json", {"instructions": "Independently assess correctness and preserved behavior. Do not consult the private mode mapping before scoring.", "items": sheets})
    return len(sheets)


def merge_human_scores(observations, mapping, sheets):
    if mapping["freeze_hash"] != observations["freeze_hash"]:
        raise ValueError("Human review belongs to another frozen benchmark")
    scores = {}
    seen = set()
    for sheet in sheets["items"]:
        identifier = sheet["blind_id"]
        if identifier not in mapping["mapping"] or identifier in seen:
            raise ValueError("Unknown or duplicate blinded review")
        seen.add(identifier)
        entry = mapping["mapping"][identifier]
        if sheet.get("decision") not in {"accepted", "rejected"} or not all(sheet.get(key) for key in ("reviewer", "reviewed_at", "reason")):
            raise ValueError("Every proposal needs an independent recorded human decision")
        scores[(entry["case_id"], entry["mode"], entry["repetition"], entry["proposal_id"])] = {**sheet, "proposal_hash": entry["proposal_hash"]}
    if seen != set(mapping["mapping"]):
        raise ValueError("Some blinded proposal reviews are missing")
    return scores


def _quantile(values, probability):
    values = sorted(values)
    if not values:
        return None
    position = (len(values)-1)*probability
    lower = int(position)
    return values[lower] + (values[min(lower+1, len(values)-1)]-values[lower])*(position-lower)


def score(corpus, frozen, observations, human_scores, *, bootstrap_samples=4000):
    validate_corpus(corpus)
    if digest({key: value for key, value in frozen.items() if key != "freeze_hash"}) != frozen.get("freeze_hash") or frozen.get("corpus_hash") != digest(corpus):
        raise ValueError("Frozen benchmark identity is invalid")
    if (observations.get("origin") != "recorded" or observations.get("freeze_hash") != frozen.get("freeze_hash")
            or observations.get("corpus_hash") != digest(corpus)):
        raise ValueError("Only recorded observations from this exact frozen corpus can satisfy a gate")
    labels = {case["id"]: case["vulnerable"] for case in corpus["cases"]}
    expected = {(case, mode, repetition) for case in labels for mode in MODES for repetition in range(3)}
    rows = {}
    for original in observations.get("records", []):
        row = dict(original)
        key = (row["case_id"], row["mode"], row["repetition"])
        if key not in expected or key in rows or not row.get("finished_at") or type(row.get("positive")) is not bool:
            raise ValueError("Unknown, duplicated or unfinished observation")
        successful = False
        for proposal in row.get("proposals", []):
            review = human_scores.get((*key, proposal["id"]))
            if review is None or review.get("proposal_hash") != digest(proposal):
                raise ValueError("Proposal lacks a matching independent human review")
            # A passed static result alone or an LLM review alone never qualifies.
            successful |= (review["decision"] == "accepted" and proposal.get("status") == "reviewed"
                           and proposal.get("validation", {}).get("status") == "passed"
                           and bool(set(proposal.get("finding_ids", [])) & set(row.get("matched_finding_ids", [])))
                           and not row.get("incomplete") and row.get("status") == "completed")
        row["successful_fix"] = successful and labels[row["case_id"]]
        rows[key] = row
    if set(rows) != expected:
        raise ValueError("A complete benchmark needs three observations per case and mode")
    metrics = {}
    for mode in MODES:
        items = [row for (case, m, rep), row in rows.items() if m == mode]
        vulnerable = [row for row in items if labels[row["case_id"]]]
        safe = [row for row in items if not labels[row["case_id"]]]
        metrics[mode] = {"cases": len(items), "false_positives": sum(row["positive"] for row in safe),
            "true_positives": sum(row["positive"] for row in vulnerable),
            "false_negatives": sum(not row["positive"] for row in vulnerable),
            "recall": sum(row["positive"] for row in vulnerable)/len(vulnerable),
            "accepted_validated_fix_rate": sum(row["successful_fix"] for row in vulnerable)/len(vulnerable),
            "failures_or_incomplete": sum(bool(row.get("incomplete")) for row in items),
            "median_latency_ms": statistics.median(row["latency_ms"] for row in items),
            "p95_latency_ms": _quantile([row["latency_ms"] for row in items], .95),
            "reported_tokens": sum(row["tokens"] for row in items),
            "usage_complete": all(row.get("usage_complete") for row in items)}
    single, multi = metrics["single_agent"], metrics["multi_agent"]
    fix_delta = multi["accepted_validated_fix_rate"] - single["accepted_validated_fix_rate"]
    fp_reduction = 1-multi["false_positives"]/single["false_positives"] if single["false_positives"] else None
    # Paired, language-stratified cluster bootstrap. Repetitions of a case are
    # sampled together, avoiding pseudoreplication of the three model runs.
    rng = random.Random(20260925)
    buckets = {}
    for case in corpus["cases"]:
        buckets.setdefault((case["language"], case["vulnerable"]), []).append(case["id"])
    boot = {"fix_difference": [], "false_positive_rate_difference": [], "recall_difference": []}
    for _ in range(bootstrap_samples):
        sampled = [rng.choice(ids) for ids in buckets.values() for _ in range(len(ids))]
        deltas = {name: [] for name in boot}
        for case in sampled:
            a = [rows[(case, "single_agent", rep)] for rep in range(3)]
            b = [rows[(case, "multi_agent", rep)] for rep in range(3)]
            if labels[case]:
                deltas["fix_difference"].append(sum(y["successful_fix"]-x["successful_fix"] for x,y in zip(a,b))/3)
                deltas["recall_difference"].append(sum(y["positive"]-x["positive"] for x,y in zip(a,b))/3)
            else:
                deltas["false_positive_rate_difference"].append(sum(x["positive"]-y["positive"] for x,y in zip(a,b))/3)
        for name, values in deltas.items():
            boot[name].append(statistics.mean(values))
    intervals = {name: [_quantile(values,.025), _quantile(values,.975)] for name,values in boot.items()}
    reasons = []
    if fix_delta < .10 - 1e-12: reasons.append("Accepted validated fix improvement is below 10 percentage points")
    if fp_reduction is None: reasons.append("Single-agent false positives are zero; reduction is inconclusive")
    elif fp_reduction < .20 - 1e-12: reasons.append("False-positive reduction is below 20 percent")
    if multi["recall"] < single["recall"]: reasons.append("Vulnerability recall decreased")
    if intervals["fix_difference"][0] <= 0 or intervals["false_positive_rate_difference"][0] <= 0:
        reasons.append("Paired confidence intervals do not establish improvement beyond sampling noise")
    if any(metrics[mode]["failures_or_incomplete"] for mode in MODES):
        reasons.append("Some recorded cases have incomplete operational evidence")
    return {"release_status": "candidate" if reasons else "quality_gate_passed", "origin": "recorded",
            "freeze_hash": frozen["freeze_hash"], "metrics": metrics,
            "accepted_fix_improvement_percentage_points": fix_delta*100,
            "false_positive_relative_reduction": fp_reduction,
            "paired_95_percent_intervals": intervals, "bootstrap": {"samples": bootstrap_samples,
            "method": "language/label-stratified paired case-cluster bootstrap", "seed": 20260925},
            "gate_reasons": reasons, "environment": frozen["environment"], "config": frozen["config"],
            "limitations": "Human labels and proposal decisions are required. Static validation is not execution or proof of security."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--corpus", type=Path, default=Path(__file__).parent / "corpus-v1/corpus.json")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("audit")
    manifest_args = commands.add_parser("review-manifest", help="Prepare an unsigned offline human review packet")
    manifest_args.add_argument("--output", type=Path, required=True)
    freeze_args = commands.add_parser("freeze")
    freeze_args.add_argument("--config", type=Path, required=True)
    freeze_args.add_argument("--output", type=Path, required=True)
    freeze_args.add_argument("--allow-cloud", action="store_true")
    run_args = commands.add_parser("run")
    run_args.add_argument("--freeze", type=Path, required=True)
    run_args.add_argument("--output", type=Path, required=True)
    run_args.add_argument("--allow-cloud", action="store_true")
    run_args.add_argument("--limit-cases", type=int, help="Checkpoint after N cases; incomplete collections cannot pass")
    blind_args = commands.add_parser("blind")
    blind_args.add_argument("--records", type=Path, required=True)
    blind_args.add_argument("--output", type=Path, required=True)
    score_args = commands.add_parser("score")
    score_args.add_argument("--freeze", type=Path, required=True)
    score_args.add_argument("--records", type=Path, required=True)
    score_args.add_argument("--mapping", type=Path, required=True)
    score_args.add_argument("--sheets", type=Path, required=True)
    score_args.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    corpus = load_json(args.corpus)
    if args.command == "audit":
        cases = validate_corpus(corpus, require_approved=False)
        approvals = approval_summary(corpus)
        print(json.dumps({"cases": len(cases), "languages": len(LANGUAGES),
                          "human_approved": approvals["valid_human_approvals"],
                          **approvals, "release_status": "candidate"}, indent=2))
    elif args.command == "review-manifest":
        validate_corpus(corpus, require_approved=False)
        packet = review_manifest(corpus)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # A review packet may contain decisions entered by its human recipient.
        # Never replace it, including on a repeated invocation of this command.
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(packet, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps({"cases": len(packet["cases"]), "status": packet["status"],
                          "output": str(args.output)}, indent=2))
    elif args.command == "freeze":
        validate_corpus(corpus)  # Fail before touching the network for unreviewed labels.
        api = API(args.url)
        write_json(args.output, freeze(corpus, load_json(args.config), api.request("GET", "/capabilities"), allow_cloud=args.allow_cloud))
    elif args.command == "run":
        validate_corpus(corpus)
        run(corpus, load_json(args.freeze), args.output, API(args.url), allow_cloud=args.allow_cloud, limit_cases=args.limit_cases)
    elif args.command == "blind":
        print(blind_sheets(corpus, load_json(args.records), args.output))
    else:
        observations = load_json(args.records)
        scores = merge_human_scores(observations, load_json(args.mapping), load_json(args.sheets))
        result = score(corpus, load_json(args.freeze), observations, scores)
        write_json(args.output, result)
        print(result["release_status"])


if __name__ == "__main__":
    main()
