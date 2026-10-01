"""Stable scanner service boundary. No LLM, repository execution, or credentials."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from . import analyzer_registry
from .base import AnalysisCancelled
from .common import ROOT, LANGUAGE_EXTENSIONS, DOTNET_LANGUAGES, executable, inventory
from .depcheck_runner import database_ready, database_metadata, LOCKS, MANIFESTS
from .profiles import validate_profile, profile_metadata, rule_inventory, PROFILES
from .dotnet_runner import dotnet_command
from .semgrep_runner import semgrep_core

DEFAULT_ANALYZERS = ('semgrep','bandit','dotnet','depcheck')

def get_capabilities():
    pins = json.loads((ROOT / 'rules/tool-versions.json').read_text())
    output = []
    for name in DEFAULT_ANALYZERS:
        tool = analyzer_registry.get_analyzer(name)
        version = tool.version
        if name == 'dotnet':
            ready = bool(dotnet_command()) and version != 'unavailable'
            languages = sorted(DOTNET_LANGUAGES)
            expected = f'codeagent-dotnet {pins.get("dotnet_analyzer",pins["rulepack"])}'
        else:
            actual_tool = 'trivy' if name == 'depcheck' else name
            ready = bool(executable(actual_tool)) and version != 'unavailable'
            expected = pins[actual_tool]
            languages = sorted(set(LANGUAGE_EXTENSIONS)-DOTNET_LANGUAGES) if name == 'semgrep' else ['python'] if name == 'bandit' else []
        if name == 'depcheck': ready = ready and database_ready()
        if name == 'semgrep': ready = ready and bool(semgrep_core())
        pinned = expected in version
        output.append({'id': name, 'name': name, 'display_name': 'Trivy' if name == 'depcheck' else name,
                       'version': version, 'expected_version': expected, 'ready': ready and pinned, 'available': ready and pinned,
                       'status': 'ready' if ready and pinned else 'unavailable' if not ready else 'version_mismatch',
                       'languages': languages, 'rulepack_version': pins['rulepack'],
                       'profiles':list(PROFILES), 'rule_coverage':{p:[r for r in rule_inventory(p) if r['tool']==name] for p in PROFILES} if name in ('semgrep','dotnet') else {}, 'analysis_kinds':['function-local-taint','structural'] if name=='semgrep' else ['semantic-api','structural'] if name=='dotnet' else ['structural'],
                       **({'ecosystems': sorted(LOCKS), 'requires_database': True,'database':database_metadata(),'advisory_database':{'updated_at':database_metadata().get('updated_at'),'age_hours':(database_metadata().get('age_seconds') or 0)/3600 if database_ready() else None,'error':None if database_ready() else 'Pre-provisioned advisory database unavailable'}} if name == 'depcheck' else {})})
    return output

def scan_workspace(workspace_path, analyzers=None, timeout_sec=600, cancel=lambda: False, profile="security-v1"):
    validate_profile(profile)
    root = Path(workspace_path).resolve(strict=True)
    if not root.is_dir(): raise ValueError('Workspace must be a directory')
    selected = list(dict.fromkeys(analyzers if analyzers is not None else DEFAULT_ANALYZERS))
    if not selected: raise ValueError('Select at least one analyzer')
    unknown = set(selected) - set(DEFAULT_ANALYZERS) - {'trivy'}
    if unknown: raise ValueError(f'Unknown analyzers: {", ".join(sorted(unknown))}')
    selected = list(dict.fromkeys('depcheck' if name=='trivy' else name for name in selected))
    started, coverage, tools, by_path = time.monotonic(), [], [], {}
    summary = {level:0 for level in ('critical','high','medium','low')}
    for name in selected:
        if cancel(): raise AnalysisCancelled('Analysis cancelled')
        remaining = timeout_sec - (time.monotonic()-started)
        analyzer = analyzer_registry.get_analyzer(name, timeout_sec=max(0.01,remaining), cancel=cancel, **({"profile":profile} if name in {"semgrep","dotnet"} else {}))
        report = analyzer.run_analysis(str(root))
        report.coverage['profile']=profile
        report.coverage['ruleset_version']='2.0.0-candidate' if profile=='security-v2' else '1.0.0'
        active_rules=[rule for rule in rule_inventory(profile) if rule['tool']==name]
        report.coverage['rule_ids']=sorted({rule['rule_id'] for rule in active_rules})
        for outcome in report.coverage.get('path_outcomes',[]):
            outcome['rule_ids']=[rule['rule_id'] for rule in active_rules if rule['language']==outcome.get('language')]
        coverage.append(report.coverage)
        tools.append({'name':name, 'version':report.coverage.get('version'), 'status':report.status, 'duration_ms':report.duration_ms})
        for issue in report.issues:
            path = (root / issue.file).resolve(strict=True)
            relative = path.relative_to(root).as_posix()
            if path.is_symlink(): continue
            issue.source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            identity = '\0'.join([issue.tool,issue.rule_id,relative,str(issue.line),issue.source_hash,issue.message])
            issue.id = hashlib.sha256(identity.encode()).hexdigest()
            issue.file = relative
            items = by_path.setdefault(relative, {})
            if issue.id not in items:
                items[issue.id] = issue.to_dict()
                summary[issue.severity.value] += 1
    statuses = [entry['status'] for entry in coverage]
    status = 'partial' if all(s == 'skipped' for s in statuses) else 'completed' if all(s in ('completed','skipped') for s in statuses) else 'partial' if any(s in ('completed','partial') for s in statuses) else 'failed'
    errors = ['No applicable checks ran for the selected analyzers.'] if all(s == 'skipped' for s in statuses) else []
    return {'files':[{'path':path,'issues':sorted(items.values(),key=lambda i:(i['line'],i['rule_id'],i['id']))} for path,items in sorted(by_path.items())],
            'summary':summary, 'coverage':coverage, 'tools':selected, 'tool_runs':tools, 'status':status, 'errors':errors,
            'rulepack_version':'2.0.0-candidate' if profile=='security-v2' else '1.0.0',
            'profile':profile,'profile_digests':profile_metadata(profile,tools),
            'source_inventory':[p for p,_ in inventory(root)],'source_inventory_complete':True}
