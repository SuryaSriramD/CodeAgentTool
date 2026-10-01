"""Local .NET parser/rulepack adapter. Never builds the uploaded project."""
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from .base import BaseAnalyzer, Issue, analyzer_registry, AnalysisCancelled
from .common import ROOT, DOTNET_LANGUAGES, inventory, executable, result, command_version

def dotnet_command():
    dll = Path(os.getenv("CODEAGENT_DOTNET_ANALYZER", str(ROOT / "dotnet-analyzer" / "publish" / "CodeAgent.DotNet.dll")))
    runtime = executable("dotnet")
    return [runtime, str(dll)] if runtime and dll.is_file() else None

class DotnetAnalyzer(BaseAnalyzer):
    def __init__(self, timeout_sec=300, cancel=None, profile="security-v1"):
        super().__init__(timeout_sec,cancel)
        from .profiles import validate_profile
        self.profile=validate_profile(profile)

    @property
    def name(self): return "dotnet"

    @property
    def version(self): return self._version()

    def _version(self, runner=None):
        cmd = dotnet_command()
        if not cmd: return "unavailable"
        return command_version('codeagent-dotnet',cmd[0],cmd+['--version'],runner)

    def is_applicable(self, workspace_path):
        return bool(inventory(workspace_path, DOTNET_LANGUAGES))

    def run_analysis(self, workspace_path, **kwargs):
        start = time.monotonic()
        self._command_deadline = start + self.timeout_sec
        files = inventory(workspace_path, DOTNET_LANGUAGES)
        version = self._version(self._run_command)
        if not files: return result(self.name, start, files, version=version)
        cmd = dotnet_command()
        expected='codeagent-dotnet '+json.loads((ROOT/'rules/tool-versions.json').read_text()).get('dotnet_analyzer','1.0.0')
        if cmd and version!='unavailable' and version!=expected:
            return result(self.name,start,files,errors=[f'The .NET analyzer version must be {expected}; found {version}'],version=version)
        if not cmd or version == "unavailable":
            return result(self.name, start, files, errors=["The compiled .NET security rulepack or runtime is unavailable"], version=version)
        try:
            with tempfile.TemporaryDirectory(prefix="codeagent-dotnet-") as tmp:
                manifest = Path(tmp, "manifest.json")
                manifest.write_text(json.dumps({"workspace": str(Path(workspace_path).resolve()),
                                               "profile":self.profile, "files": [{"path": p, "language": lang} for p, lang in files]}))
                proc = self._run_command(cmd + [str(manifest)], workspace_path)
            if proc.returncode != 0:
                raise RuntimeError(f".NET analyzer exited {proc.returncode}: {proc.stderr[-2000:]}")
            data = json.loads(proc.stdout)
            if not isinstance(data, list): raise ValueError("Invalid .NET analyzer report")
            scanned, issues, errors = [], [], []
            for file in data:
                path = self._normalize_file_path(file["path"], workspace_path)
                diagnostics = file.get("errors", [])
                errors.extend(f"{path}: {e}" for e in diagnostics)
                if not diagnostics: scanned.append(path)
                for finding in file["issues"]:
                    issues.append(Issue(self.name, finding["rule_id"], finding["message"],
                                        self._parse_severity(finding["severity"]), path,
                                        int(finding["line"]), finding["rule_id"],
                                        family=finding.get("family"), cwe=finding.get("cwe"),
                                        analysis_kind="semantic-api" if file.get("language") != "fsharp" else "structural",
                                        end_line=finding.get("end_line",finding["line"]),
                                        rule_revision="2" if finding["rule_id"].endswith(".v2") else "1",
                                        evidence=[{"kind":"source_span","file":path,"line":finding["line"],"text":finding.get("evidence","")}]))
            if len(scanned) < len(files) and not errors:
                errors.append("The .NET analyzer did not report every source file")
            return result(self.name, start, files, scanned, issues, errors, version)
        except AnalysisCancelled: raise
        except Exception as exc:
            return result(self.name, start, files, errors=[str(exc)], version=version)

analyzer_registry.register(DotnetAnalyzer)
