"""Actual-engine parser controls authored independently of evaluation cases.

These source strings are data for the pinned scanner. They are never compiled,
installed, imported, or executed. The rules remain the repository rule profile.
"""
import hashlib
import json
import zipfile

import pytest

from analyzers.common import ROOT, executable
from analyzers.service import scan_workspace
from ingestion.snapshots import build_snapshot, verify_snapshot
from settings import Settings


pytestmark = pytest.mark.skipif(not executable("semgrep"), reason="Trusted pinned Semgrep engine is required")

METADATA_CONTROLS = {
    "exported.js": ("OtherDirective:Export", """export function inspect(value) {
  return eval(value);
}
"""),
    "exported.ts": ("OtherDirective:Export", """export function describe(value: string): string {
  return String(value);
}
"""),
    "sized.c": ("OtherType:TSized", """unsigned int byte_count(unsigned char value) {
  return value;
}
"""),
    "Resource.java": ("OtherAttribute:Throw", """class Resource {
  static void close() throws java.io.IOException {
    throw new java.io.IOException("closed");
  }
}
"""),
    "message.go": ("OtherAttribute:GoTag", """package message
type Message struct {
    Value string `json:"value"`
}
func valueOf(message Message) string { return message.Value }
"""),
}


def snapshot_scan(tmp_path, files):
    settings = Settings(storage=tmp_path / "storage", team_mode=False)
    settings.prepare()
    archive = tmp_path / "input.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        for name, source in files.items():
            stream.writestr(name, source)
    manifest = build_snapshot(archive, "parser-controls", settings, {"source": "zip"}, {})
    root = settings.storage / "snapshots/parser-controls/source"
    original_hashes = {name: hashlib.sha256(source.encode()).hexdigest() for name, source in files.items()}
    assert manifest["files"] == original_hashes
    report = scan_workspace(root, ["semgrep"], timeout_sec=60, profile="security-v2")
    verify_snapshot(root, manifest)
    assert {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files} == original_hashes
    return report


@pytest.fixture(scope="module")
def metadata_report(tmp_path_factory):
    return snapshot_scan(tmp_path_factory.mktemp("native-metadata"),
                         {name: source for name, (_, source) in METADATA_CONTROLS.items()})


@pytest.mark.parametrize("path,metadata_kind", [(name, kind) for name, (kind, _) in METADATA_CONTROLS.items()])
def test_only_audited_metadata_can_complete_parser_coverage(metadata_report, path, metadata_kind):
    assert metadata_report["status"] == "completed", metadata_report["coverage"]
    coverage = metadata_report["coverage"][0]
    outcome = next(item for item in coverage["path_outcomes"] if item["path"] == path)
    assert outcome["status"] == "completed"
    assert outcome["rule_ids"]
    parser = outcome["parser"]
    assert parser["status"] == "completed"
    assert parser["policy"] == "native-parser-evidence/2"
    assert parser["syntax_error_files"] == 0
    assert parser["untranslated_node_count"] > 0
    assert parser["audited_metadata_counts"][metadata_kind] > 0
    assert sum(parser["audited_metadata_counts"].values()) == parser["untranslated_node_count"]
    assert parser["errors"] == []


def test_scan_report_preserves_parser_audit_and_source_profile(metadata_report, tmp_path):
    report_file = tmp_path / "saved-report.json"
    report_file.write_text(json.dumps(metadata_report))
    saved = json.loads(report_file.read_text())
    assert saved["coverage"] == metadata_report["coverage"]
    source = saved["profile_digests"]["source_details"]
    assert source["coverage_contract"] == "native-parser-evidence/2"
    for adapter in ("semgrep_runner.py", "parser_evidence.py"):
        assert source["adapters"][adapter] == hashlib.sha256((ROOT / "analyzers" / adapter).read_bytes()).hexdigest()
    assert source["ingestion"]["policy.py"] == hashlib.sha256((ROOT / "ingestion/policy.py").read_bytes()).hexdigest()
    findings = [issue for entry in saved["files"] for issue in entry["issues"]]
    assert any(issue["rule_id"] == "codeagent.javascript.security.v1" and issue["file"] == "exported.js" for issue in findings)


@pytest.mark.parametrize("untrusted", [False, True], ids=["fixed-path", "request-path"])
def test_export_metadata_preserves_actual_taint_analysis(tmp_path, untrusted):
    argument = "req.query.asset" if untrusted else "'/srv/static/catalog.json'"
    source = "import fs from 'node:fs';\nexport function readAsset(req) {\n"
    source += f"  const location = {argument};\n  return fs.readFileSync(location, 'utf8');\n}}\n"
    report = snapshot_scan(tmp_path, {"assets.js": source})
    assert report["status"] == "completed", report["coverage"]
    findings = [issue for entry in report["files"] for issue in entry["issues"]]
    assert any(issue["rule_id"] == "codeagent.javascript.path-traversal.v2" for issue in findings) is untrusted
    assert report["coverage"][0]["path_outcomes"][0]["parser"]["audited_metadata_counts"]["OtherDirective:Export"] > 0


@pytest.mark.parametrize("path,source", [
    ("broken.js", "export function broken( {\n"),
    ("broken.ts", "export function broken(value: {\n"),
    ("broken.c", "unsigned int byte_count( {\n"),
    ("Broken.java", "class Broken { static void run( }\n"),
    ("broken.go", "package broken\nfunc run( {\n"),
])
def test_real_syntax_errors_remain_incomplete(tmp_path, path, source):
    report = snapshot_scan(tmp_path, {path: source})
    assert report["status"] in {"partial", "failed"}, report["coverage"]
    coverage = report["coverage"][0]
    assert coverage["files_scanned"] == 0
    assert coverage["errors"]
    outcome = coverage["path_outcomes"][0]
    assert outcome["status"] == "not_assessed"
    assert outcome["parser"]["status"] == "incomplete"
    assert outcome["parser"]["errors"]


@pytest.mark.parametrize("path,source", [
    ("send.go", "package channel\nfunc send(c chan string, value string) { c <- value }\n"),
    ("Outcome.swift", "func answer() -> Result<Int, Error> { return .success(1) }\n"),
    ("TypeName.java", "class TypeName { Class<?> type() { return String.class; } }\n"),
])
def test_unsupported_executable_nodes_are_not_treated_as_metadata(tmp_path, path, source):
    report = snapshot_scan(tmp_path, {path: source})
    assert report["status"] in {"partial", "failed"}, report["coverage"]
    coverage = report["coverage"][0]
    assert coverage["files_scanned"] == 0
    assert coverage["errors"]
    outcome = coverage["path_outcomes"][0]
    assert outcome["status"] == "not_assessed"
    parser = outcome["parser"]
    assert parser["status"] == "incomplete"
    assert parser["syntax_error_files"] == 0
    assert parser["untranslated_node_count"] > 0
    assert parser["errors"]
