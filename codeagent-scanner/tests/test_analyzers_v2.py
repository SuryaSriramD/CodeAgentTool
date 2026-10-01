"""Real-engine release gates plus scanner failure/cancellation boundary tests.

CODEAGENT_REQUIRE_REAL_TOOLS=1 makes missing pinned tools/database a failure.
"""
from __future__ import annotations
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyzers.base import AnalysisCancelled, BaseAnalyzer
from analyzers.common import inventory, LANGUAGE_EXTENSIONS
from analyzers.service import scan_workspace, get_capabilities
from analyzers.depcheck_runner import DepCheckAnalyzer, dependency_inventory
from analyzers.semgrep_runner import SemgrepAnalyzer
from analyzers.dotnet_runner import DotnetAnalyzer

FIXTURES = Path(__file__).resolve().parents[1] / 'fixtures/security-v1'
DOTNET_RULES = {'dotnet.weak-crypto.v1','dotnet.binary-formatter.v1','dotnet.tls-validation.v1','dotnet.xml-dtd.v1'}

@pytest.fixture(scope='module')
def capabilities(): return {entry['id']:entry for entry in get_capabilities()}

def require_tool(name, capabilities):
    if not capabilities[name]['ready']:
        reason = f'{name} unavailable: {capabilities[name]}'
        if os.environ.get('CODEAGENT_REQUIRE_REAL_TOOLS') == '1': pytest.fail(reason)
        pytest.skip(reason)

@pytest.fixture(scope='module')
def source_results(capabilities):
    for name in ('semgrep','dotnet'): require_tool(name, capabilities)
    report = scan_workspace(FIXTURES, ['semgrep','dotnet'])
    assert report['status']=='completed', report['coverage']
    return report

@pytest.mark.parametrize('language', sorted(LANGUAGE_EXTENSIONS))
def test_every_language_real_positive_and_safe_negative(language, source_results):
    hits = {entry['path']:entry['issues'] for entry in source_results['files']}
    positive = [p for p in hits if p.startswith(language+'/positive/')]
    assert positive, f'No actual engine finding for {language}'
    assert not [p for p in hits if p.startswith(language+'/negative/')], language
    if language in ('csharp','vb','fsharp'):
        for case in ('positive','aliases'):
            rules = {issue['rule_id'] for path,issues in hits.items() if path.startswith(language+'/'+case+'/') for issue in issues}
            assert rules == DOTNET_RULES
        assert not [p for p in hits if p.startswith(language+'/shadowed/')]
    for path in positive:
        for issue in hits[path]:
            assert issue['line'] > 0
            assert len(issue['id']) == len(issue['source_hash']) == 64


def test_bandit_real_engine(capabilities, tmp_path):
    require_tool('bandit', capabilities)
    (tmp_path/'source.py').write_text('import subprocess\nsubprocess.run(user_input, shell=True)\n')
    report = scan_workspace(tmp_path, ['bandit'])
    assert report['status']=='completed',report['coverage']
    assert any(i['rule_id']=='B602' for f in report['files'] for i in f['issues'])


def test_trivy_real_offline_known_advisory(capabilities,tmp_path):
    require_tool('depcheck',capabilities)
    (tmp_path/'requirements.txt').write_text('requests==2.19.1\n')
    # A repository must not be able to suppress findings or point the engine at a server.
    (tmp_path/'.trivyignore').write_text('CVE-2018-18074\n')
    (tmp_path/'trivy.yaml').write_text('server: http://127.0.0.1:1\nscanners: []\n')
    report = scan_workspace(tmp_path,['depcheck'])
    assert report['status']=='completed',report['coverage']
    assert any(i['rule_id']=='CVE-2018-18074' for f in report['files'] for i in f['issues'])
    assert report['coverage'][0]['database_updated_at']


def test_unresolved_dependency_manifests_are_not_clean(tmp_path):
    nested=tmp_path/'nested';nested.mkdir()
    (nested/'package.json').write_text('{"dependencies":{"unknown":"*"}}')
    files, unresolved=dependency_inventory(tmp_path)
    assert files==[('nested/package.json','npm')]
    assert unresolved=={'nested/package.json'}
    result=DepCheckAnalyzer().run_analysis(tmp_path)
    assert not result.success
    assert result.status in ('partial','failed')
    assert result.coverage['files_skipped']==1
    assert result.coverage['errors']

@pytest.mark.parametrize('name,filename,invalid',[
    ('semgrep','broken.py','def broken(:\n'),
    ('dotnet','broken.cs','class {\n'),
    ('dotnet','broken.vb','Public Class\n'),
    ('dotnet','broken.fs','module Example\nlet value = (\n'),
])
def test_parse_failures_cannot_report_clean(name, filename, invalid, capabilities,tmp_path):
    require_tool(name,capabilities)
    (tmp_path/filename).write_text(invalid)
    report=scan_workspace(tmp_path,[name])
    assert report['status'] in ('partial','failed')
    assert report['coverage'][0]['errors']
    assert report['coverage'][0]['files_scanned']==0


def test_missing_tool_is_explicit_failure(monkeypatch,tmp_path):
    monkeypatch.setenv('CODEAGENT_SEMGREP_BIN','/nonexistent/codeagent-semgrep')
    (tmp_path/'main.js').write_text('eval(input);')
    result=SemgrepAnalyzer().run_analysis(tmp_path)
    assert result.status=='failed'
    assert result.coverage['files_skipped']==1
    assert result.coverage['errors']


def test_inventory_never_follows_symlinks_or_appledouble(tmp_path):
    (tmp_path/'source.py').write_text('pass')
    (tmp_path/'._source.py').write_bytes(b'not-source')
    (tmp_path/'loop').symlink_to(tmp_path,target_is_directory=True)
    (tmp_path/'linked.py').symlink_to(tmp_path/'source.py')
    assert inventory(tmp_path)==[('source.py','python')]


class ProcessProbe(BaseAnalyzer):
    name='probe'
    version='1'
    def is_applicable(self,workspace):return True
    def run_analysis(self,workspace,**kwargs):raise NotImplementedError

@pytest.mark.skipif(os.name!='posix',reason='POSIX process-group assertion')
@pytest.mark.parametrize('stop',['cancel','timeout'])
def test_cancel_and_timeout_kill_descendants(stop,tmp_path):
    child=tmp_path/'child.py'
    child.write_text('import time\nfrom pathlib import Path\ntime.sleep(1.3)\nPath("escaped").write_text("bad")\ntime.sleep(10)\n')
    parent=tmp_path/'parent.py'
    parent.write_text('import subprocess,sys,time\nsubprocess.Popen([sys.executable,"child.py"])\nprint("started",flush=True)\ntime.sleep(20)\n')
    start=time.monotonic()
    probe=ProcessProbe(timeout_sec=.3 if stop=='timeout' else 10,cancel=lambda: stop=='cancel' and time.monotonic()-start>.3)
    with pytest.raises(AnalysisCancelled if stop=='cancel' else subprocess.TimeoutExpired):
        probe._run_command([sys.executable,str(parent)],str(tmp_path))
    time.sleep(1.4)
    assert not (tmp_path/'escaped').exists()


def test_no_applicable_checks_are_incomplete(tmp_path):
    (tmp_path/'notes.txt').write_text('No source here')
    report=scan_workspace(tmp_path,['bandit'])
    assert report['status']=='partial'
    assert report['errors']
    assert report['tools']==['bandit']


def test_requirements_with_unresolved_ranges_are_incomplete(capabilities,tmp_path):
    require_tool('depcheck', capabilities)
    (tmp_path/'requirements.txt').write_text('requests==2.19.1\nurllib3>=1.0\n')
    report=scan_workspace(tmp_path,['depcheck'])
    assert report['status']=='partial'
    assert any('unresolved requirement' in e for e in report['coverage'][0]['errors'])


DEPENDENCY_FIXTURES = Path(__file__).resolve().parents[1] / 'fixtures/dependencies-v1'
DEPENDENCY_CASES = json.loads((DEPENDENCY_FIXTURES/'expected.json').read_text())

@pytest.fixture(scope='module')
def dependency_results(capabilities,tmp_path_factory):
    import shutil
    require_tool('depcheck', capabilities)
    root=tmp_path_factory.mktemp('mixed-dependency-monorepo')
    for case in DEPENDENCY_CASES:
        for variant in ('vulnerable','patched'):
            destination=root/case['format']/variant/case['filename']
            destination.parent.mkdir(parents=True)
            shutil.copyfile(DEPENDENCY_FIXTURES/case['format']/variant/case['filename'],destination)
    report=scan_workspace(root,['depcheck'])
    assert report['status']=='completed',report['coverage']
    assert report['coverage'][0]['files_scanned']==len(DEPENDENCY_CASES)*2
    return {entry['path']:entry['issues'] for entry in report['files']}

@pytest.mark.parametrize('case',DEPENDENCY_CASES,ids=lambda case:case['format'])
def test_every_supported_dependency_format_vulnerable_and_patched(case,dependency_results):
    positive=f"{case['format']}/vulnerable/{case['filename']}"
    patched=f"{case['format']}/patched/{case['filename']}"
    assert any(i['rule_id']==case['advisory'] and i['message'].startswith(case['package']+' ') for i in dependency_results.get(positive,[]))
    assert not any(i['rule_id']==case['advisory'] and i['message'].startswith(case['package']+' ') for i in dependency_results.get(patched,[]))


def test_advertised_dependency_patterns_have_actual_engine_fixtures():
    import fnmatch
    from analyzers.depcheck_runner import LOCKS
    names={case['filename'] for case in DEPENDENCY_CASES}
    assert len(DEPENDENCY_CASES)==20
    for ecosystem,patterns in LOCKS.items():
        for pattern in patterns:
            assert any(fnmatch.fnmatchcase(name,pattern) for name in names),(ecosystem,pattern)

@pytest.mark.parametrize('filename',['package-lock.json','packages.lock.json','uv.lock','Cargo.lock'])
def test_malformed_dependency_inputs_are_not_clean(filename,capabilities,tmp_path):
    require_tool('depcheck',capabilities)
    (tmp_path/filename).write_text('{ BROKEN = [')
    report=scan_workspace(tmp_path,['depcheck'])
    assert report['status']=='failed'
    assert report['coverage'][0]['files_scanned']==0
    assert report['coverage'][0]['errors']

@pytest.mark.parametrize('filename',['bun.lockb','npm-shrinkwrap.json'])
def test_unverified_dependency_formats_are_explicitly_incomplete(filename,tmp_path):
    (tmp_path/filename).write_bytes(b'\x00unsupported' if filename.endswith('lockb') else b'{"lockfileVersion":3}')
    files,unresolved=dependency_inventory(tmp_path)
    assert files==[(filename,'npm')]
    assert unresolved=={filename}
    report=scan_workspace(tmp_path,['depcheck'])
    assert report['status'] in ('partial','failed')
    assert report['coverage'][0]['files_scanned']==0


@pytest.fixture(scope='module')
def utf16_results(capabilities,tmp_path_factory):
    import hashlib
    for tool in ('semgrep','dotnet'):
        require_tool(tool,capabilities)
    root=tmp_path_factory.mktemp('utf16-source')
    expected={}
    extensions={'csharp':'cs','vb':'vb','fsharp':'fs','xml':'xml'}
    for language,extension in extensions.items():
        source=(FIXTURES/language/'positive'/f'example.{extension}').read_text()
        for byte_order,bom in (('le',b'\xff\xfe'),('be',b'\xfe\xff')):
            raw=bom+source.encode('utf-16-'+byte_order)
            relative=f'{language}-{byte_order}/example.{extension}'
            destination=root/relative
            destination.parent.mkdir()
            destination.write_bytes(raw)
            expected[relative]={'language':language,'hash':hashlib.sha256(raw).hexdigest()}
    report=scan_workspace(root,['semgrep','dotnet'])
    return report,expected

@pytest.mark.parametrize('language',['csharp','vb','fsharp','xml'])
@pytest.mark.parametrize('byte_order',['le','be'])
def test_utf16_source_checked_or_explicitly_incomplete(language,byte_order,utf16_results):
    report,expected=utf16_results
    extension={'csharp':'cs','vb':'vb','fsharp':'fs','xml':'xml'}[language]
    path=f'{language}-{byte_order}/example.{extension}'
    tool='semgrep' if language=='xml' else 'dotnet'
    coverage=next(entry for entry in report['coverage'] if entry['tool']==tool)
    assert coverage['files_discovered']==(2 if language=='xml' else 6)
    issues=next((entry['issues'] for entry in report['files'] if entry['path']==path),[])
    if language!='xml':
        assert path in coverage['scanned_paths'],coverage
        assert {issue['rule_id'] for issue in issues}==DOTNET_RULES
    elif not issues:
        # The engine may lack UTF-16 XML support, but must not silently claim clean.
        assert path not in coverage['scanned_paths'],coverage
        assert coverage['status'] in ('partial','failed')
        assert coverage['errors']
    for issue in issues:
        assert issue['source_hash']==expected[path]['hash']
