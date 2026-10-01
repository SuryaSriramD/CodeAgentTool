"""Fail-closed coverage boundaries, independent of the held-out evaluation corpus.

Scanner evidence is mocked at the adapter boundary. The production validation
code verifies and copies source, without executing, building, or installing it.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from analyzers.base import AnalysisCancelled
from analyzers import semgrep_runner, validation


def _stats(path):
    return {"projects": [{"name": str(path), "file_count": 1,
                          "error_file_count": 0, "untranslated_node_count": 0,
                          "line_count": 2, "error_line_count": 0,
                          "total_node_count": 37, "parsing_rate": 1.0}]}


def _run_semgrep(tmp_path, monkeypatch, mutate=None, parser_error=None):
    source = tmp_path / "main.js"
    source.write_text("function label(value) { return String(value); }\n")
    stats = _stats(source)
    if mutate:
        mutate(stats)
    monkeypatch.setattr(semgrep_runner, "executable", lambda name: "/trusted/" + name)
    monkeypatch.setattr(semgrep_runner, "semgrep_core", lambda: "/trusted/semgrep-core")
    monkeypatch.setattr(semgrep_runner, "tool_version", lambda *args, **kwargs: "1.178.0")

    def run(self, command, workspace, **kwargs):
        if "-parsing_stats" in command:
            if parser_error:
                raise parser_error
            return subprocess.CompletedProcess(command, 0, json.dumps(stats), "")
        return subprocess.CompletedProcess(command, 0, json.dumps({
            "results": [], "errors": [], "paths": {"scanned": [str(source)]}}), "")

    monkeypatch.setattr(semgrep_runner.SemgrepAnalyzer, "_run_command", run)
    return semgrep_runner.SemgrepAnalyzer(profile="security-v2").run_analysis(tmp_path)


def test_complete_native_and_scan_evidence_permits_coverage(tmp_path, monkeypatch):
    report = _run_semgrep(tmp_path, monkeypatch)
    assert report.status == "completed", report.coverage
    assert report.coverage["scanned_paths"] == ["main.js"]


@pytest.mark.parametrize("field", ["error_file_count", "untranslated_node_count"])
def test_actual_parse_or_translation_failure_is_incomplete(tmp_path, monkeypatch, field):
    report = _run_semgrep(tmp_path, monkeypatch,
                          lambda stats: stats["projects"][0].update({field: 1}))
    assert report.status in ("failed", "partial")
    assert report.coverage["files_scanned"] == 0
    assert report.coverage["errors"]
    assert report.coverage["path_outcomes"][0]["status"] == "not_assessed"


def _corrupt_stats(stats, mutation):
    entry = stats["projects"][0]
    if mutation == "omitted-path":
        stats["projects"] = []
    elif mutation == "duplicate-path":
        stats["projects"].append(deepcopy(entry))
    elif mutation == "unknown-path":
        stats["projects"].append(dict(entry, name=str(Path(entry["name"]).with_name("unexpected.js"))))
    elif mutation == "missing-count":
        del entry["error_file_count"]
    elif mutation == "boolean-count":
        entry["file_count"] = True
    elif mutation == "fractional-count":
        entry["file_count"] = 1.0
    elif mutation == "text-count":
        entry["error_file_count"] = "0"
    elif mutation == "negative-count":
        entry["untranslated_node_count"] = -1
    elif mutation == "null-entry":
        stats["projects"] = [None]
    elif mutation == "wrong-container":
        stats["projects"] = {}


@pytest.mark.parametrize("mutation", [
    "omitted-path", "duplicate-path", "unknown-path", "missing-count",
    "boolean-count", "fractional-count", "text-count", "negative-count",
    "null-entry", "wrong-container",
])
def test_unreliable_native_evidence_cannot_claim_complete_coverage(tmp_path, monkeypatch, mutation):
    report = _run_semgrep(tmp_path, monkeypatch, lambda stats: _corrupt_stats(stats, mutation))
    assert report.status in ("failed", "partial"), (mutation, report.coverage)
    assert report.coverage["errors"]


def test_native_parser_timeout_stays_incomplete(tmp_path, monkeypatch):
    report = _run_semgrep(tmp_path, monkeypatch,
                          parser_error=subprocess.TimeoutExpired(["semgrep-core"], 1))
    assert report.status == "failed"
    assert report.coverage["files_scanned"] == 0
    assert report.coverage["errors"]


def test_native_parser_cancellation_propagates(tmp_path, monkeypatch):
    with pytest.raises(AnalysisCancelled):
        _run_semgrep(tmp_path, monkeypatch, parser_error=AnalysisCancelled("Canceled"))


def _proposal_snapshot(tmp_path):
    root = tmp_path / "snapshot"
    source = root / "source"
    source.mkdir(parents=True)
    raw = b"function decode(input) { return eval(input); }\n"
    (source / "app.js").write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    (root / "manifest.json").write_text(json.dumps({"files": {"app.js": digest}}))
    body = {
        "profile": "security-v2", "timeout_sec": 120,
        "edits": [{"file": "app.js", "source_hash": digest,
                   "original": "eval(input)", "replacement": "JSON.parse(input)"}],
        "target_findings": [{"id": "finding-1", "tool": "semgrep",
                             "rule_id": "codeagent.javascript.security.v1", "file": "app.js", "line": 1}],
    }
    return root, body, digest


def _scan_evidence(path):
    original = "eval(input)" in (Path(path) / "app.js").read_text()
    issues = [{"id": "finding-1", "tool": "semgrep", "file": "app.js", "line": 1,
               "rule_id": "codeagent.javascript.security.v1", "message": "Dynamic evaluation"}] if original else []
    return {
        "status": "completed", "files": [{"path": "app.js", "issues": issues}],
        "coverage": [{"tool": "semgrep", "status": "completed", "errors": [],
                      "files_discovered": 1, "files_scanned": 1, "files_skipped": 0,
                      "scanned_paths": ["app.js"],
                      "path_outcomes": [{"path": "app.js", "language": "javascript", "status": "completed"}]}],
        "profile_digests": {"source": "frozen", "dependency": "frozen"},
        "tool_runs": [{"name": "semgrep", "version": "1.178.0", "status": "completed"}],
    }


def _corrupt_coverage(report, mutation):
    coverage = report["coverage"][0]
    if mutation == "omitted-tool":
        report["coverage"] = []
    elif mutation == "duplicate-tool":
        report["coverage"].append(deepcopy(coverage))
    elif mutation == "omitted-path":
        coverage["path_outcomes"] = []
    elif mutation == "duplicate-path":
        coverage["path_outcomes"].append(deepcopy(coverage["path_outcomes"][0]))
    elif mutation == "path-not-assessed":
        coverage["path_outcomes"][0]["status"] = "not_assessed"
    elif mutation == "tool-not-assessed":
        coverage["status"] = "failed"
    elif mutation == "diagnostic-error":
        coverage["errors"] = ["app.js: parser translation is incomplete"]
    elif mutation == "wrong-count":
        coverage["files_scanned"] = 0
    elif mutation == "boolean-count":
        coverage["files_scanned"] = True
    elif mutation == "omitted-scanned-path":
        coverage["scanned_paths"] = []
    elif mutation == "parser-incomplete":
        coverage["path_outcomes"][0]["parser"] = {"status": "incomplete", "errors": []}
    elif mutation == "parser-error":
        coverage["path_outcomes"][0]["parser"] = {"status": "completed", "errors": ["Untranslated syntax"]}
    elif mutation == "parser-malformed":
        coverage["path_outcomes"][0]["parser"] = None
    elif mutation == "unsupported-translation":
        coverage["status"] = "partial"
        coverage["path_outcomes"][0].update(status="not_assessed", parser={
            "status": "incomplete", "untranslated_nodes": 1,
            "errors": ["Unsupported syntax"]})
        coverage["errors"] = ["app.js: unsupported parser translation"]


@pytest.mark.parametrize("parser_evidence", [False, True])
def test_proposal_validation_accepts_complete_evidence_without_changing_snapshot(tmp_path, monkeypatch, parser_evidence):
    root, body, digest = _proposal_snapshot(tmp_path)
    def scan(path, *args, **kwargs):
        report = _scan_evidence(path)
        if parser_evidence:
            report["coverage"][0]["path_outcomes"][0]["parser"] = {
                "status": "completed", "syntax_error_files": 0, "error_lines": 0,
                "untranslated_nodes": 0, "audited_metadata_counts": {}, "errors": []}
        return report
    monkeypatch.setattr(validation, "scan_workspace", scan)
    result = validation.validate_proposal(root, body)
    assert result["status"] == result["syntax"]["status"] == "passed", result
    assert hashlib.sha256((root / "source/app.js").read_bytes()).hexdigest() == digest
    assert result["applied"] is False and result["runtime_tested"] is False


@pytest.mark.parametrize("phase", ["before", "after"])
@pytest.mark.parametrize("mutation", [
    "omitted-tool", "duplicate-tool", "omitted-path", "duplicate-path",
    "path-not-assessed", "tool-not-assessed", "diagnostic-error", "unsupported-translation",
    "wrong-count", "boolean-count", "omitted-scanned-path",
    "parser-incomplete", "parser-error", "parser-malformed",
])
def test_aggregate_completed_cannot_override_incomplete_proposal_evidence(tmp_path, monkeypatch, phase, mutation):
    root, body, _ = _proposal_snapshot(tmp_path)

    def scan(path, *args, **kwargs):
        report = _scan_evidence(path)
        actual_phase = "before" if Path(path) == root / "source" else "after"
        if actual_phase == phase:
            _corrupt_coverage(report, mutation)
        return report

    monkeypatch.setattr(validation, "scan_workspace", scan)
    result = validation.validate_proposal(root, body)
    assert result["status"] == "incomplete", (phase, mutation, result)
    assert result["errors"]
    if phase == "after":
        assert result["syntax"]["status"] != "passed"
    if mutation == "unsupported-translation":
        evidence = result["coverage_" + phase][0]["path_outcomes"][0]["parser"]
        assert evidence["untranslated_nodes"] == 1
        assert evidence["errors"] == ["Unsupported syntax"]


def test_validation_requires_coverage_of_other_relevant_source_files(tmp_path, monkeypatch):
    root, body, _ = _proposal_snapshot(tmp_path)
    source = b"function show(value) { return String(value); }\n"
    (root / "source/caller.js").write_bytes(source)
    manifest = json.loads((root / "manifest.json").read_text())
    manifest["files"]["caller.js"] = hashlib.sha256(source).hexdigest()
    (root / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(validation, "scan_workspace", lambda path, *args, **kwargs: _scan_evidence(path))
    result = validation.validate_proposal(root, body)
    assert result["status"] == "incomplete"
    assert any("caller.js" in error for error in result["errors"])


@pytest.mark.parametrize("changed_path,dependency_changes", [
    ("analyzers/parser_evidence.py", False),
    ("analyzers/validation.py", False),
    ("ingestion/policy.py", True),
    ("ingestion/snapshots.py", True),
    ("analyzers/common.py", True),
])
def test_profile_identity_tracks_coverage_and_ingestion_policy(tmp_path, monkeypatch, changed_path, dependency_changes):
    from analyzers import profiles, depcheck_runner, dotnet_runner
    paths = ["rules/security-v2.yaml", "ingestion/policy.py", "ingestion/snapshots.py",
             "dotnet-analyzer/Program.fs", "dotnet-analyzer/Roslyn/Analyzer.cs"]
    paths += ["analyzers/" + name for name in (
        "semgrep_runner.py", "parser_evidence.py", "bandit_runner.py", "dotnet_runner.py",
        "common.py", "service.py", "validation.py", "depcheck_runner.py")]
    for relative in paths:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("identity fixture: " + relative)
    (tmp_path / "rules/tool-versions.json").write_text(json.dumps({
        "semgrep": "1.178.0", "bandit": "1.9.4", "trivy": "0.74.0", "dotnet_analyzer": "1.1.0"}))
    monkeypatch.setattr(profiles, "ROOT", tmp_path)
    monkeypatch.setattr(profiles, "tool_version", lambda name: "fixed-" + name)
    monkeypatch.setattr(dotnet_runner.DotnetAnalyzer, "version", property(lambda self: "fixed-dotnet"))
    monkeypatch.setattr(depcheck_runner, "database_metadata", lambda: {"updated_at": "frozen", "age_seconds": 1})
    before = profiles.profile_metadata("security-v2")
    (tmp_path / changed_path).write_text("revised identity fixture")
    after = profiles.profile_metadata("security-v2")
    assert after["source"] != before["source"]
    assert (after["dependency"] != before["dependency"]) is dependency_changes
