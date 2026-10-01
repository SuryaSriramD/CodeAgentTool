import hashlib
import io
import json
from pathlib import Path
import uuid
import zipfile

import pytest
from fastapi.testclient import TestClient
from api.app import create_app
from pipeline.projects import prepare_identity, ProjectConflict
from pipeline.store import Store
from settings import Settings


@pytest.fixture
def workspace(tmp_path):
    settings = Settings(storage=tmp_path)
    settings.prepare()
    store = Store(tmp_path)
    return settings, store, store.create_project('Web application')['id']


def publish(workspace, text='eval(input)\n', lines=(1,), version='engine1', status='completed', scanned=True,
            inventory_complete=True, source_inventory=None, file_outcomes=None, tool='semgrep', path='app.js', dependency=None, database=None):
    settings, store, project_id = workspace
    config = {'profile': 'security-v1', 'analyzers': [tool], 'include': [], 'exclude': []}
    baseline = store.pin_baseline(project_id, 'default', config)
    job = store.create_job('scan', config, {'source': 'zip', 'project_id': project_id, 'stream': 'default', 'baseline': baseline})
    claim = store.claim('test')
    assert claim['job_id'] == job['job_id']
    root = settings.storage / 'snapshots' / job['job_id'] / 'source'
    root.mkdir(parents=True)
    hashes = {}
    if text is not None:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text)
        hashes[path] = hashlib.sha256(text.encode()).hexdigest()
    issues = [{'id': uuid.uuid4().hex, 'tool': tool, 'type': 'security', 'rule_id': 'eval-rule', 'file': path,
        'line': line, 'end_line': line, 'source_hash': hashes.get(path), 'severity': 'high', 'message': 'Review evaluation'} for line in lines]
    coverage = {'tool': tool, 'status': status, 'version': version, 'scanned_paths': [path] if scanned else [], 'errors': []}
    if dependency:
        for finding in issues:
            finding['dependency'] = dependency
    if database:
        coverage['database'] = database
    if file_outcomes is not None:
        coverage['file_outcomes'] = file_outcomes
    report = {'schema_version': '2.0', 'job_id': job['job_id'], 'status': status,
        'meta': {'repo': job['source'], 'generated_at': job['submitted_at'], 'snapshot': {'files': hashes,
            'source_inventory': source_inventory if source_inventory is not None else list(hashes), 'inventory_complete': inventory_complete, 'warnings': []}},
        'coverage': [coverage], 'files': [{'path': path, 'issues': issues}] if issues else [],
        'summary': {'high': len(issues), 'critical': 0, 'medium': 0, 'low': 0}}
    prepare_identity(report, root, config)
    report_hash = store.publish_scan_report(job['job_id'], report, claim['_lease_owner'])
    store.finish(job['job_id'], status, owner=claim['_lease_owner'])
    return store.read_artifact(f'report_versions/{job["job_id"]}/{report_hash}.json')


def issue(report):
    return report['files'][0]['issues'][0]


def test_unrelated_line_change_preserves_logical_id_and_human_decision(workspace):
    _, store, project = workspace
    first = publish(workspace)
    logical = issue(first)['logical_id']
    store.set_triage(project, logical, 'dismissed', 0, 'Input is constrained by the caller', 'accepted_risk')
    second = publish(workspace, '\n\neval(input)\n', lines=(3,))
    assert issue(second)['id'] != issue(first)['id']
    assert issue(second)['logical_id'] == logical
    assert store.project_findings(project)['items'][0]['triage']['status'] == 'dismissed'
    assert store.comparison(second['job_id'])['counts'] == {'existing': 1}


def test_changed_tokens_do_not_inherit_dismissal_or_manufacture_resolution(workspace):
    _, store, project = workspace
    first = publish(workspace)
    store.set_triage(project, issue(first)['logical_id'], 'dismissed', 0, 'Constrained input', 'false_positive')
    second = publish(workspace, 'eval(other)\n')
    assert issue(first)['logical_id'] != issue(second)['logical_id']
    records = store.project_findings(project)['items']
    assert next(r for r in records if r['id'] == issue(second)['logical_id'])['triage']['status'] == 'open'
    result = store.comparison(second['job_id'])
    assert result['counts'] == {'new': 1, 'ambiguous': 1}


def test_rule_upgrade_requires_reconfirmation(workspace):
    _, store, project = workspace
    first = publish(workspace)
    store.set_triage(project, issue(first)['logical_id'], 'dismissed', 0, 'Reviewed', 'false_positive')
    second = publish(workspace, version='engine2')
    item = store.project_findings(project)['items'][0]
    assert item['triage']['status'] == 'open'
    assert item['triage']['requires_reconfirmation']
    with pytest.raises(ProjectConflict):
        store.set_triage(project, issue(first)['logical_id'], 'dismissed', 1, 'Stale form', 'false_positive')
    assert store.comparison(second['job_id'])['status'] == 'incomplete'


def test_duplicate_calls_are_ambiguous_but_unchanged_occurrences_stay_distinct(workspace):
    _, store, _ = workspace
    first = publish(workspace, 'eval(input)\neval(input)\n', lines=(1, 2))
    assert len({f['logical_id'] for f in first['files'][0]['issues']}) == 2
    assert all(f['tracking_ambiguous'] for f in first['files'][0]['issues'])
    second = publish(workspace, 'eval(input)\neval(input)\n', lines=(1, 2))
    assert [f['logical_id'] for f in first['files'][0]['issues']] == [f['logical_id'] for f in second['files'][0]['issues']]
    assert store.comparison(second['job_id'])['counts'] == {'existing': 2}


@pytest.mark.parametrize('options,expected', [
    ({'text': 'JSON.parse(input)\n', 'lines': ()}, 'resolved'),
    ({'text': None, 'lines': ()}, 'resolved'),
    ({'text': None, 'lines': (), 'source_inventory': ['app.js']}, 'not_assessed'),
    ({'text': None, 'lines': (), 'inventory_complete': False}, 'not_assessed'),
    ({'text': 'JSON.parse(input)\n', 'lines': (), 'status': 'failed', 'scanned': False}, 'not_assessed'),
    ({'text': 'JSON.parse(input)\n', 'lines': (), 'status': 'partial'}, 'not_assessed'),
    ({'text': 'JSON.parse(input)\n', 'lines': (), 'status': 'partial', 'file_outcomes': {'app.js': {'status': 'completed'}}}, 'resolved'),
    ({'text': 'JSON.parse(input)\n', 'lines': (), 'status': 'partial', 'file_outcomes': [{'path': 'app.js', 'status': 'completed'}]}, 'resolved'),
    ({'text': 'JSON.parse(input)\n', 'lines': (), 'version': 'upgraded'}, 'not_assessed'),
])
def test_absence_requires_compatible_successful_evidence(workspace, options, expected):
    _, store, _ = workspace
    publish(workspace)
    second = publish(workspace, **options)
    assert store.comparison(second['job_id'])['items'][0]['classification'] == expected


def test_no_baseline_and_compact_evidence_survives_report_expiry(workspace):
    settings, store, _ = workspace
    first = publish(workspace)
    assert not store.comparison(first['job_id'])['has_baseline']
    second = publish(workspace, 'JSON.parse(input)\n', lines=())
    for path in (settings.storage / 'reports').glob('*.json'):
        path.unlink()
    assert store.comparison(second['job_id'])['counts'] == {'resolved': 1}


def test_human_notes_and_optimistic_revision_history(workspace):
    _, store, project = workspace
    finding = issue(publish(workspace))['logical_id']
    store.set_triage(project, finding, 'confirmed', 0)
    with pytest.raises(ProjectConflict):
        store.set_triage(project, finding, 'dismissed', 0, 'Old decision', 'accepted_risk')
    with pytest.raises(ValueError):
        store.set_triage(project, finding, 'dismissed', 1)
    store.add_note(project, finding, 'Investigate caller validation')
    result = store.set_triage(project, finding, 'dismissed', 1, 'Caller has an allowlist', 'false_positive')
    assert [event['kind'] for event in result['history']] == ['triage', 'note', 'triage']
    assert result['triage']['revision'] == 2


def test_repository_alias_and_zip_names_are_not_implicit_identity(workspace):
    _, store, _ = workspace
    assert store.create_project('archive')['id'] != store.create_project('archive')['id']
    first = store.create_project('a/b', 'github', 'url:github.com/a/b')
    store.resolve_repository_project(first['id'], 42)
    assert store.create_project('a/b', 'github', 'url:github.com/a/b')['id'] == first['id']


def test_api_projects_triage_comparison_and_saved_export(workspace):
    settings, store, project = workspace
    report = publish(workspace)
    with TestClient(create_app(settings)) as client:
        assert client.get('/projects').json()['total'] == 1
        result = client.get(f'/projects/{project}/findings').json()['items'][0]
        logical = result['id']
        route = f'/projects/{project}/findings/{logical}'
        assert client.patch(route + '/triage', json={'status': 'dismissed', 'expected_revision': 0}).status_code == 400
        assert client.patch(route + '/triage', json={'status': 'confirmed', 'expected_revision': 0}).status_code == 200
        assert client.patch(route + '/triage', json={'status': 'open', 'expected_revision': 0}).status_code == 409
        assert client.post(route + '/notes', json={'body': 'A note'}).status_code == 201
        assert client.get(f'/reports/{report["job_id"]}/comparison').json()['has_baseline'] is False
        result = client.get(f'/reports/{report["job_id"]}/export', params={'format': 'sarif', 'report_hash': report['report_hash']})
        assert result.status_code == 200
        assert result.json()['runs'][0]['results'][0]['ruleId'] == 'semgrep/eval-rule'
        assert client.get(f'/reports/{report["job_id"]}/export', params={'report_hash': '../../secret'}).status_code == 400


def test_submission_project_and_profile_are_persisted(workspace):
    settings, store, project = workspace
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as output:
        output.writestr('main.py', 'print(1)\n')
    with TestClient(create_app(settings)) as client:
        result = client.post('/analyze', data={'project_id': project, 'profile': 'security-v2'}, files={'file': ('source.zip', archive.getvalue())})
        assert result.status_code == 202
        job = store.get(result.json()['job_id'])
        assert job['source']['project_id'] == project and job['source']['baseline'] is None
        assert job['config']['profile'] == 'security-v2'
        assert client.post('/analyze', data={'profile': '../../custom'}, files={'file': ('source.zip', archive.getvalue())}).status_code == 400


def test_same_named_other_project_cannot_be_a_baseline(workspace):
    _, store, _ = workspace
    report = publish(workspace)
    other = store.create_project('Web application')['id']
    with pytest.raises(ValueError):
        store.pin_baseline(other, 'default', {}, report['job_id'], report['report_hash'])


def test_changed_guard_literal_reopens_human_triage_without_changing_identity(workspace):
    _, store, project = workspace
    first = publish(workspace, 'input = "allowed"\neval(input)\n', lines=(2,))
    logical = issue(first)['logical_id']
    store.set_triage(project, logical, 'dismissed', 0, 'Fixed input', 'false_positive')
    second = publish(workspace, 'input = request.query\neval(input)\n', lines=(2,))
    assert issue(second)['logical_id'] == logical
    item = store.project_findings(project)['items'][0]
    assert item['triage']['status'] == 'open' and item['triage']['requires_reconfirmation']
    with pytest.raises(ProjectConflict):
        store.set_triage(project, logical, 'dismissed', 1, 'Stale decision', 'false_positive')


def test_dependency_upgrade_tracks_identity_but_reconfirms_decision(workspace):
    _, store, project = workspace
    package = {'ecosystem': 'npm', 'name': 'example', 'purl': 'pkg:npm/example@1.0.0',
               'advisory_id': 'CVE-2025-0001', 'installed_version': '1.0.0', 'fixed_versions': ['2.0.0']}
    first = publish(workspace, tool='depcheck', dependency=package)
    logical = issue(first)['logical_id']
    store.set_triage(project, logical, 'dismissed', 0, 'Version-specific decision', 'accepted_risk')
    second = publish(workspace, tool='depcheck', dependency={**package, 'purl': 'pkg:npm/example@1.1.0', 'installed_version': '1.1.0'})
    assert issue(second)['logical_id'] == logical
    assert store.project_findings(project)['items'][0]['triage']['requires_reconfirmation']


def test_advisory_age_does_not_change_compatibility_but_database_does(workspace):
    _, store, _ = workspace
    package = {'ecosystem': 'npm', 'name': 'example', 'advisory_id': 'CVE-2025-0001'}
    publish(workspace, tool='depcheck', dependency=package, database={'metadata_hash': 'a', 'age_seconds': 10})
    second = publish(workspace, tool='depcheck', dependency=package, database={'metadata_hash': 'a', 'age_seconds': 20})
    assert store.comparison(second['job_id'])['status'] == 'completed'
    third = publish(workspace, tool='depcheck', dependency=package, database={'metadata_hash': 'b', 'age_seconds': 20})
    assert store.comparison(third['job_id'])['counts'] == {'not_assessed': 1}


@pytest.mark.parametrize('options,expected', [
    ({'text': 'safe()\n', 'lines': ()}, 'resolved'),
    ({'text': 'safe()\n', 'lines': (), 'status': 'partial'}, 'not_assessed'),
])
def test_project_listing_computes_resolution_independently_of_human_status(workspace, options, expected):
    _, store, project = workspace
    first = publish(workspace)
    store.set_triage(project, issue(first)['logical_id'], 'confirmed', 0)
    publish(workspace, **options)
    item = store.project_findings(project)['items'][0]
    assert item['triage']['status'] == 'confirmed'
    assert item['assessment']['classification'] == expected
