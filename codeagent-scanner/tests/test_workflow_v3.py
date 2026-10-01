"""No-network safety gates for grouped review and trusted static validation."""
import copy
import json
from pathlib import Path

import pytest

from integration.context import SourceContext, ContextError, combined_diff, proposal_conflicts
from integration.models import ReviewCancelled
from integration.workflow import _finding_groups
from integration import workflow
from tests.test_workflow_v2 import review_case, TRIAGE, AUTHOR, APPROVE, FakeProvider


@pytest.mark.asyncio
async def test_missing_validator_cannot_be_overridden_by_model_approval(review_case):
    result, fake = await review_case.run([TRIAGE, AUTHOR, APPROVE], _validator=None)
    proposal = result['proposals'][0]
    assert proposal['validation']['status'] == 'incomplete'
    assert proposal['review']['decision'] == 'approve'
    assert proposal['review']['validation_blocked'] is True
    assert proposal['status'] == 'unresolved' and result['status'] == 'partial'
    assert not proposal['applied'] and not proposal['tested']


@pytest.mark.asyncio
@pytest.mark.parametrize('validation', [
    {'status': 'failed', 'syntax': {'status': 'failed'}, 'errors': ['syntax error']},
    {'status': 'passed', 'syntax': {'status': 'passed'}, 'target_findings_remaining': ['finding1']},
    {'status': 'passed', 'syntax': {'status': 'passed'}, 'introduced_findings': [{'rule_id': 'new'}]},
    {'status': 'passed'}, {'status': 'imaginary'},
])
async def test_validation_failure_or_missing_evidence_blocks_approval(review_case, validation):
    async def validate(payload, *, is_cancelled):
        assert payload['timeout_sec'] <= 120
        assert payload['target_findings'][0]['id'] == 'finding1'
        return validation
    result, _ = await review_case.run([TRIAGE, AUTHOR, APPROVE], _validator=validate)
    assert result['proposals'][0]['status'] == 'unresolved'
    assert result['proposals'][0]['validation']['status'] in {'failed', 'incomplete'}


@pytest.mark.asyncio
async def test_validation_is_checkpointed_and_revisions_revalidate(review_case):
    calls = []
    async def validate(payload, *, is_cancelled):
        calls.append(payload)
        return {'status': 'passed', 'syntax': {'status': 'passed'}, 'coverage_after': [{'status': 'completed'}]}
    revision = {'decision': 'request_revision', 'comments': ['Describe the argument type']}
    result, _ = await review_case.run([TRIAGE, AUTHOR, revision, AUTHOR, APPROVE], _validator=validate)
    assert len(calls) == 2
    replay, provider = await review_case.run([], _validator=validate)
    assert not provider.calls and len(calls) == 2
    assert replay['proposals'] == result['proposals']
    author_revision = review_case.steps['finding:finding1:author:1']
    assert author_revision['status'] == 'completed'


@pytest.mark.asyncio
@pytest.mark.parametrize('changed_proof', [False, True])
async def test_changed_validator_implementation_reruns_proof_without_repeating_authorship(review_case, monkeypatch, changed_proof):
    implementation = {'digest': 'old-implementation'}
    monkeypatch.setattr(workflow, 'validation_implementation_digest', lambda: implementation['digest'])
    calls = []

    async def validate(payload, *, is_cancelled):
        calls.append(payload)
        if changed_proof and implementation['digest'] == 'repaired-implementation':
            return {'status': 'incomplete', 'syntax': {'status': 'incomplete'},
                    'errors': ['Parser proof no longer meets the coverage contract']}
        return {'status': 'passed', 'syntax': {'status': 'passed'},
                'coverage_after': [{'tool': 'semgrep', 'status': 'completed'}]}

    first, _ = await review_case.run([TRIAGE, AUTHOR, APPROVE], _validator=validate)
    author_steps = {key: copy.deepcopy(value) for key, value in review_case.steps.items()
                    if value['role'] in {'analyst', 'author'}}
    original = copy.deepcopy(review_case.steps['finding:finding1:validator:0'])
    repeated, provider = await review_case.run([], _validator=validate)
    assert len(calls) == 1 and not provider.calls
    assert repeated['proposals'] == first['proposals']

    implementation['digest'] = 'repaired-implementation'
    repaired, provider = await review_case.run([APPROVE] if changed_proof else [], _validator=validate)
    assert len(calls) == 2
    validator = review_case.steps['finding:finding1:validator:0']
    assert validator['attempt'] == original['attempt'] + 1
    assert validator['input_hash'] != original['input_hash']
    assert validator['validation_implementation_digest'] == 'repaired-implementation'
    assert all(review_case.steps[key] == value for key, value in author_steps.items())
    assert len(provider.calls) == int(changed_proof)
    if changed_proof:
        assert provider.calls[0]['schema'] == 'ReviewerOutput'
        assert repaired['proposals'][0]['validation']['status'] == 'incomplete'
        assert repaired['proposals'][0]['status'] == 'unresolved'
    else:
        assert repaired['proposals'] == first['proposals']


@pytest.mark.parametrize('changed_path', [
    'analyzers/validation.py', 'analyzers/parser_evidence.py',
    'analyzers/profiles.py', 'ingestion/policy.py',
])
def test_validation_checkpoint_digest_tracks_trusted_implementation_bytes(tmp_path, monkeypatch, changed_path):
    for name in workflow.VALIDATION_IMPLEMENTATION_FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'original trusted implementation fixture\n')
    monkeypatch.setattr(workflow, '__file__', str(tmp_path / 'integration/workflow.py'))
    original = workflow.validation_implementation_digest()
    assert workflow.validation_implementation_digest() == original
    (tmp_path / changed_path).write_bytes(b'repaired trusted implementation fixture\n')
    assert workflow.validation_implementation_digest() != original


@pytest.mark.asyncio
async def test_validator_exception_keeps_partial_proposal(review_case):
    async def validate(*args, **kwargs):
        raise ConnectionError('scanner worker unavailable')
    result, _ = await review_case.run([TRIAGE, AUTHOR, APPROVE], _validator=validate)
    assert result['proposals'][0]['validation']['errors'] == ['scanner worker unavailable']
    assert result['status'] == 'partial'


@pytest.mark.asyncio
async def test_single_agent_reuses_one_conversation_and_multi_agent_is_fresh(review_case):
    single, provider = await review_case.run([TRIAGE, AUTHOR, APPROVE], workflow_mode='single_agent')
    assert [len(call['messages']) for call in provider.calls] == [2, 4, 6]
    assert provider.calls[-1]['messages'][2]['role'] == 'assistant'
    assert json.loads(provider.calls[-1]['messages'][2]['content'])['disposition'] == 'confirmed'
    multi, provider = await review_case.run([TRIAGE, AUTHOR, APPROVE], workflow_mode='multi_agent')
    assert [len(call['messages']) for call in provider.calls] == [2, 2, 2]
    assert single['workflow_mode'] == 'single_agent' and multi['workflow_mode'] == 'multi_agent'


@pytest.mark.asyncio
async def test_single_agent_cache_reconstructs_the_conversation(review_case):
    result, _ = await review_case.run([TRIAGE, AUTHOR, APPROVE], workflow_mode='single_agent')
    repeated, provider = await review_case.run([], workflow_mode='single_agent')
    assert not provider.calls and repeated['proposals'] == result['proposals']


@pytest.mark.asyncio
@pytest.mark.parametrize('ids', [['finding1'], ['finding1', 'unknown'], ['finding1', 'finding1']])
async def test_group_cannot_omit_invent_or_duplicate_finding_ids(review_case, ids):
    issues = review_case.report['files'][0]['issues']
    issues.append({**issues[0], 'id': 'finding2'})
    output = {'findings': [{**TRIAGE, 'finding_id': identifier} for identifier in ids]}
    result, _ = await review_case.run([output])
    assert result['status'] == 'failed' and not result['triage'] and not result['proposals']
    assert result['errors'][0]['code'] in {'invalid_output', 'invalid_context'}


@pytest.mark.asyncio
async def test_group_separate_verdicts_and_shared_context(review_case):
    issues = review_case.report['files'][0]['issues']
    issues.append({**issues[0], 'id': 'finding2'})
    group = {'findings': [{**TRIAGE, 'finding_id': 'finding1'},
              {**TRIAGE, 'finding_id': 'finding2', 'disposition': 'false_positive'}]}
    result, provider = await review_case.run([group, AUTHOR, APPROVE])
    assert len(provider.calls) == 3
    assert len(result['triage']) == 2 and len(result['proposals']) == 1
    assert [entry['disposition'] for entry in result['triage']] == ['confirmed', 'false_positive']


def test_equivalence_requires_known_rules_and_overlapping_spans():
    findings = [dict(id='a', file='x.py', line=1, end_line=2, tool='bandit', rule_id='B602'),
                dict(id='b', file='x.py', line=2, end_line=3, tool='semgrep', rule_id='codeagent.python.security.v1'),
                dict(id='c', file='x.py', line=5, tool='semgrep', rule_id='codeagent.python.security.v1')]
    groups, _ = _finding_groups(findings)
    assert groups[0]['equivalent_occurrences'] == [['a', 'b']]
    assert groups[0]['basis'] == 'shared_context_only'


def test_identifier_index_is_cached_but_source_mutation_invalidates_it(tmp_path):
    (tmp_path / 'app.py').write_text('def callback():\n    return read_config()\n')
    first, second = SourceContext(str(tmp_path)), SourceContext(str(tmp_path))
    assert first.identifier_index() is second.identifier_index()
    (tmp_path / 'app.py').write_text('def changed():\n    return 123\n')
    third = SourceContext(str(tmp_path))
    assert 'changed' in third.identifier_index()['identifiers']
    assert third.identifier_index() is not first.identifier_index() or 'changed' in first.identifier_index()['identifiers']


@pytest.mark.asyncio
async def test_conflicts_and_combined_diff_require_explicit_compatible_validated_selection(review_case):
    result, _ = await review_case.run([TRIAGE, AUTHOR, APPROVE])
    proposal = result['proposals'][0]
    context = SourceContext(str(review_case.path))
    assert combined_diff(context, [proposal], [proposal['id']]) == proposal['diff']
    with pytest.raises(ContextError, match='Select distinct'):
        combined_diff(context, [proposal], [])
    duplicate = {**copy.deepcopy(proposal), 'id': 'other'}
    assert proposal_conflicts([proposal, duplicate])[0]['files'] == ['app.py']
    with pytest.raises(ContextError, match='conflicting'):
        combined_diff(context, [proposal, duplicate], [proposal['id'], 'other'])
    proposal['validation']['status'] = 'incomplete'
    with pytest.raises(ContextError, match='statically validated'):
        combined_diff(context, [proposal], [proposal['id']])


@pytest.mark.asyncio
async def test_profile_or_snapshot_identity_changes_invalidate_paid_checkpoints(review_case):
    await review_case.run([TRIAGE, AUTHOR, APPROVE], rule_profile='security-v1', _snapshot_digest='old')
    _, provider = await review_case.run([TRIAGE, AUTHOR, APPROVE], rule_profile='security-v2', _snapshot_digest='old')
    assert len(provider.calls) == 3
    _, provider = await review_case.run([TRIAGE, AUTHOR, APPROVE], rule_profile='security-v2', _snapshot_digest='new')
    assert len(provider.calls) == 3

@pytest.mark.asyncio
async def test_validation_from_changed_rule_profile_cannot_be_approved(review_case):
    review_case.report['profile_digests'] = {'source': 'original-profile', 'dependency': 'old-advisories'}
    async def validate(payload, *, is_cancelled):
        return {'status': 'passed', 'syntax': {'status': 'passed'},
                'coverage_after': [{'tool': 'semgrep', 'status': 'completed'}],
                'profile_digests': {'source': 'changed-profile', 'dependency': 'old-advisories'}}
    result, _ = await review_case.run([TRIAGE, AUTHOR, APPROVE], _validator=validate)
    assert result['proposals'][0]['validation']['status'] == 'incomplete'
    assert 'differs from the scanned report' in result['proposals'][0]['validation']['errors'][0]
    assert result['proposals'][0]['status'] == 'unresolved'


@pytest.mark.asyncio
async def test_source_only_validation_is_not_invalidated_by_new_advisories(review_case):
    review_case.report['profile_digests'] = {'source': 'source-profile', 'dependency': 'old-advisories'}
    async def validate(payload, *, is_cancelled):
        return {'status': 'passed', 'syntax': {'status': 'passed'},
                'coverage_after': [{'tool': 'semgrep', 'status': 'completed'}],
                'profile_digests': {'source': 'source-profile', 'dependency': 'new-advisories'}}
    result, _ = await review_case.run([TRIAGE, AUTHOR, APPROVE], _validator=validate)
    assert result['proposals'][0]['status'] == 'reviewed'


@pytest.mark.asyncio
async def test_validation_cancellation_never_reaches_reviewer(review_case):
    async def validate(payload, *, is_cancelled):
        raise ReviewCancelled('Canceled by operator')
    with pytest.raises(ReviewCancelled):
        await review_case.run([TRIAGE, AUTHOR], _validator=validate)
    assert review_case.steps['finding:finding1:validator:0']['status'] == 'cancelled'

@pytest.mark.asyncio
async def test_private_pinned_model_digest_fences_cached_roles(review_case):
    await review_case.run([TRIAGE, AUTHOR, APPROVE], _model_digest='old-digest')
    _, provider = await review_case.run([TRIAGE, AUTHOR, APPROVE], _model_digest='new-digest')
    assert len(provider.calls) == 3


@pytest.mark.asyncio
async def test_ollama_changed_digest_stops_before_any_model_request():
    import httpx
    from integration.providers import OllamaProvider
    from integration.models import AnalystOutput, ProviderError
    paths = []
    async def handle(request):
        paths.append(request.url.path)
        return httpx.Response(200, json={'models': [{'name': 'unit-model', 'digest': 'changed'}]})
    provider = OllamaProvider({'model': 'unit-model', '_model_digest': 'pinned'})
    await provider.client.aclose()
    provider.client = httpx.AsyncClient(transport=httpx.MockTransport(handle))
    try:
        with pytest.raises(ProviderError, match='changed since submission') as caught:
            await provider.generate([], AnalystOutput, max_output_tokens=100, timeout_sec=2)
        assert caught.value.usage['model_calls'] == 0 and not caught.value.uncertain
        assert paths == ['/api/tags']
    finally:
        await provider.aclose()
