"""Real pinned-engine gates for all candidate rules and deterministic fix validation."""
import hashlib
import json
import os
from pathlib import Path
import threading
import time
import pytest
from analyzers.base import AnalysisCancelled
from analyzers.service import scan_workspace,get_capabilities
from analyzers.profiles import profile_metadata
from analyzers.validation import validate_proposal
from analyzers import validation

FIXTURES=Path(__file__).resolve().parents[1]/'fixtures/security-v2'
CASES=json.loads((FIXTURES/'manifest.json').read_text())['cases']

def require_tools(*names):
    capabilities={c['id']:c for c in get_capabilities()}
    for name in names:
        if not capabilities[name]['ready']:
            if os.environ.get('CODEAGENT_REQUIRE_REAL_TOOLS')=='1':pytest.fail(f'{name} unavailable: {capabilities[name]}')
            pytest.skip(f'{name} unavailable')

@pytest.fixture(scope='module')
def candidate():
    require_tools('semgrep','dotnet')
    result=scan_workspace(FIXTURES,['semgrep','dotnet'],profile='security-v2')
    assert result['status']=='completed',result['coverage']
    return result


def test_candidate_fixture_inventory_is_complete():
    assert len(CASES)==228
    cells={(c['language'],c['family']) for c in CASES}
    assert len(cells)==38
    assert len({c['language'] for c in CASES})==17
    for language,family in cells:
        cases=[c for c in CASES if c['language']==language and c['family']==family]
        assert sum(c['expected'] for c in cases)==3
        assert len({(FIXTURES/c['path']).read_bytes() for c in cases})==6


@pytest.mark.parametrize('case',CASES,ids=[c['path'] for c in CASES])
def test_candidate_actual_engine_case(case,candidate):
    hits=[i for f in candidate['files'] if f['path']==case['path'] for i in f['issues'] if i['rule_id']==case['rule_id']]
    assert bool(hits)==case['expected']
    for issue in hits:
        assert issue['family']==case['family']
        assert issue['cwe'].startswith('CWE-')
        assert issue['rule_revision']=='2'
        assert issue['end_line']>=issue['line']
        assert issue['evidence']
    coverage=next(c for c in candidate['coverage'] if c['tool']==('dotnet' if case['language'] in ('csharp','vb','fsharp') else 'semgrep'))
    assert any(p['path']==case['path'] and p['status']=='completed' for p in coverage['path_outcomes'])


def test_v1_stays_default_and_candidate_requires_explicit_selection(tmp_path):
    require_tools('semgrep')
    (tmp_path/'app.py').write_text('from flask import request\nimport requests\ndef handler():\n    return requests.get(request.args.get("url"))\n')
    old=scan_workspace(tmp_path,['semgrep'])
    new=scan_workspace(tmp_path,['semgrep'],profile='security-v2')
    assert old['profile']=='security-v1' and not old['files']
    assert any(i['rule_id']=='codeagent.python.ssrf.v2' for f in new['files'] for i in f['issues'])
    assert old['profile_digests']['source']!=new['profile_digests']['source']
    with pytest.raises(ValueError):scan_workspace(tmp_path,profile='../untrusted')


def test_fsharp_scope_and_alias_resolution_does_not_cross_functions(tmp_path):
    require_tools('dotnet')
    (tmp_path/'scopes.fs').write_text('''module Scope
open System.Runtime.Serialization.Formatters.Binary
open System.Data.Common
open System.Diagnostics
let dangerous (input:System.IO.Stream) =
    let formatter = new BinaryFormatter()
    formatter.Deserialize(input)
let safe (formatter:obj) =
    formatter.ToString()
let command (db:DbConnection) (input:string) =
    let cmd = db.CreateCommand()
    cmd.CommandText <- "SELECT * FROM users WHERE id=" + input
let separate (input:string) =
    let cmd = "display only"
    printfn "%s%s" cmd input
let shell (input:string) =
    let command = "-c " + input
    Process.Start("sh",command) |> ignore
let safeShell () =
    let command = "-c uptime"
    Process.Start("sh",command) |> ignore
''')
    report=scan_workspace(tmp_path,['dotnet'],profile='security-v2')
    assert report['status']=='completed'
    hits=[(i['rule_id'],i['line']) for f in report['files'] for i in f['issues']]
    assert hits==[('dotnet.binary-formatter.v1',7),('dotnet.sql-injection.v2',12),('dotnet.shell-injection.v2',18)]


def snapshot(tmp_path,text='function decode(input) { return eval(input); }\n'):
    root=tmp_path/'snapshot';source=root/'source';source.mkdir(parents=True)
    raw=text.encode();(source/'app.js').write_bytes(raw)
    digest=hashlib.sha256(raw).hexdigest()
    (root/'manifest.json').write_text(json.dumps({'files':{'app.js':digest}}))
    return root,digest


def proposal(digest,**kwargs):
    body={'profile':'security-v1','timeout_sec':120,
          'edits':[{'file':'app.js','source_hash':digest,'original':'eval(input)','replacement':'JSON.parse(input)'}],
          'target_findings':[{'id':'finding-1','tool':'semgrep','rule_id':'codeagent.javascript.security.v1','file':'app.js','line':1}]}
    body.update(kwargs);return body


@pytest.mark.parametrize('mutation,status',[('fixed','passed'),('unchanged','failed'),('broken','incomplete'),('absent-target','incomplete')])
def test_actual_validation_is_anchored_and_never_changes_source(tmp_path,mutation,status):
    require_tools('semgrep')
    root,digest=snapshot(tmp_path);body=proposal(digest)
    if mutation=='unchanged':body['edits'][0]['replacement']='eval(input)'
    if mutation=='broken':body['edits'][0]['replacement']='JSON.parse('
    if mutation=='absent-target':body['target_findings'][0]['rule_id']='missing-rule'
    result=validate_proposal(root,body)
    assert result['status']==status,result
    assert hashlib.sha256((root/'source/app.js').read_bytes()).hexdigest()==digest
    assert result['applied'] is False and result['runtime_tested'] is False
    if status=='passed':assert result['syntax']['status']=='passed' and not result['target_findings_remaining']
    if mutation=='unchanged':assert result['target_findings_remaining']==['finding-1']
    assert result['coverage_before'] and result['coverage_after']


@pytest.mark.parametrize('kind',['hash','original','overlap','offset','traversal','utf8','unexpected','symlink'])
def test_validation_rejects_invalid_anchors_before_running_scanners(tmp_path,monkeypatch,kind):
    root,digest=snapshot(tmp_path);body=proposal(digest)
    if kind=='hash':body['edits'][0]['source_hash']='0'*64
    elif kind=='original':body['edits'][0]['original']='not present'
    elif kind=='overlap':body['edits'].append(dict(body['edits'][0]))
    elif kind=='offset':body['edits'][0].update(start_offset=0,end_offset=3)
    elif kind=='traversal':body['edits'][0]['file']='../app.js'
    elif kind=='utf8':
        raw=b'\xff\xfea\x00';(root/'source/app.js').write_bytes(raw);digest=hashlib.sha256(raw).hexdigest()
        (root/'manifest.json').write_text(json.dumps({'files':{'app.js':digest}}));body['edits'][0]['source_hash']=digest
    elif kind=='unexpected':(root/'source/unexpected.txt').write_text('tampered')
    else:(root/'source/link.js').symlink_to(root/'source/app.js')
    monkeypatch.setattr(validation,'scan_workspace',lambda *args,**kwargs:pytest.fail('Scanner must not run for invalid source'))
    result=validate_proposal(root,body)
    assert result['status'] in ('failed','incomplete') and result['errors']


def fake_scan(root,*args,**kwargs):
    original='eval(input)' in (Path(root)/'app.js').read_text()
    issues=[{'id':'finding-1','tool':'semgrep','rule_id':'codeagent.javascript.security.v1','message':'dynamic eval','file':'app.js','line':1}] if original else []
    return {'status':'completed','coverage':[{'tool':'semgrep','status':'completed','errors':[],
            'files_discovered':1,'files_scanned':1,'files_skipped':0,'scanned_paths':['app.js'],
            'path_outcomes':[{'path':'app.js','language':'javascript','status':'completed'}]}],
            'profile_digests':{'source':'stable','dependency':'stable'},'tool_runs':[{'name':'semgrep','version':'1'}],
            'files':[{'path':'app.js','issues':issues}]}


def test_validation_new_findings_cannot_pass(tmp_path,monkeypatch):
    root,digest=snapshot(tmp_path)
    def changed_scan(path,*args,**kwargs):
        report=fake_scan(path)
        if path!=root/'source':report['files'][0]['issues']=[{'id':'new','tool':'semgrep','rule_id':'different','message':'new issue','file':'app.js','line':1}]
        return report
    monkeypatch.setattr(validation,'scan_workspace',changed_scan)
    result=validate_proposal(root,proposal(digest))
    assert result['status']=='failed' and result['introduced_findings'][0]['id']=='new'


def test_validation_missing_tool_cannot_pass(tmp_path,monkeypatch):
    root,digest=snapshot(tmp_path)
    def failed(*args,**kwargs):
        report=fake_scan(root/'source');report['status']='failed';report['coverage'][0].update(status='failed',errors=['tool unavailable']);return report
    monkeypatch.setattr(validation,'scan_workspace',failed)
    assert validate_proposal(root,proposal(digest))['status']=='incomplete'


def test_validation_cancellation_releases_workspace(tmp_path,monkeypatch):
    root,digest=snapshot(tmp_path)
    monkeypatch.setattr(validation,'scan_workspace',fake_scan)
    with pytest.raises(AnalysisCancelled):validate_proposal(root,proposal(digest),lambda:True)
    assert validate_proposal(root,proposal(digest))['status']=='passed'


def test_validation_workspace_timeout_and_cleanup(tmp_path,monkeypatch):
    root,digest=snapshot(tmp_path);scratch=[]
    def slow(path,*args,**kwargs):
        scratch.append(path);time.sleep(.03);return fake_scan(path)
    monkeypatch.setattr(validation,'scan_workspace',slow)
    result=validate_proposal(root,proposal(digest,timeout_sec=.02))
    assert result['status']=='incomplete' and 'budget' in result['errors'][0]
    assert all(not p.exists() for p in scratch if p!=root/'source')


def test_validation_preserves_crlf_and_offsets(tmp_path,monkeypatch):
    text='// café\r\nfunction decode(input) { return eval(input); }\r\n'
    root,digest=snapshot(tmp_path,text);body=proposal(digest)
    body['target_findings'][0]['line']=1 # Fake engine's preserved evidence position.
    start=text.index('eval(input)');body['edits'][0].update(start_offset=start,end_offset=start+len('eval(input)'))
    def check_crlf(path,*args,**kwargs):
        assert (Path(path)/'app.js').read_bytes().count(b'\r\n')==2
        return fake_scan(path)
    monkeypatch.setattr(validation,'scan_workspace',check_crlf)
    assert validate_proposal(root,body)['status']=='passed'


def test_profiles_ignore_database_age_but_track_revision(monkeypatch):
    from analyzers import depcheck_runner
    monkeypatch.setattr(depcheck_runner,'database_metadata',lambda:{'updated_at':'frozen','age_seconds':1})
    first=profile_metadata()
    monkeypatch.setattr(depcheck_runner,'database_metadata',lambda:{'updated_at':'frozen','age_seconds':100})
    assert profile_metadata()==first
    monkeypatch.setattr(depcheck_runner,'database_metadata',lambda:{'updated_at':'new','age_seconds':100})
    later=profile_metadata()
    assert later['source']==first['source'] and later['dependency']!=first['dependency']


def test_fsharp_type_aliases_and_imports_are_lexically_scoped(tmp_path):
    require_tools('dotnet')
    (tmp_path/'modules.fs').write_text('''module Lexical
module Dangerous =
    type Digest = System.Security.Cryptography.MD5
    let hash () = Digest.Create()
module Safe =
    type Digest = System.Security.Cryptography.SHA256
    let hash () = Digest.Create()
module Imported =
    open System.Security.Cryptography
    let hash () = MD5.Create()
module Unrelated =
    type MD5 =
        static member Create() = "safe domain identifier"
    let hash () = MD5.Create()
''')
    report=scan_workspace(tmp_path,['dotnet'],profile='security-v2')
    assert report['status']=='completed',report['coverage']
    assert [(i['rule_id'],i['line']) for f in report['files'] for i in f['issues']]==[('dotnet.weak-crypto.v1',4),('dotnet.weak-crypto.v1',10)]


def test_fsharp_lambda_parameter_shadows_receiver(tmp_path):
    require_tools('dotnet')
    (tmp_path/'lambda.fs').write_text('''module LambdaScope
open System.Runtime.Serialization.Formatters.Binary
let handle stream =
    let formatter = new BinaryFormatter()
    let dangerous = formatter.Deserialize(stream)
    let safe = List.map (fun formatter -> formatter.Deserialize(stream)) []
    dangerous
''')
    result=scan_workspace(tmp_path,['dotnet'],profile='security-v2')
    assert result['status']=='completed'
    assert [i['line'] for f in result['files'] for i in f['issues']]==[5]


def test_validation_detects_new_evidence_when_rule_counts_stay_constant(tmp_path,monkeypatch):
    root,digest=snapshot(tmp_path,'function decode(input) { return eval(input); }\nconst existing = eval(oldInput);\n')
    body=proposal(digest)
    body['edits'].append({'file':'app.js','source_hash':digest,'original':'eval(oldInput)','replacement':'eval(newInput)'})
    def two_rules(path,*args,**kwargs):
        report=fake_scan(path)
        report['files'][0]['issues'].append({'id':'other','tool':'semgrep','rule_id':'existing-rule','message':'existing issue','file':'app.js','line':2})
        return report
    monkeypatch.setattr(validation,'scan_workspace',two_rules)
    result=validate_proposal(root,body)
    assert result['status']=='failed' and result['introduced_findings'][0]['id']=='other'


def test_old_dotnet_binary_cannot_claim_candidate_coverage(tmp_path,monkeypatch):
    from analyzers import dotnet_runner
    (tmp_path/'source.cs').write_text('class Source {}')
    monkeypatch.setattr(dotnet_runner,'dotnet_command',lambda:['unexecuted','analyzer.dll'])
    monkeypatch.setattr(dotnet_runner.DotnetAnalyzer,'_version',lambda *args:'codeagent-dotnet 1.0.0')
    report=dotnet_runner.DotnetAnalyzer(profile='security-v2').run_analysis(tmp_path)
    assert report.status=='failed' and '1.1.0' in report.coverage['errors'][0]


def test_version_timeout_kills_wrapper_descendants(tmp_path,monkeypatch):
    import sys
    from analyzers import common
    child=tmp_path/'child.py'
    child.write_text('import time\nfrom pathlib import Path\ntime.sleep(1)\nPath('+repr(str(tmp_path/'leaked'))+').write_text("bad")\ntime.sleep(5)\n')
    wrapper=tmp_path/'wrapper.py'
    wrapper.write_text('import subprocess,sys,time\nsubprocess.Popen([sys.executable,'+repr(str(child))+'])\ntime.sleep(5)\n')
    monkeypatch.setattr(common,'VERSION_PROBE_TIMEOUT',.15)
    assert common.command_version('test-timeout',str(wrapper),[sys.executable,str(wrapper)])=='unavailable'
    time.sleep(1.1)
    assert not (tmp_path/'leaked').exists()


def test_version_probes_are_singleflight_with_negative_cache(tmp_path):
    import sys
    from concurrent.futures import ThreadPoolExecutor
    from analyzers import common
    for success in (True,False):
        marker=tmp_path/str(success)
        code='from pathlib import Path;import time; p=Path('+repr(str(marker))+');p.write_text(p.read_text()+"x" if p.exists() else "x");time.sleep(.1);print("1.2.3");raise SystemExit('+('0' if success else '1')+')'
        command=[sys.executable,'-c',code]
        with ThreadPoolExecutor(max_workers=8) as pool:
            outputs=list(pool.map(lambda _:common.command_version('test-singleflight-'+str(success),sys.executable,command),range(8)))
        assert outputs==[('1.2.3' if success else 'unavailable')]*8
        assert marker.read_text()=='x'
        common.command_version('test-singleflight-'+str(success),sys.executable,command)
        assert marker.read_text()=='x'


def test_foreign_configured_semgrep_is_actually_probed(tmp_path,monkeypatch):
    from analyzers import common,semgrep_runner
    binary=tmp_path/'custom-semgrep'
    binary.write_text('#!/bin/sh\nprintf "foreign-semgrep-9\\n"\n');binary.chmod(0o755)
    monkeypatch.setenv('CODEAGENT_SEMGREP_BIN',str(binary))
    monkeypatch.setattr(semgrep_runner,'semgrep_core',lambda:'/misleading/bundled-core')
    assert common.tool_version('semgrep')=='foreign-semgrep-9'


def test_bandit_metadata_cannot_hide_foreign_entrypoint(tmp_path,monkeypatch):
    from analyzers import common
    binary=tmp_path/'bin/bandit';binary.parent.mkdir()
    binary.write_text('#!/bin/sh\nprintf "foreign-bandit-9\\n"\n');binary.chmod(0o755)
    metadata=tmp_path/'lib/python3.12/site-packages/bandit-1.9.4.dist-info/METADATA';metadata.parent.mkdir(parents=True)
    metadata.write_text('Name: bandit\nVersion: 1.9.4\n')
    monkeypatch.setenv('CODEAGENT_BANDIT_BIN',str(binary))
    assert common.tool_version('bandit')=='foreign-bandit-9'
