import asyncio
import io
import json
from pathlib import Path
import zipfile

import pytest
from fastapi.testclient import TestClient
import cli
from api.app import create_app
from integration.models import ProviderResult, ProviderError, ReviewCancelled
from pipeline.orchestrator import JobOrchestrator
from pipeline.orchestrator import verify_profile
from ingestion.snapshots import SourceError, build_snapshot
from pipeline.provider_checks import connection_fingerprint, check_provider
from pipeline.store import Store
from settings import Settings


@pytest.fixture
def settings(tmp_path):
    config = Settings(storage=tmp_path, openai_key='server-secret-canary', github_token='', workspace_password='', session_secret='', team_mode=False)
    config.prepare()
    return config


def ready_report():
    return {'status': 'completed', 'coverage': [{'status': 'completed'}], 'files': [
        {'issues': [{'severity': 'high', 'logical_id': 'one'}]}]}


@pytest.mark.parametrize('threshold,policy,comparison,initialize,dismissed,expected', [
    ('high', 'all', None, False, (), 1),
    ('critical', 'all', None, False, (), 0),
    ('high', 'all', None, False, ('one',), 0),
    ('high', 'new', {'has_baseline': False}, False, (), 2),
    ('high', 'new', {'has_baseline': False}, True, (), 0),
    ('high', 'new', {'has_baseline': True, 'status': 'incomplete'}, False, (), 2),
    ('high', 'new', {'has_baseline': True, 'status': 'completed', 'items': [{'classification': 'existing', 'finding': {'severity': 'high'}}]}, False, (), 0),
    ('high', 'new', {'has_baseline': True, 'status': 'completed', 'items': [{'classification': 'new', 'finding': {'severity': 'high'}}]}, False, (), 1),
])
def test_policy_codes(threshold, policy, comparison, initialize, dismissed, expected):
    assert cli.policy_result(ready_report(), threshold, policy, comparison, initialize, dismissed) == expected


@pytest.mark.parametrize('status', ['partial', 'failed', 'interrupted', 'canceled'])
def test_incomplete_is_never_a_passing_policy(status):
    report = ready_report()
    report['status'] = status
    assert cli.policy_result(report) == 2


def test_archive_applies_filters_limits_and_excludes_credentials(tmp_path):
    (tmp_path / 'main.py').write_text('print(1)')
    (tmp_path / '.env').write_text('SECRET=value')
    (tmp_path / 'nested').mkdir()
    (tmp_path / 'nested/skip.py').write_text('skip')
    archive = io.BytesIO()
    cli.archive_source(tmp_path, archive, exclude=['nested/**'])
    with zipfile.ZipFile(archive) as source:
        assert source.namelist() == ['main.py']
    with pytest.raises(cli.CLIError):
        cli.archive_source(tmp_path, io.BytesIO(), max_expanded=1)


def test_archive_rejects_symlinks_unless_explicitly_excluded(tmp_path):
    (tmp_path / 'main.py').write_text('print(1)')
    (tmp_path / 'linked').symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(cli.CLIError):
        cli.archive_source(tmp_path, io.BytesIO())
    archive = io.BytesIO()
    cli.archive_source(tmp_path, archive, exclude=['linked/**'])
    assert zipfile.ZipFile(archive).namelist() == ['main.py']


def test_local_archive_and_server_share_bin_source_policy(tmp_path, settings):
    root = tmp_path / 'local-source'
    sources = {
        'bin/entry.sh': "#!/usr/bin/env bash\nprintf '%s\\n' \"$1\"\n",
        'nested/bin/status.py': "def status():\n    return 'ready'\n",
        'bin/project/requirements.txt': 'requests==2.32.4\n',
    }
    excluded = {
        'bin/Debug/App.dll': 'compiled output',
        'bin/Debug/App.pdb': 'compiled symbols',
        'bin/.env': 'SECRET=not-uploaded',
        'bin/.DS_Store': 'metadata',
        'bin/._entry.sh': 'metadata',
        'build/bin/generated.sh': 'generated source',
        'bin/obj/generated.cs': 'generated source',
        'vendor/bin/third-party.sh': 'vendored source',
    }
    for name, content in {**sources, **excluded}.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    archive = io.BytesIO()
    cli.archive_source(root, archive)
    with zipfile.ZipFile(archive) as zipped:
        assert set(zipped.namelist()) == set(sources)
        assert {name: zipped.read(name).decode() for name in zipped.namelist()} == sources
    upload = tmp_path / 'cli-upload.zip'
    upload.write_bytes(archive.getvalue())
    manifest = build_snapshot(upload, 'cli-bin-sources', settings, {'source': 'zip'}, {})
    assert set(manifest['files']) == set(sources)
    assert manifest['excluded_files'] == []


def test_local_bin_source_still_obeys_explicit_exclusion(tmp_path):
    (tmp_path / 'bin').mkdir()
    (tmp_path / 'bin/kept.sh').write_text("printf 'kept\\n'\n")
    (tmp_path / 'bin/excluded.sh').write_text("printf 'excluded\\n'\n")
    archive = io.BytesIO()
    cli.archive_source(tmp_path, archive, exclude=['bin/excluded.sh'])
    with zipfile.ZipFile(archive) as zipped:
        assert zipped.namelist() == ['bin/kept.sh']


def test_cli_requires_explicit_project_and_review_destination(monkeypatch, tmp_path):
    assert cli.main(['scan', str(tmp_path)]) == 2
    assert cli.main(['scan', str(tmp_path), '--project-name', 'Demo', '--review']) == 2


def test_cli_dismissal_is_bound_to_the_saved_evidence_version(monkeypatch):
    client = cli.Client('http://localhost:8000')
    original = {'logical_id': 'one', 'fingerprint': 'v1:a', 'rule_digest': 'rules', 'evidence_digest': 'old'}
    current = {**original, 'evidence_digest': 'new', 'triage': {'status': 'dismissed'}}
    monkeypatch.setattr(client, 'json', lambda *args, **kwargs: {'total': 1, 'items': [current]})
    report = {'files': [{'issues': [original]}]}
    assert client.dismissals('project', report) == set()
    current['evidence_digest'] = 'old'
    assert client.dismissals('project', report) == {'one'}
    client.http.close()


def test_scanner_profile_pins_refuse_changed_rules_or_database():
    config = {'profile_digests': {'source': 'source-v1', 'dependency': 'database-v1'}}
    output = {'profile_digests': {'source': 'source-v1', 'dependency': 'database-v2'}}
    verify_profile(output, config, 'semgrep')
    with pytest.raises(SourceError, match='Pinned dependency scanner profile'):
        verify_profile(output, config, 'depcheck')
    with pytest.raises(SourceError, match='Pinned source scanner profile'):
        verify_profile({}, config, 'bandit')
    verify_profile(output, {}, 'depcheck')  # Historical jobs are labeled unverified.


def test_recovery_can_retry_static_validation_without_repeating_uncertain_model(settings):
    store = Store(settings.storage)
    job = store.create_job('review', {'provider': 'ollama', 'model': 'local'}, {})
    claim = store.claim('one')
    store.save_step(job['job_id'], 'validation', {'role': 'validator', 'status': 'running'}, claim['_lease_owner'])
    store.save_step(job['job_id'], 'author', {'role': 'author', 'status': 'completed'}, claim['_lease_owner'])
    with store.connect(write=True) as db:
        db.execute('UPDATE jobs SET lease_until=0 WHERE job_id=?', (job['job_id'],))
    store.recover()
    assert store.get(job['job_id'])['status'] == 'queued'
    assert store.load_step(job['job_id'], 'validation')['status'] == 'retry_requested'
    assert store.load_step(job['job_id'], 'author')['status'] == 'completed'


def test_provider_checks_share_ollama_slot_with_reviews(settings):
    store = Store(settings.storage)
    review = store.create_job('review', {'provider': 'ollama', 'model': 'local'}, {})
    check = store.create_job('provider_check', {'provider': 'ollama', 'model': 'local'}, {})
    assert store.claim('one')['job_id'] == review['job_id']
    assert store.claim('two') is None
    store.cancel(review['job_id'])
    assert store.claim('two')['job_id'] == check['job_id']


def test_provider_check_redacts_outputs_and_persists_configuration(settings, monkeypatch):
    from pipeline import provider_checks
    class Fake:
        async def generate(self, *args, **kwargs):
            return ProviderResult({'ok': True}, {'effective_model': settings.openai_key, settings.openai_key: 'hidden', 'total_tokens': 8})
        async def aclose(self):
            pass
    monkeypatch.setattr(provider_checks, 'get_provider', lambda config: Fake())
    orchestrator = JobOrchestrator(settings=settings)
    config = {'provider': 'openai', 'model': 'exact-id', '_connection_fingerprint': connection_fingerprint(settings, 'openai', 'exact-id')}
    job = orchestrator.store.create_job('provider_check', config, {'source': 'synthetic'})
    orchestrator.execute(orchestrator.store.claim('one'))
    saved = orchestrator.store.get(job['job_id'])
    assert saved['status'] == 'completed'
    assert saved['progress']['percent'] == 100
    output = saved['steps'][0]['output']
    assert output['schema_test_passed'] and output['reachable']
    assert settings.openai_key not in json.dumps(saved)
    persisted = orchestrator.store.get_setting('provider_test:openai:exact-id')
    assert settings.openai_key not in json.dumps(persisted)
    assert persisted['usage']['total_tokens'] == 8


@pytest.mark.parametrize('uncertain,expected', [(False, 'failed'), (True, 'interrupted')])
def test_provider_failures_are_visible_and_uncertain_calls_require_retry(settings, monkeypatch, uncertain, expected):
    from pipeline import provider_checks
    class Fake:
        async def generate(self, *args, **kwargs):
            raise ProviderError('Synthetic failure', code='interrupted' if uncertain else 'invalid_output', uncertain=uncertain)
        async def aclose(self):
            pass
    monkeypatch.setattr(provider_checks, 'get_provider', lambda config: Fake())
    orchestrator = JobOrchestrator(settings=settings)
    config = {'provider': 'openai', 'model': 'exact-id', '_connection_fingerprint': connection_fingerprint(settings, 'openai', 'exact-id')}
    job = orchestrator.store.create_job('provider_check', config, {})
    orchestrator.execute(orchestrator.store.claim('one'))
    saved = orchestrator.store.get(job['job_id'])
    assert saved['status'] == expected
    assert saved['steps'][0]['status'] == expected
    assert not saved['steps'][0]['output']['schema_test_passed']


@pytest.mark.asyncio
async def test_provider_check_cancellation_closes_connection(monkeypatch):
    from pipeline import provider_checks
    state = {'closed': False}
    class Fake:
        async def generate(self, *args, **kwargs):
            await asyncio.Event().wait()
        async def aclose(self):
            state['closed'] = True
    monkeypatch.setattr(provider_checks, 'get_provider', lambda config: Fake())
    with pytest.raises(ReviewCancelled):
        await check_provider({}, lambda: True)
    assert state['closed']


def test_saving_configuration_makes_no_model_call_and_check_deduplicates(settings, monkeypatch):
    with TestClient(create_app(settings)) as client:
        assert client.patch('/config/ai', json={'provider': 'openai', 'model': 'exact-id', 'max_model_calls': 10}).status_code == 200
        assert Store(settings.storage).list()['total'] == 0
        first = client.post('/config/ai/test', json={})
        second = client.post('/config/ai/test', json={})
        assert first.status_code == second.status_code == 202
        assert first.json()['job_id'] == second.json()['job_id']
        job = Store(settings.storage).get(first.json()['job_id'])
        assert job['kind'] == 'provider_check' and job['source']['source'] == 'synthetic'


def test_implicit_and_explicit_default_branch_pin_the_same_project_stream(settings, monkeypatch):
    from api import app as api_module
    monkeypatch.setattr(api_module, 'github_repository_identity', lambda url, settings: {'id': 7, 'default_branch': 'main', 'url': 'https://github.com/o/r'})
    with TestClient(create_app(settings)) as client:
        one = client.post('/analyze', data={'github_url': 'https://github.com/o/r'}).json()
        two = client.post('/analyze', data={'github_url': 'https://github.com/o/r', 'ref': 'main'}).json()
        store = Store(settings.storage)
        first, second = store.get(one['job_id']), store.get(two['job_id'])
        assert first['source']['stream'] == second['source']['stream'] == 'main'
        assert first['source']['project_id'] == second['source']['project_id']
        monkeypatch.setattr(api_module, 'github_repository_identity', lambda url, settings: {'id': 7, 'default_branch': 'trunk', 'url': 'https://github.com/o/r'})
        three = client.post('/analyze', data={'github_url': 'https://github.com/o/r'}).json()
        assert store.get(three['job_id'])['source']['stream'] == 'trunk'
