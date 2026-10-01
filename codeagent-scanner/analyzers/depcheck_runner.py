"""Offline dependency auditing through one pinned Trivy engine; never resolve/build projects."""
from __future__ import annotations
import fnmatch
import hashlib
from datetime import datetime, timezone
import json
import os
import re
import tempfile
import time
from pathlib import Path
from .base import BaseAnalyzer, Issue, AnalysisCancelled, analyzer_registry
from .common import executable, inventory, tool_version, result, IGNORED_DIRS

# Language and package ecosystem are intentionally separate concepts.
LOCKS = {
    'python': ('requirements*.txt', 'Pipfile.lock', 'poetry.lock', 'uv.lock'),
    'npm': ('package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'bun.lock'),
    'maven': ('gradle.lockfile', '*.sbt.lock'),
    'nuget': ('packages.lock.json', 'packages.config', '*.deps.json'),
    'go': ('go.mod',), 'cargo': ('Cargo.lock',), 'rubygems': ('Gemfile.lock',),
    'composer': ('composer.lock',), 'conan': ('conan.lock',),
    'swift': ('Package.resolved',), 'cocoapods': ('Podfile.lock',),
}
MANIFESTS = {
    'python': ('pyproject.toml', 'Pipfile', 'setup.py', 'setup.cfg'), 'npm': ('package.json', 'bun.lockb', 'npm-shrinkwrap.json'),
    'maven': ('pom.xml', 'build.gradle', 'build.gradle.kts', 'build.sbt'),
    'nuget': ('*.csproj', '*.fsproj', '*.vbproj', 'Directory.Packages.props'),
    'go': ('go.sum',), 'cargo': ('Cargo.toml',), 'rubygems': ('Gemfile', '*.gemspec'),
    'composer': ('composer.json',), 'conan': ('conanfile.txt', 'conanfile.py'),
    'swift': ('Package.swift',), 'cocoapods': ('Podfile',),
}

def dependency_inventory(workspace):
    found, manifests = [], []
    for rel, _ in inventory(workspace):
        name = Path(rel).name
        ecosystem = next((e for e, pats in LOCKS.items() if any(fnmatch.fnmatchcase(name,p) for p in pats)), None)
        if ecosystem:
            found.append((rel, ecosystem))
        else:
            ecosystem = next((e for e,pats in MANIFESTS.items() if any(fnmatch.fnmatchcase(name,p) for p in pats)), None)
            if ecosystem:
                manifests.append((rel, ecosystem))
    resolved = {(str(Path(p).parent), e) for p,e in found}
    unresolved = [(p,e) for p,e in manifests if (str(Path(p).parent),e) not in resolved]
    return sorted(found + unresolved), {p for p,_ in unresolved}

def cache_dir():
    return Path(os.environ.get('CODEAGENT_TRIVY_CACHE_DIR', os.environ.get('TRIVY_CACHE_DIR', '/opt/trivy-cache')))

def database_ready():
    return (cache_dir() / 'db' / 'trivy.db').is_file() and (cache_dir() / 'db' / 'metadata.json').is_file()

def database_metadata():
    try:
        raw=(cache_dir()/'db'/'metadata.json').read_bytes()
        data=json.loads(raw)
        stamp=data.get('UpdatedAt')
        age=max(0,int((datetime.now(timezone.utc)-datetime.fromisoformat(stamp.replace('Z','+00:00'))).total_seconds())) if stamp else None
        return {'updated_at':stamp,'next_update':data.get('NextUpdate'),'metadata_hash':hashlib.sha256(raw).hexdigest(),'age_seconds':age,'ready':database_ready()}
    except (OSError,ValueError,TypeError):
        return {'ready':False,'updated_at':None,'age_seconds':None}

class DepCheckAnalyzer(BaseAnalyzer):
    @property
    def name(self): return 'depcheck'
    @property
    def version(self): return tool_version('trivy')
    def is_applicable(self, workspace_path): return bool(dependency_inventory(workspace_path)[0])
    def _find_dependency_files(self, workspace_path): return [p for p,_ in dependency_inventory(workspace_path)[0]]

    def run_analysis(self, workspace_path, **kwargs):
        report = self._analyze(workspace_path, **kwargs)
        if 'ecosystems' not in report.coverage:
            report.coverage['ecosystems'] = report.coverage.get('languages', [])
        report.coverage['languages'] = []
        return report

    def _analyze(self, workspace_path, **kwargs):
        started = time.monotonic()
        self._command_deadline = started + self.timeout_sec
        files, unresolved = dependency_inventory(workspace_path)
        version = tool_version("trivy", runner=self._run_command)
        errors = [f'{p}: no supported resolved dependency file; dependencies were not installed or resolved' for p in sorted(unresolved)]
        for path, ecosystem in files:
            if ecosystem == 'python' and fnmatch.fnmatchcase(Path(path).name, 'requirements*.txt'):
                text = (Path(workspace_path)/path).read_text(errors='replace')
                logical = text.replace('\\\n', ' ')
                for line_no, raw in enumerate(logical.splitlines(), 1):
                    line = raw.strip()
                    if not line or line.startswith(('#', '--hash=', '--index-url', '--extra-index-url', '--trusted-host', '--find-links', '--no-index')):
                        continue
                    # Only exact PEP 440 versions are audited, never VCS/path/editable/ranges.
                    if not re.match(r'^[A-Za-z0-9_.-]+(?:\[[^]]+\])?\s*==\s*[^*\s;]+(?:\s|;|$)', line):
                        errors.append(f'{path}:{line_no}: unresolved requirement; only exact pinned versions are audited')
        if not files:
            return result(self.name, started, files, version=version)
        if not executable('trivy') or not database_ready():
            return result(self.name, started, files, errors=errors + ['Trivy executable or pre-provisioned vulnerability database unavailable'], version=version)
        if len(unresolved) == len(files):
            return result(self.name, started, files, errors=errors, version=version, status='partial')
        issues, scanned = [], set()
        try:
            with tempfile.TemporaryDirectory(prefix='codeagent-trivy-') as scratch:
                config = Path(scratch,'trusted-config.yaml'); config.write_text('{}\n')
                ignore = Path(scratch,'empty-ignore'); ignore.write_text('')
                cmd = [executable('trivy'), 'fs', '--config', str(config), '--ignorefile', str(ignore),
                       '--cache-dir', str(cache_dir()), '--scanners', 'vuln', '--pkg-types', 'library',
                       '--offline-scan', '--skip-db-update', '--skip-java-db-update', '--skip-check-update',
                       '--skip-version-check', '--disable-telemetry', '--list-all-pkgs', '--include-dev-deps',
                       '--format', 'json', '--quiet', '--timeout', f'{max(1,int(self.timeout_sec))}s',
                       '--skip-dirs', ','.join(sorted(IGNORED_DIRS)), '--skip-files', '**/._*',
                       str(Path(workspace_path).resolve())]
                # Do not let host TRIVY_* variables activate remote servers/plugins or alter the scan.
                env = {k:v for k,v in os.environ.items() if not k.startswith('TRIVY_')}
                env['TRIVY_DISABLE_TELEMETRY'] = 'true'
                proc = self._run_command(cmd, scratch, env=env)
            if proc.returncode != 0:
                raise RuntimeError(f'Trivy exited {proc.returncode}: {proc.stderr[-2500:]}')
            data = json.loads(proc.stdout)
            if not isinstance(data,dict) or 'SchemaVersion' not in data:
                raise ValueError('Trivy output missing report schema')
            known = {p for p,_ in files} - unresolved
            for entry in data.get('Results',[]):
                target = self._normalize_file_path(entry.get('Target',''), workspace_path)
                if target not in known:
                    continue
                if 'Packages' in entry:
                    scanned.add(target)
                for vuln in entry.get('Vulnerabilities',[]) or []:
                    rule = vuln.get('VulnerabilityID', 'unknown-advisory')
                    package, version_found = vuln.get('PkgName','unknown'), vuln.get('InstalledVersion','unknown')
                    fix = vuln.get('FixedVersion')
                    issues.append(Issue(self.name, rule, f'{package} {version_found}: {vuln.get("Title") or vuln.get("Description") or rule}',
                                        self._parse_severity(vuln.get('Severity')), target, 1, rule,
                                        f'Upgrade {package} to a reviewed compatible fixed version: {fix}' if fix else None,
                                        family='vulnerable-dependency',cwe=next(iter(vuln.get('CweIDs') or []),None),
                                        analysis_kind='advisory',end_line=1,
                                        dependency={'ecosystem':dict(files).get(target),'manifest':target,'package':package,'name':package,
                                                    'package_id':vuln.get('PkgID') or package,'purl':(vuln.get('PkgIdentifier') or {}).get('PURL'),
                                                    'advisory':rule,'advisory_id':rule,'installed_version':version_found,'fixed_version':fix,
                                                    'fixed_versions':[v.strip() for v in (fix or '').split(',') if v.strip()]} ))
            for path in sorted(known-scanned):
                errors.append(f'{path}: no package inventory returned; empty, unsupported, unpinned, or unresolved dependency input')
            report = result(self.name, started, files, scanned, issues, errors, version)
            report.coverage['ecosystems'] = report.coverage.pop('languages')
            report.coverage['languages'] = []
            metadata = json.loads((cache_dir() / 'db' / 'metadata.json').read_text())
            report.coverage['database_updated_at'] = metadata.get('UpdatedAt')
            report.coverage['database'] = database_metadata()
            report.coverage['scope'] = 'Known advisories for resolved versions; no dependency restore, build, or source execution.'
            return report
        except AnalysisCancelled:
            raise
        except Exception as exc:
            return result(self.name, started, files, scanned, issues, errors + [str(exc)], version)

analyzer_registry.register(DepCheckAnalyzer)
