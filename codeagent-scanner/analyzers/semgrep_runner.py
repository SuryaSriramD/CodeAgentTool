"""Semgrep with our versioned local rules: no registry, account or metrics."""
import json
import os
import time
from pathlib import Path
from .base import BaseAnalyzer, Issue, analyzer_registry, AnalysisCancelled
from .common import ROOT, LANGUAGE_EXTENSIONS, DOTNET_LANGUAGES, inventory, executable, tool_version, result
from .parser_evidence import evidence, parse_statistics, from_statistics, audit_ast

SEMGREP_LANGUAGES = set(LANGUAGE_EXTENSIONS) - DOTNET_LANGUAGES

def semgrep_core():
    configured = executable('semgrep-core')
    if configured: return configured
    wrapper = executable('semgrep')
    if not wrapper: return None
    root = Path(wrapper).resolve().parent.parent
    candidates = list(root.glob('lib/python*/site-packages/semgrep/bin/semgrep-core'))
    candidates += [root / 'Lib/site-packages/semgrep/bin/semgrep-core.exe']
    return next((str(p) for p in candidates if p.is_file() and os.access(p, os.X_OK)), None)

class SemgrepAnalyzer(BaseAnalyzer):
    def __init__(self, timeout_sec=300, rulesets=None, cancel=None, profile="security-v1"):
        super().__init__(timeout_sec, cancel)
        # Remote / repository-provided rule configs are intentionally not accepted.
        from .profiles import validate_profile
        self.profile = validate_profile(profile)
        self.rules = ROOT / "rules" / f"{self.profile}.yaml"

    @property
    def name(self): return "semgrep"

    @property
    def version(self): return tool_version("semgrep")

    def is_applicable(self, workspace_path):
        return bool(inventory(workspace_path, SEMGREP_LANGUAGES))

    def run_analysis(self, workspace_path, **kwargs):
        start = time.monotonic()
        self._command_deadline = start + self.timeout_sec
        files = inventory(workspace_path, SEMGREP_LANGUAGES)
        version = tool_version("semgrep", runner=self._run_command)
        parser_evidence = {path: evidence("Native parser was not run") for path, _ in files}

        def finish(scanned=(), issues=(), errors=()):
            output = result(self.name, start, files, scanned, issues, errors, version)
            for outcome in output.coverage['path_outcomes']:
                outcome['parser'] = parser_evidence[outcome['path']]
            return output

        if not files: return result(self.name, start, files, version=version)
        binary = executable("semgrep")
        if not binary or not semgrep_core():
            return finish(errors=["Semgrep wrapper or bundled parser executable is not installed"])
        try:
            cmd = [binary, "scan", "--config", str(self.rules), "--json", "--metrics=off",
                   "--disable-version-check", "--no-git-ignore", "--no-rewrite-rule-ids",
                   "--disable-nosem", "--jobs", "2", "--quiet", "--exclude", "._*",
                   "--max-target-bytes", "0", "--optimizations", "none", "--oss-only"]
            # Explicit files avoid scanning dependencies, symlinks, generated output or
            # repository rules. Tool-level skips are still reported as coverage gaps.
            cmd.extend(str(Path(workspace_path, path).resolve()) for path, _ in files)
            env = {k:v for k,v in os.environ.items() if not k.startswith("SEMGREP_")}
            env.update({"SEMGREP_SEND_METRICS": "off", "SEMGREP_ENABLE_VERSION_CHECK": "0"})
            # The CLI counts prefiltered files as scanned even when it never parses
            # them. Independently force the pinned native parser across every target.
            parse_errors, parsed_paths = [], set()
            language_aliases = {'javascript':'js','typescript':'ts','kotlin':'kt'}
            for language in sorted({lang for _,lang in files}):
                targets = [p for p,lang in files if lang == language]
                parser_cmd = [semgrep_core(), '-json', '-lang', language_aliases.get(language,language), '-parsing_stats']
                parser_cmd.extend(str(Path(workspace_path,path).resolve()) for path in targets)
                try:
                    parsed = self._run_command(parser_cmd, workspace_path, env=env)
                    if parsed.returncode != 0:
                        raise ValueError(f'Native parser exited {parsed.returncode}')
                    stats = parse_statistics(json.loads(parsed.stdout), targets,
                        lambda path: self._normalize_file_path(path, workspace_path))
                except AnalysisCancelled:
                    raise
                except Exception as exc:
                    message = str(exc) if isinstance(exc, ValueError) and not isinstance(exc, json.JSONDecodeError) else type(exc).__name__
                    for path in targets:
                        parser_evidence[path] = evidence(message)
                        parse_errors.append(f'{path}: {message}')
                    continue
                for path, entry in stats.items():
                    item = parser_evidence[path] = from_statistics(entry)
                    if not item['errors'] and entry['untranslated_node_count']:
                        try:
                            ast_cmd = [semgrep_core(), '-json', '-lang', language_aliases.get(language,language),
                                       '-dump_ast', str(Path(workspace_path,path).resolve())]
                            dumped = self._run_command(ast_cmd, workspace_path, env=env)
                            if dumped.returncode != 0:
                                raise ValueError(f'Generic AST parser exited {dumped.returncode}')
                            audited, unsupported, errors = audit_ast(json.loads(dumped.stdout), language,
                                entry['untranslated_node_count'], version)
                            item.update(audited_metadata_counts=audited, unsupported_node_counts=unsupported)
                            item['errors'].extend(errors)
                            if not errors:
                                item['status'] = 'completed'
                        except AnalysisCancelled:
                            raise
                        except Exception as exc:
                            item['errors'].append('Generic AST audit failed: ' + type(exc).__name__)
                    if item['status'] == 'completed':
                        parsed_paths.add(path)
                    else:
                        parse_errors.extend(f'{path}: {error}' for error in item['errors'])
            proc = self._run_command(cmd, workspace_path, env=env)
            data = json.loads(proc.stdout)
            if not isinstance(data, dict) or "results" not in data:
                raise ValueError("Semgrep returned an invalid report")
            errors = parse_errors + [str(e.get("message", e)) for e in data.get("errors", [])]
            bad_paths = {self._normalize_file_path(e["path"], workspace_path) for e in data.get("errors", []) if e.get("path")}
            scanned = {self._normalize_file_path(p, workspace_path) for p in data.get("paths", {}).get("scanned", [])} - bad_paths
            scanned &= parsed_paths
            issues = [self._convert_semgrep_finding(f, workspace_path) for f in data["results"]]
            if proc.returncode not in (0, 1):
                errors.append(f"Semgrep exited {proc.returncode}: {proc.stderr[-1000:]}")
            missing = {p for p, _ in files} - scanned
            if missing: errors.append(f"{len(missing)} source files were skipped or did not parse: " + ", ".join(sorted(missing)[:10]))
            return finish(scanned, issues, errors)
        except AnalysisCancelled:
            raise
        except Exception as exc:
            return finish(errors=[str(exc)])

    def _convert_semgrep_finding(self, finding, workspace_path):
        extra = finding.get("extra", {})
        legacy={"python":("shell-injection","CWE-78"),"javascript":("dynamic-evaluation","CWE-95"),
                "typescript":("dynamic-evaluation","CWE-95"),"java":("weak-crypto","CWE-327"),
                "go":("shell-injection","CWE-78"),"c":("buffer-overflow","CWE-120"),"cpp":("buffer-overflow","CWE-120"),
                "ruby":("dynamic-evaluation","CWE-95"),"php":("dynamic-evaluation","CWE-95"),
                "scala":("weak-crypto","CWE-327"),"kotlin":("weak-crypto","CWE-327"),"swift":("weak-crypto","CWE-327"),
                "rust":("shell-injection","CWE-78"),"bash":("unverified-code-execution","CWE-494"),
                "yaml":("excessive-privilege","CWE-250"),"json":("tls-validation","CWE-295"),
                "xml":("insecure-cookie","CWE-614"),"html":("weak-sandbox","CWE-693"),"dockerfile":("excessive-privilege","CWE-250")}
        parts=finding.get("check_id","").split(".")
        fallback=legacy.get(parts[1],(None,None)) if len(parts)>1 else (None,None)
        return Issue(self.name, finding.get("check_id", "unknown"),
                     extra.get("message", finding.get("message", "Security pattern detected")),
                     self._parse_severity(extra.get("severity", "warning")),
                     self._normalize_file_path(finding["path"], workspace_path),
                     int(finding.get("start", {}).get("line", 1)), finding.get("check_id", "unknown"),
                     extra.get("fix"), family=extra.get("metadata",{}).get("family",fallback[0]),
                     cwe=extra.get("metadata",{}).get("cwe",fallback[1]),
                     analysis_kind=extra.get("metadata",{}).get("analysis_kind","structural"),
                     end_line=finding.get("end",{}).get("line"), end_column=finding.get("end",{}).get("col"),
                     rule_revision=extra.get("metadata",{}).get("rule_revision","1"),
                     evidence=[{"kind":"source_span","file":self._normalize_file_path(finding["path"],workspace_path),
                                "line":finding.get("start",{}).get("line",1),"end_line":finding.get("end",{}).get("line",1)}]
                              + ([{"kind":"dataflow_trace","trace":extra["dataflow_trace"]}] if extra.get("dataflow_trace") else []))

analyzer_registry.register(SemgrepAnalyzer)
