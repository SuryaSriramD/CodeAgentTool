"""Bandit adapter preserving tool errors and Python parse coverage."""
import json
import time
from pathlib import Path
from .base import BaseAnalyzer, Issue, analyzer_registry, AnalysisCancelled
from .common import inventory, executable, tool_version, result

class BanditAnalyzer(BaseAnalyzer):
    def __init__(self, timeout_sec=300, confidence_level="low", cancel=None):
        super().__init__(timeout_sec, cancel)
        self.confidence_level = confidence_level

    @property
    def name(self): return "bandit"

    @property
    def version(self): return tool_version("bandit")

    def is_applicable(self, workspace_path):
        return bool(inventory(workspace_path, {"python"}))

    def run_analysis(self, workspace_path, **kwargs):
        start = time.monotonic()
        self._command_deadline = start + self.timeout_sec
        files = inventory(workspace_path, {"python"})
        version = tool_version("bandit", runner=self._run_command)
        if not files: return result(self.name, start, files, version=version)
        binary = executable("bandit")
        if not binary:
            return result(self.name, start, files, errors=["Bandit executable is not installed"], version=version)
        try:
            cmd = [binary, "--format", "json", "--ignore-nosec", "--quiet"]
            # An explicit target list prevents .bandit configuration auto-discovery.
            cmd.extend(str(Path(workspace_path, path).resolve()) for path, _ in files)
            proc = self._run_command(cmd, workspace_path)
            data = json.loads(proc.stdout)
            if not isinstance(data, dict) or "results" not in data or "metrics" not in data:
                raise ValueError("Bandit returned an invalid report")
            errors = [f"{e.get('filename','')}: {e.get('reason', e)}" for e in data.get("errors", [])]
            scanned = {self._normalize_file_path(p, workspace_path) for p in data["metrics"] if p != "_totals"}
            bad = {self._normalize_file_path(e["filename"], workspace_path) for e in data.get("errors", []) if e.get("filename")}
            scanned -= bad
            if proc.returncode not in (0, 1):
                errors.append(f"Bandit exited {proc.returncode}: {proc.stderr[-1000:]}")
            missing = {p for p, _ in files} - scanned
            if missing: errors.append(f"{len(missing)} Python files were not scanned")
            issues = [self._convert_bandit_finding(f, workspace_path) for f in data["results"]]
            return result(self.name, start, files, scanned, issues, errors, version)
        except AnalysisCancelled:
            raise
        except Exception as exc:
            return result(self.name, start, files, errors=[str(exc)], version=version)

    def _convert_bandit_finding(self, finding, workspace_path):
        return Issue(self.name, finding.get("test_id", "unknown"), finding.get("issue_text", ""),
                     self._parse_severity(finding.get("issue_severity", "medium")),
                     self._normalize_file_path(finding["filename"], workspace_path),
                     int(finding.get("line_number", 1)), finding.get("test_id", "unknown"),
                     f"See: {finding['more_info']}" if finding.get("more_info") else None,
                     family=finding.get("test_name"),cwe=f"CWE-{finding['issue_cwe']['id']}" if finding.get('issue_cwe',{}).get('id') else None,
                     analysis_kind='structural',end_line=max(finding.get('line_range') or [finding.get('line_number',1)]),
                     evidence=[{'kind':'source_span','file':self._normalize_file_path(finding['filename'],workspace_path),
                                'line':finding.get('line_number',1),'text':finding.get('code','')}])

analyzer_registry.register(BanditAnalyzer)
