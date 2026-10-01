"""Record candidate parser/scanner evidence through the existing API/worker.

This is authoring validation, not a quality benchmark. It never requests AI
review, approves labels, changes rules, or executes submitted source.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fnmatch
import hashlib
import json
import time
import uuid
from collections import Counter
from pathlib import Path

import httpx

from analyzers.common import DOTNET_LANGUAGES, language_for
from analyzers.depcheck_runner import LOCKS, MANIFESTS
from evaluation.benchmark import API, make_zip, matches_expected, now, write_json
from evaluation.candidate_corpus import ROOT, canonical_digest, validate_candidate
from evaluation.corpus_review import case_review_digest

VERSION = "candidate-static-validation/1"
TERMINAL = {"completed", "partial", "failed", "canceled", "interrupted"}
TOOLS = {"semgrep", "bandit", "dotnet", "depcheck"}


def implementation_digest():
    root = Path(__file__).resolve().parent.parent
    paths = ("evaluation/static_validation.py", "evaluation/candidate_corpus.py",
             "evaluation/corpus_review.py", "evaluation/benchmark.py", "analyzers/common.py",
             "analyzers/depcheck_runner.py")
    return canonical_digest({path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths})


def environment(capabilities, profile):
    profiles = capabilities.get("profile_digests") or {}
    selected = profiles.get(profile) or {}
    if not selected.get("source"):
        raise ValueError("The server must expose the selected source/rule profile digest")
    tools = [{k: tool.get(k) for k in ("id", "version", "expected_version", "available")}
             for tool in capabilities.get("analyzers", []) if tool.get("id") in TOOLS]
    if {tool["id"] for tool in tools} != TOOLS:
        raise ValueError("The server must expose all four configured scanners")
    return {"profile": profile, "profile_digests": {k: selected.get(k) for k in ("source", "dependency")},
            "tools": sorted(tools, key=lambda tool: tool["id"])}


def assess(case, report, job, pinned):
    """Separate operational/parser evidence from unapproved label agreement."""
    errors = []
    expected_files = {name: hashlib.sha256(text.encode("utf-8")).hexdigest()
                      for name, text in case["files"].items()}
    snapshot = (report.get("meta") or {}).get("snapshot") or {}
    if snapshot.get("files") != expected_files:
        errors.append("Scanned snapshot inventory/hashes differ from the authored source")
    if report.get("job_id") != job.get("job_id"):
        errors.append("Report identity differs from the submitted job")
    if report.get("ai_analysis"):
        errors.append("Static validation unexpectedly contains AI analysis")
    if {key: (report.get("profile_digests") or {}).get(key) for key in ("source", "dependency")} != pinned["profile_digests"]:
        errors.append("Effective rule/tool/database profile differs from the pinned validation profile")
    if job.get("config", {}).get("mode") != "static":
        errors.append("Job is not a static scan")
    coverage = report.get("coverage") or []
    if len(coverage) != len(TOOLS) or {entry.get("tool") for entry in coverage} != TOOLS:
        errors.append("A configured scanner did not return coverage evidence")
    languages = {language_for(Path(path)) for path in case["files"]} - {None}
    dependency_patterns = [pattern for registry in (LOCKS, MANIFESTS)
                           for patterns in registry.values() for pattern in patterns]
    applicable = {"semgrep": bool(languages - DOTNET_LANGUAGES),
                  "dotnet": bool(languages & DOTNET_LANGUAGES), "bandit": "python" in languages,
                  "depcheck": any(fnmatch.fnmatchcase(Path(path).name, pattern)
                                  for path in case["files"] for pattern in dependency_patterns)}
    for entry in coverage:
        if entry.get("status") not in {"completed", "skipped"} or entry.get("errors"):
            errors.append(f"{entry.get('tool')}: incomplete scanner coverage")
        if applicable.get(entry.get("tool")) and entry.get("status") != "completed":
            errors.append(f"{entry.get('tool')}: applicable scanner did not complete")
        tool = entry.get("tool")
        additional_paths = [path for path in case["files"] if
                            (tool == "bandit" and language_for(Path(path)) == "python") or
                            (tool == "depcheck" and any(fnmatch.fnmatchcase(Path(path).name, pattern)
                                                       for pattern in dependency_patterns))]
        for path in additional_paths:
            outcomes = [item for item in entry.get("path_outcomes", []) if item.get("path") == path]
            if len(outcomes) != 1 or outcomes[0].get("status") != "completed":
                errors.append(f"{tool}: {path} has no complete per-file check outcome")
    parsing = []
    for path in case["files"]:
        language = language_for(Path(path))
        if language is None:
            continue  # Contracts and documentation remain context, not parsed code.
        tool = "dotnet" if language in DOTNET_LANGUAGES else "semgrep"
        matching = [item for entry in coverage if entry.get("tool") == tool
                    for item in entry.get("path_outcomes", []) if item.get("path") == path]
        complete = len(matching) == 1 and matching[0].get("status") == "completed"
        parsing.append({"path": path, "language": language, "tool": tool,
                        "status": "completed" if complete else "incomplete"})
        if not complete:
            errors.append(f"{path}: no complete trusted-parser/check outcome")
    if not parsing:
        errors.append("No source file received a trusted-parser outcome")
    if job.get("status") != "completed" or report.get("status") != "completed":
        errors.append("Scan did not complete successfully")
    findings = [dict(issue, file=file["path"]) for file in report.get("files", [])
                for issue in file.get("issues", [])]
    for finding in findings:
        if (finding.get("file") not in expected_files
                or finding.get("source_hash") != expected_files.get(finding.get("file"))):
            errors.append("Finding evidence has an incompatible source hash")
    observations = []
    matched_ids = set()
    for expected in case["expected_findings"]:
        matched = [item["id"] for item in findings if matches_expected(item, [expected])
                   and (not expected.get("line_start") or
                        max(item.get("line", 1), expected["line_start"]) <=
                        min(item.get("end_line") or item.get("line", 1),
                            expected.get("line_end") or expected["line_start"]))]
        matched_ids.update(matched)
        observations.append({"expected": expected, "observed_finding_ids": matched})
    unexpected = [item["id"] for item in findings if item["id"] not in matched_ids]
    missing = [item["expected"] for item in observations if not item["observed_finding_ids"]]
    agreement = ("missing_and_unexpected" if missing and unexpected else "expected_not_observed" if missing
                 else "unexpected_findings" if unexpected else "matches_proposed_labels")
    return {"operational_status": "incomplete" if errors else "completed",
            "parser_status": "completed" if parsing and all(p["status"] == "completed" for p in parsing) else "incomplete",
            "parser_outcomes": parsing, "label_observation": agreement,
            "expected_observations": observations, "missing_expected_findings": missing,
            "unexpected_finding_ids": unexpected, "findings": findings,
            "coverage": coverage, "tool_runs": report.get("meta", {}).get("tool_runs", []),
            "snapshot_id": snapshot.get("id"), "snapshot_digest": snapshot.get("digest"),
            "report_version": report.get("report_hash"), "errors": sorted(set(errors)),
            "human_review_required": True, "runtime_tested": False, "source_applied": False}


def summary(state):
    results = [record["result"] for record in state["records"].values() if record.get("result")]
    return {"validation_version": VERSION, "corpus_version": state["corpus_version"],
            "expected_cases": len(state["case_identities"]), "recorded_cases": len(results),
            "operational_statuses": dict(Counter(row["operational_status"] for row in results)),
            "parser_statuses": dict(Counter(row["parser_status"] for row in results)),
            "proposed_label_observations": dict(Counter(row["label_observation"] for row in results)),
            "collection_complete": len(results) == len(state["case_identities"]),
            "human_approvals_created": 0, "model_calls": 0, "runtime_tested": False,
            "release_status": "candidate",
            "limitation": "Unapproved authored labels; these observations are not accuracy estimates or proof of security/independence."}


@contextmanager
def evidence_lock(output):
    """Do not let concurrent collectors overwrite checkpoints or double-submit."""
    import fcntl
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".collector.lock").open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("Another static-evidence collector is using this output directory") from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def evidence_markdown(state):
    totals = summary(state)
    lines = ["# Candidate static-validation evidence", "",
             "These are trusted scanner observations against AI-authored, unapproved labels. "
             "They are not a quality benchmark, human approval, or runtime test.", "",
             f"Recorded cases: **{totals['recorded_cases']}/{totals['expected_cases']}**. "
             "Model calls: **0**. Human approvals created: **0**.", "",
             "## Frozen environment", "", "```json", json.dumps(state["environment"], indent=2), "```", "",
             "## Case observations", "",
             "| Case | Execution | Parser/check coverage | Proposed-label agreement | Evidence |",
             "| --- | --- | --- | --- | --- |"]
    for identity in state["case_identities"]:
        record = state["records"].get(identity, {})
        result = record.get("result")
        if not result:
            lines.append(f"| {identity} | {record.get('status', 'pending')} | — | — | — |")
            continue
        lines.append(f"| {identity} | {result['operational_status']} | {result['parser_status']} | "
                     f"{result['label_observation']} | [Report]({record['report_artifact']}) |")
    lines += ["", "## Incomplete checks", ""]
    incomplete = False
    for identity, record in state["records"].items():
        errors = record.get("result", {}).get("errors", [])
        if errors:
            incomplete = True
            lines.append(f"- **{identity}**: " + "; ".join(errors).replace("\n", " "))
    if not incomplete:
        lines.append("No incomplete results among collected cases. Pending cases have not been assessed.")
    lines += ["", "A missed expected finding is a detection observation, not permission to relabel or tune a held-out case. "
              "Unexpected findings require independent semantic review. Parse/check failures stay incomplete; "
              "they must not count as safe results. The full journal retains source/specification hashes, "
              "exact reports, tool coverage and prior attempts.", ""]
    return "\n".join(lines)


def _safe_error(exc):
    # Do not persist request objects, URLs with credentials, response bodies,
    # authorization headers, or process environment in the evidence journal.
    if isinstance(exc, httpx.HTTPStatusError):
        return f"API returned HTTP {exc.response.status_code}"
    return f"{type(exc).__name__}: validation interrupted; inspect server job status before retrying"


def run_validation(corpus, output, api, **options):
    validate_candidate(corpus)
    with evidence_lock(output):
        return _run_validation(corpus, output, api, **options)


def _run_validation(corpus, output, api, *, profile="security-v2", timeout_sec=120,
                   limit_cases=None, concurrency=2, poll_seconds=1, retry_cases=(), progress=print):
    validate_candidate(corpus)
    if profile != "security-v2" or not 1 <= timeout_sec <= 120 or not 1 <= concurrency <= 2:
        raise ValueError("Use security-v2, a 1–120 second scan budget and one or two concurrent jobs")
    if limit_cases is not None and not 1 <= limit_cases <= len(corpus["cases"]):
        raise ValueError("limit_cases must select at least one case and at most the whole corpus")
    output = Path(output); state_path = output / "state.json"
    identities = {case["id"]: case_review_digest(corpus, case) for case in corpus["cases"]}
    pinned = environment(api.request("GET", "/capabilities"), profile)
    implementation = implementation_digest()
    state = json.loads(state_path.read_text()) if state_path.exists() else {
        "validation_version": VERSION, "corpus_version": corpus["version"], "case_identities": identities,
        "implementation_sha256": implementation, "environment": pinned,
        "timeout_sec": timeout_sec, "records": {}, "created_at": now()}
    if any((state.get("validation_version") != VERSION, state.get("case_identities") != identities,
            state.get("implementation_sha256") != implementation, state.get("environment") != pinned,
            state.get("timeout_sec") != timeout_sec)):
        raise ValueError("Source/specification, validation implementation or scanner profile changed; use a new evidence directory")
    selected = corpus["cases"][:limit_cases] if limit_cases else corpus["cases"]
    retries = set(retry_cases)
    if retries - {case["id"] for case in selected}:
        raise ValueError("Explicit retry case is outside the selected candidate set")
    active = {}

    def save():
        write_json(state_path, state)
        write_json(output / "summary.json", summary(state))
        (output / "README.md").write_text(evidence_markdown(state), encoding="utf-8")

    if "project_id" not in state:
        project = api.request("POST", "/projects", json={"name": "Corpus-v2 static authoring validation"})
        state["project_id"] = project["id"]
        save()
    pending = []
    for case in selected:
        record = state["records"].get(case["id"])
        if case["id"] in retries and record:
            if record.get("job_id"):
                current = api.request("GET", f"/jobs/{record['job_id']}")
                if current.get("status") not in TERMINAL:
                    raise ValueError("A prior attempt is still active; resume or cancel it before explicit retry")
            history = [*record.get("previous_attempts", []), {k:v for k,v in record.items() if k != "previous_attempts"}]
            state["records"][case["id"]] = {"previous_attempts": history}
            record = state["records"][case["id"]]
        if record and record.get("result"):
            artifact = output / record["report_artifact"]
            if not artifact.is_file() or canonical_digest(json.loads(artifact.read_text())) != record["report_sha256"]:
                raise ValueError("Saved report evidence is missing or changed; do not silently reuse it")
            continue
        if record and record.get("status") == "submitting" and not record.get("job_id"):
            raise ValueError(f"{case['id']}: submission outcome uncertain; reconcile server jobs, then use --retry-case only if needed")
        pending.append(case)
    save()
    try:
        while pending or active:
            while pending and len(active) < concurrency:
                case = pending.pop(0)
                record = state["records"].setdefault(case["id"], {})
                if not record.get("job_id"):
                    record.update(status="submitting", submitted_at=now())
                    save()  # An interrupted HTTP call is never silently resubmitted.
                    try:
                        submitted = api.request("POST", "/analyze", data={
                            "mode": "static", "profile": profile, "timeout_sec": str(timeout_sec),
                            "project_id": state["project_id"], "stream": case["id"],
                            "labels": "corpus-v2,authoring-validation,unapproved"},
                            files={"file": (case["id"] + ".zip", make_zip(case), "application/zip")})
                        record.update(job_id=str(uuid.UUID(submitted["job_id"])), status=submitted["status"])
                    except Exception as exc:
                        record["error"] = _safe_error(exc); save(); raise
                    save()
                active[case["id"]] = (case, time.monotonic() + timeout_sec + 120)
            for case_id, (case, deadline) in list(active.items()):
                record = state["records"][case_id]
                job = api.request("GET", f"/jobs/{record['job_id']}")
                if job.get("status") not in TERMINAL:
                    if time.monotonic() >= deadline:
                        api.request("DELETE", f"/jobs/{record['job_id']}")
                        record.update(status="cancel_requested", error="Client wait deadline elapsed; server cancellation requested")
                        save(); raise TimeoutError("Static scan wait deadline elapsed")
                    continue
                try:
                    report = api.request("GET", f"/reports/{record['job_id']}",
                                         params={"report_hash": job.get("source", {}).get("report_hash")} if job.get("source", {}).get("report_hash") else {})
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code != 404:
                        raise
                    report = {"job_id": record["job_id"], "status": job["status"],
                              "errors": ["No saved report was produced; operational result is incomplete"]}
                result = assess(case, report, job, pinned)
                name = f"reports/{case_id}-{record['job_id']}.json"
                write_json(output / name, report)
                record.update(status=job["status"], finished_at=now(), result=result,
                              report_artifact=name, report_sha256=canonical_digest(report))
                save(); del active[case_id]
                progress(f"{len([r for r in state['records'].values() if r.get('result')])}/{len(identities)} "
                         f"{case_id}: {result['operational_status']}; {result['label_observation']}")
            if active:
                time.sleep(poll_seconds)
    except KeyboardInterrupt:
        for case_id in active:
            record = state["records"][case_id]
            try:
                api.request("DELETE", f"/jobs/{record['job_id']}")
                record["status"] = "cancel_requested"
            except Exception as exc:
                record["error"] = _safe_error(exc)
        save(); raise
    state["updated_at"] = now(); save()
    return state


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=ROOT / "corpus.json")
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit-cases", type=int)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--timeout-sec", type=int, default=120)
    parser.add_argument("--retry-case", action="append", default=[])
    args = parser.parse_args(argv)
    corpus = json.loads(args.corpus.read_text())
    validate_candidate(corpus)  # Reject invalid input before an API client exists.
    try:
        state = run_validation(corpus, args.output, API(args.url), limit_cases=args.limit_cases,
                               concurrency=args.concurrency, timeout_sec=args.timeout_sec,
                               retry_cases=args.retry_case)
    except KeyboardInterrupt:
        return 130
    result = summary(state)
    print(json.dumps(result, indent=2))
    return 0 if result["collection_complete"] and not result["operational_statuses"].get("incomplete") else 2


if __name__ == "__main__":
    raise SystemExit(main())
