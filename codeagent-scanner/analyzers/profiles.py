"""Pinned, repository-owned profiles. Never consume repository scanner configuration."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .common import ROOT, tool_version

PROFILES = ('security-v1','security-v2')

def validate_profile(profile):
    if profile not in PROFILES: raise ValueError('Unknown scanner profile')
    return profile

def profile_metadata(profile='security-v1', tool_runs=()):
    validate_profile(profile)
    rule_bytes=(ROOT/'rules'/f'{profile}.yaml').read_bytes()
    pins=json.loads((ROOT/'rules/tool-versions.json').read_text())
    ingestion={name:hashlib.sha256((ROOT/'ingestion'/name).read_bytes()).hexdigest()
               for name in ('policy.py','snapshots.py')}
    source={'profile':profile,'rules':hashlib.sha256(rule_bytes).hexdigest(),'versions':{key:value for key,value in pins.items() if key!='trivy'},
            'coverage_contract':'native-parser-evidence/2','ingestion':ingestion,
            'adapters':{name:hashlib.sha256((ROOT/'analyzers'/name).read_bytes()).hexdigest()
                        for name in ('semgrep_runner.py','parser_evidence.py','bandit_runner.py','dotnet_runner.py','common.py','service.py','validation.py')},
            'dotnet':{name:hashlib.sha256((ROOT/'dotnet-analyzer'/name).read_bytes()).hexdigest()
                      for name in ('Program.fs','Roslyn/Analyzer.cs')}}
    from .dotnet_runner import DotnetAnalyzer
    source['effective_tools']=[{'name':'semgrep','version':tool_version('semgrep')},
                               {'name':'bandit','version':tool_version('bandit')},
                               {'name':'dotnet','version':DotnetAnalyzer().version}]
    from .depcheck_runner import database_metadata
    database=database_metadata()
    dependency={'version':tool_version('trivy'),'expected_version':pins['trivy'],
                'adapter':hashlib.sha256((ROOT/'analyzers/depcheck_runner.py').read_bytes()).hexdigest(),
                'ingestion':ingestion,'inventory':hashlib.sha256((ROOT/'analyzers/common.py').read_bytes()).hexdigest(),
                'database':{k:v for k,v in database.items() if k!='age_seconds'}}
    digest=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'source':digest(source),'dependency':digest(dependency),'source_details':source,'dependency_details':dependency}


def rule_inventory(profile='security-v1'):
    validate_profile(profile)
    output=[]
    for rule in json.loads((ROOT/'rules'/f'{profile}.yaml').read_text())['rules']:
        metadata=rule.get('metadata',{})
        for language in rule['languages']:
            output.append({'tool':'semgrep','language':language,'rule_id':rule['id'],
                           'family':metadata.get('family'),'cwe':metadata.get('cwe'),
                           'analysis_kind':metadata.get('analysis_kind','structural'),
                           'rule_revision':metadata.get('rule_revision','1')})
    dotnet=[('weak-crypto','CWE-327',1),('binary-formatter','CWE-502',1),('tls-validation','CWE-295',1),('xml-dtd','CWE-611',1)]
    if profile=='security-v2':dotnet.extend([('sql-injection','CWE-89',2),('shell-injection','CWE-78',2)])
    for language in ('csharp','vb','fsharp'):
        for family,cwe,revision in dotnet:
            output.append({'tool':'dotnet','language':language,'rule_id':f'dotnet.{family}.v{revision}',
                           'family':family,'cwe':cwe,'analysis_kind':'structural' if language=='fsharp' else 'semantic-api',
                           'rule_revision':str(revision)})
    return output
