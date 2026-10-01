"""Synthetic metric and mocked transport fixtures; never benchmark observations."""
import copy
import json
from pathlib import Path

import pytest

from integration.workflow import WORKFLOW_VERSION, implementation_digest
from evaluation.corpus_review import REVIEW_SCHEMA_VERSION, case_review_digest
from evaluation.benchmark import (validate_corpus, freeze, verify_freeze, observe, score,
    digest, blind_sheets, merge_human_scores, run, make_zip)

CORPUS = Path(__file__).parents[1] / 'evaluation/corpus-v1/corpus.json'


def approved_fixture():
    corpus = json.loads(CORPUS.read_text())
    for case in corpus['cases']:
        case['human_review'] = {'status': 'approved', 'reviewer': 'synthetic-unit-test-reviewer',
             'reviewer_kind': 'human', 'review_schema_version': REVIEW_SCHEMA_VERSION,
             'reviewed_at': '2000-01-01T00:00:00+00:00', 'reviewed_content_sha256': case['content_sha256'],
             'reviewed_case_sha256': case_review_digest(corpus, case)}
    return corpus


def capabilities():
    return {'workflow': {'version': WORKFLOW_VERSION, 'implementation_hash': implementation_digest()}, 'providers': {'ollama': {'available': True, 'model_digests': {'unit-model': 'sha256:unit'}}},
            'analyzers': [{'id': 'unit-scanner', 'version': '1.0', 'available': True}],
            'profile_digests': {'security-v2': {'source': 'unit-source', 'dependency': 'unit-db'}}}


def frozen_fixture(corpus):
    return freeze(corpus, {'provider': 'ollama', 'model': 'unit-model'}, capabilities())


def metric_fixture(corpus, frozen):
    """Explicitly mocked records isolate the mathematical gate, not real quality."""
    records, reviews = [], {}
    for case in corpus['cases']:
        for mode in ('static', 'single_agent', 'multi_agent'):
            for repetition in range(3):
                row = {'case_id': case['id'], 'mode': mode, 'repetition': repetition, 'finished_at': 'unit-time',
                       'positive': case['vulnerable'] or mode != 'multi_agent', 'matched_finding_ids': ['finding'] if case['vulnerable'] else [],
                       'status': 'completed', 'incomplete': False, 'latency_ms': 10, 'tokens': 20, 'usage_complete': True,
                       'proposals': []}
                if case['vulnerable'] and mode == 'multi_agent':
                    proposal = {'id': 'proposal', 'finding_ids': ['finding'], 'status': 'reviewed', 'validation': {'status': 'passed'}}
                    row['proposals'].append(proposal)
                    reviews[(case['id'], mode, repetition, 'proposal')] = {'decision': 'accepted', 'proposal_hash': digest(proposal)}
                records.append(row)
    return {'origin': 'recorded', 'freeze_hash': frozen['freeze_hash'], 'corpus_hash': digest(corpus), 'records': records}, reviews


def test_authored_corpus_is_complete_distinct_and_unapproved():
    corpus = json.loads(CORPUS.read_text())
    assert len(validate_corpus(corpus, require_approved=False)) == 204
    assert len({case['content_sha256'] for case in corpus['cases']}) == 204
    assert all(case['human_review']['status'] == 'pending' for case in corpus['cases'])
    assert any(len(case['files']) > 1 for case in corpus['cases'])
    with pytest.raises(ValueError, match='independent human approval'):
        freeze(corpus, {'model': 'unit-model'}, capabilities())


def test_corpus_wide_concerns_require_human_resolution_then_fresh_case_approval():
    corpus = approved_fixture()
    corpus['review_concerns'] = [{'id':'synthetic-only', 'status':'pending_independent_human_review'}]
    with pytest.raises(ValueError, match='Corpus-wide'):
        validate_corpus(corpus)
    corpus['review_concerns'][0].update(status='resolved', reviewer_kind='human',
        reviewer='synthetic-unit-test-reviewer', reviewed_at='2000-01-01', resolution='Synthetic test only')
    with pytest.raises(ValueError, match='specification'):
        validate_corpus(corpus)
    for case in corpus['cases']:
        case['human_review']['reviewed_case_sha256'] = case_review_digest(corpus, case)
    assert len(validate_corpus(corpus)) == 204


@pytest.mark.parametrize('mutation', ['source', 'duplicate', 'language', 'label', 'approval_hash', 'held_out'])
def test_corpus_fails_closed_on_changed_or_invalid_cases(mutation):
    corpus = approved_fixture()
    case = corpus['cases'][0]
    if mutation == 'source': case['files']['app.py'] += '# changed\n'
    if mutation == 'duplicate': corpus['cases'][1] = copy.deepcopy(case)
    if mutation == 'language': case['language'] = 'invented'
    if mutation == 'label': case['vulnerable'] = False
    if mutation == 'approval_hash': case['human_review']['reviewed_content_sha256'] = 'wrong'
    if mutation == 'held_out': case['split'] = 'training'
    with pytest.raises(ValueError): validate_corpus(corpus)


def test_freeze_and_resume_pin_model_rules_prompts_corpus_and_config():
    corpus = approved_fixture()
    frozen = frozen_fixture(corpus)
    verify_freeze(corpus, frozen, capabilities())
    changed = copy.deepcopy(capabilities())
    changed['providers']['ollama']['model_digests']['unit-model'] = 'changed'
    with pytest.raises(ValueError, match='changed since freeze'): verify_freeze(corpus, frozen, changed)
    changed = copy.deepcopy(capabilities())
    changed['profile_digests']['security-v2']['source'] = 'changed'
    with pytest.raises(ValueError, match='changed since freeze'): verify_freeze(corpus, frozen, changed)
    frozen['config']['max_model_calls'] = 999
    with pytest.raises(ValueError, match='changed'): verify_freeze(corpus, frozen, capabilities())


def test_cloud_needs_explicit_permission_and_dated_snapshot():
    corpus = approved_fixture()
    cloud = capabilities()
    cloud['providers']['openai'] = {'available': True}
    config = {'provider': 'openai', 'model': 'unit-model'}
    with pytest.raises(ValueError, match='allow-cloud'): freeze(corpus, config, cloud)
    with pytest.raises(ValueError, match='dated model snapshot'): freeze(corpus, config, cloud, allow_cloud=True)
    frozen = freeze(corpus, {**config, 'model': 'unit-model-2026-01-01'}, cloud, allow_cloud=True)
    with pytest.raises(ValueError, match='allow-cloud'): verify_freeze(corpus, frozen, cloud)


def test_abstention_missing_output_and_unrelated_findings_do_not_improve_scores():
    case = approved_fixture()['cases'][0]
    report = {'files': [{'path': 'app.py', 'issues': [{'id': 'expected', 'cwe': 'CWE-89'}, {'id': 'unrelated', 'cwe': 'CWE-999'}]}],
              'coverage': [{'status': 'completed'}], 'ai_analysis': {'triage': [{'finding_id': 'expected', 'disposition': 'needs_context'}]}}
    observed = observe(case, 'multi_agent', report, 'interrupted', 10)
    assert observed['positive'] and observed['matched_finding_ids'] == ['expected'] and observed['incomplete']
    report['ai_analysis']['triage'][0].update(disposition='false_positive', evidence=[])
    assert observe(case, 'multi_agent', report, 'completed', 1)['positive']
    report['ai_analysis']['triage'][0]['evidence'] = [{'line_start': 1}]
    result = observe(case, 'multi_agent', report, 'completed', 1)
    assert not result['positive'] and result['retained_finding_ids'] == ['unrelated']


def test_metric_gate_requires_both_improvements_and_non_decreased_recall():
    corpus = approved_fixture(); frozen = frozen_fixture(corpus)
    observations, reviews = metric_fixture(corpus, frozen)
    result = score(corpus, frozen, observations, reviews, bootstrap_samples=40)
    assert result['release_status'] == 'quality_gate_passed'
    assert result['accepted_fix_improvement_percentage_points'] == 100
    assert result['false_positive_relative_reduction'] == 1
    assert result['paired_95_percent_intervals']['fix_difference'] == [1, 1]
    # Correct fixes cannot compensate for lower recall.
    observations['records'][6]['positive'] = False
    result = score(corpus, frozen, observations, reviews, bootstrap_samples=40)
    assert result['release_status'] == 'candidate' and 'Vulnerability recall decreased' in result['gate_reasons']


def test_zero_baseline_false_positives_are_inconclusive_and_synthetic_origin_is_rejected():
    corpus = approved_fixture(); frozen = frozen_fixture(corpus)
    observations, reviews = metric_fixture(corpus, frozen)
    safe = {case['id'] for case in corpus['cases'] if not case['vulnerable']}
    for row in observations['records']:
        if row['case_id'] in safe: row['positive'] = False
    result = score(corpus, frozen, observations, reviews, bootstrap_samples=40)
    assert result['release_status'] == 'candidate' and result['false_positive_relative_reduction'] is None
    assert any('inconclusive' in reason for reason in result['gate_reasons'])
    observations['origin'] = 'synthetic'
    with pytest.raises(ValueError, match='Only recorded'): score(corpus, frozen, observations, reviews)


def test_missing_results_or_human_reviews_cannot_pass():
    corpus = approved_fixture(); frozen = frozen_fixture(corpus)
    observations, reviews = metric_fixture(corpus, frozen)
    with pytest.raises(ValueError, match='human review'): score(corpus, frozen, observations, {})
    observations['records'].pop()
    with pytest.raises(ValueError, match='three observations'): score(corpus, frozen, observations, reviews)


def test_unrelated_or_unvalidated_proposal_is_unsuccessful():
    corpus = approved_fixture(); frozen = frozen_fixture(corpus)
    observations, reviews = metric_fixture(corpus, frozen)
    for row in observations['records']:
        for proposal in row['proposals']:
            proposal['finding_ids'] = ['unrelated']
            reviews[(row['case_id'], row['mode'], row['repetition'], proposal['id'])]['proposal_hash'] = digest(proposal)
    result = score(corpus, frozen, observations, reviews, bootstrap_samples=40)
    assert result['accepted_fix_improvement_percentage_points'] == 0 and result['release_status'] == 'candidate'


def test_blinded_review_sheets_omit_mode_model_and_require_complete_matching_decisions(tmp_path):
    corpus = approved_fixture(); frozen = frozen_fixture(corpus)
    observations, _ = metric_fixture(corpus, frozen)
    assert blind_sheets(corpus, observations, tmp_path) == 306
    sheets = json.loads((tmp_path / 'blinded-review-sheets.json').read_text())
    mapping = json.loads((tmp_path / 'private-review-map.json').read_text())
    assert all('mode' not in sheet and 'model' not in sheet for sheet in sheets['items'])
    with pytest.raises(ValueError, match='independent recorded human'): merge_human_scores(observations, mapping, sheets)
    for sheet in sheets['items']:
        sheet.update(decision='accepted', reviewer='unit-test human fixture', reviewed_at='unit-time', reason='unit-test metric fixture')
    assert len(merge_human_scores(observations, mapping, sheets)) == 306
    sheets['items'].pop()
    with pytest.raises(ValueError, match='missing'): merge_human_scores(observations, mapping, sheets)


def test_collection_resumes_job_ids_and_reuses_one_exact_static_report(tmp_path):
    corpus = approved_fixture(); frozen = frozen_fixture(corpus)
    class FakeAPI:
        submitted = 0
        scan_submitted = 0
        def request(self, method, path, **kwargs):
            if path == '/capabilities': return capabilities()
            if path == '/projects': return {'id': 'project'}
            if path == '/analyze':
                self.scan_submitted += 1
                assert kwargs['data']['profile'] == 'security-v2'
                return {'job_id': 'scan'}
            if path.endswith('/enhance'):
                self.submitted += 1
                assert kwargs['json']['workflow_mode'] in {'single_agent', 'multi_agent'}
                return {'job_id': f'review{self.submitted}'}
            return {'files': [], 'coverage': [{'status': 'completed'}], 'profile_digests': {'source': 'unit-source', 'dependency': 'unit-db'}}
        def wait(self, job_id):
            return {'status': 'completed', 'started_at': '2020-01-01T00:00:00+00:00', 'finished_at': '2020-01-01T00:00:01+00:00'}
    api = FakeAPI()
    state = run(corpus, frozen, tmp_path, api, limit_cases=1)
    assert api.submitted == 6 and api.scan_submitted == 1 and len(state['records']) == 9
    assert len({r['input_report_hash'] for r in state['records']}) == 1
    assert not state['collection_complete']
    resumed = run(corpus, frozen, tmp_path, api, limit_cases=1)
    assert api.submitted == 6 and api.scan_submitted == 1
    assert resumed['records'] == state['records']
    assert make_zip(corpus['cases'][0]) == make_zip(corpus['cases'][0])


def test_missing_review_artifact_recovers_known_step_costs_without_inventing_proposals():
    from evaluation.benchmark import checkpoint_analysis
    job = {'status': 'canceled', 'error': 'Canceled by user', 'steps': [
        {'role': 'analyst', 'status': 'completed', 'provider': 'ollama', 'model': 'actual-model',
         'usage': {'model_calls': 2, 'input_tokens': 20, 'output_tokens': 10, 'total_tokens': 30,
                   'accounted_tokens': 30, 'usage_complete': True}},
        {'role': 'author', 'status': 'completed', 'output': {'edits': ['not an anchored proposal']},
         'usage': {'model_calls': 1, 'input_tokens': 30, 'output_tokens': 20, 'total_tokens': 50}},
        {'role': 'validator', 'status': 'completed', 'usage': {'total_tokens': 9999}},
        {'role': 'reviewer', 'status': 'cancelled', 'reserved_tokens': 400, 'usage': {}}]}
    analysis = checkpoint_analysis(job, {'provider': 'ollama', 'model': 'alias'})
    assert analysis['usage']['total_tokens'] == 80
    assert analysis['usage']['model_calls'] == 4
    assert analysis['usage']['accounted_tokens'] == 480
    assert not analysis['usage']['usage_complete']
    assert analysis['proposals'] == [] and analysis['triage'] == []
    assert analysis['model'] == 'actual-model'
    # Incomplete review evidence still retains static findings for scoring.
    case = approved_fixture()['cases'][0]
    report = {'files': [{'path': 'app.py', 'issues': [{'id': 'original', 'cwe': 'CWE-89'}]}],
              'coverage': [{'status': 'completed'}], 'ai_analysis': analysis}
    observed = observe(case, 'multi_agent', report, job['status'], 10)
    assert observed['positive'] and observed['incomplete'] and observed['tokens'] == 80
    assert observe(case, 'multi_agent', report, 'completed', 10)['incomplete']


def test_known_zero_dispatch_and_failed_schema_usage_remain_accurate():
    from evaluation.benchmark import checkpoint_analysis
    job = {'status': 'failed', 'steps': [
        {'role': 'analyst', 'status': 'failed', 'usage': {'model_calls': 0, 'input_tokens': 0,
         'output_tokens': 0, 'total_tokens': 0, 'usage_complete': True}},
        {'role': 'author', 'status': 'failed', 'usage': {'model_calls': 1, 'input_tokens': 7,
         'output_tokens': 3, 'total_tokens': 10, 'usage_complete': True}}]}
    result = checkpoint_analysis(job, {'provider': 'ollama', 'model': 'test'})
    assert result['usage']['model_calls'] == 1 and result['usage']['total_tokens'] == 10
    assert result['usage']['usage_complete']
