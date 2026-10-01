"""Synthetic records test authoring infrastructure, never corpus behavior."""
import copy
import hashlib
import io
import json
import uuid
import zipfile

import pytest

from evaluation import candidate_corpus as candidate
from evaluation import static_validation as validation
from evaluation.corpus_review import source_digest


def fixture():
    cases = []
    extensions = {'python':'py','javascript':'js','typescript':'ts','java':'java','go':'go','c':'c','cpp':'cpp',
                  'ruby':'rb','php':'php','scala':'scala','kotlin':'kt','swift':'swift','csharp':'cs',
                  'visualbasic':'vb','fsharp':'fs','rust':'rs','bash':'sh'}
    for language in sorted(candidate.LANGUAGES):
        for vulnerable in (False, True):
            for index in range(1, 7):
                identity = f"v2-{language}-{'vulnerable' if vulnerable else 'safe'}-{index:02d}"
                files = {"app.py": f"# Synthetic transport fixture {identity}\nvalue = {index}\n"}
                if language != 'python':
                    files['declared.'+extensions[language]] = f'Synthetic transport fixture {identity}\n'
                cases.append({"id": identity, "language": language, "vulnerable": vulnerable,
                    "scenario": identity, "files": files, "content_sha256": source_digest(files),
                    "expected_findings": [{"path": "app.py", "family": "unit", "cwe": "CWE-999"}] if vulnerable else [],
                    "rationale": "Synthetic infrastructure test, not a security label.",
                    "remediation_constraints": ["No real remediation scored."],
                    "runtime_assumptions": {"runtime": "synthetic"},
                    "operation_contract": {"purpose": "test", "trust_boundary": "test",
                       "legitimate_examples": [{"input": "test", "expected": "test"}],
                       "permitted_changes": [], "forbidden_changes": ["source execution"]},
                    "regression_traps": ["test"], "ground_truth_scope": {"profile": "security-v2"},
                    "derivation": {"group": "synthetic-test-only", "origin": "test fixture", "related_case_ids": [],
                                   "independence_rationale": "not independent; used only for infrastructure unit tests"},
                    "provenance": {"origin": "synthetic unit test"}, "split": "held_out",
                    "human_review": {"status": "pending", "reviewer": None, "notes": None}})
    return {"version": "synthetic-only", "schema_version": "2.0", "cases": cases}


def capabilities():
    return {"profile_digests": {"security-v2": {"source": "unit-source", "dependency": "unit-db"}},
            "analyzers": [{"id": tool, "version": "unit", "available": True} for tool in sorted(validation.TOOLS)]}


def report_for(case, job_id):
    paths = {tool: [] for tool in validation.TOOLS}
    for name in case['files']:
        language = validation.language_for(validation.Path(name))
        if language:
            paths['dotnet' if language in validation.DOTNET_LANGUAGES else 'semgrep'].append(name)
        if language == 'python': paths['bandit'].append(name)
    return {"job_id": job_id, "status": "completed", "profile_digests": {
            "source": "unit-source", "dependency": "unit-db", "source_details": {"extra": "retained"}},
            "meta": {"snapshot": {"id": "unit-snapshot", "digest": "unit-digest",
                     "files": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in case['files'].items()}},
                     "tool_runs": []},
            "files": [], "coverage": [{"tool": tool, "status": "completed" if paths[tool] else "skipped",
              "errors": [], "path_outcomes": [{"path": path, "status": "completed"} for path in paths[tool]]}
              for tool in sorted(validation.TOOLS)]}


def assess_case(case, report=None):
    job_id = str(uuid.uuid4())
    report = report or report_for(case, job_id)
    return validation.assess(case, report,
          {"job_id": report["job_id"], "status": "completed", "config": {"mode": "static"}},
          validation.environment(capabilities(), "security-v2"))


def test_complete_candidate_has_explicit_contracts_but_no_approval():
    corpus = fixture()
    assert len(candidate.validate_candidate(corpus)) == 204
    assert candidate.audit(corpus)["independence_status"] == "pending_human_review"


@pytest.mark.parametrize('name', ['../escape.py','/escape.py','C:/escape.py','a\\escape.py','a/./file.py','a//file.py',''])
def test_candidate_path_boundaries(name):
    corpus = fixture(); case = corpus['cases'][0]
    case['files'] = {name: 'source'}; case['content_sha256'] = source_digest(case['files'])
    with pytest.raises(ValueError, match='path'):
        candidate.validate_candidate(corpus)


@pytest.mark.parametrize('field', ['rationale','runtime_assumptions','operation_contract','regression_traps','derivation','provenance'])
def test_missing_review_contract_is_rejected(field):
    corpus = fixture(); del corpus['cases'][0][field]
    with pytest.raises(ValueError): candidate.validate_candidate(corpus)


def test_duplicate_source_and_wrong_finding_anchor_are_rejected():
    corpus = fixture()
    corpus['cases'][1]['files'] = copy.deepcopy(corpus['cases'][0]['files'])
    corpus['cases'][1]['content_sha256'] = corpus['cases'][0]['content_sha256']
    with pytest.raises(ValueError, match='duplicate'): candidate.validate_candidate(corpus)
    corpus = fixture(); case = next(c for c in corpus['cases'] if c['vulnerable'])
    case['expected_findings'][0]['line_start'] = 1000
    with pytest.raises(ValueError, match='line'): candidate.validate_candidate(corpus)


def test_declared_language_requires_matching_source():
    corpus = fixture(); case = corpus['cases'][0]
    case['files'] = {'app.py': 'x = 1\n'}
    case['content_sha256'] = source_digest(case['files'])
    with pytest.raises(ValueError, match='declared language'):
        candidate.validate_candidate(corpus)


def test_file_cannot_also_be_a_source_directory():
    corpus = fixture(); case = corpus['cases'][0]
    case['files']['directory'] = 'collision'
    case['files']['directory/child.txt'] = 'child'
    case['content_sha256'] = source_digest(case['files'])
    with pytest.raises(ValueError, match='collision'): candidate.validate_candidate(corpus)


def test_generated_candidate_refuses_to_overwrite_human_review_notes(tmp_path):
    corpus = fixture()
    candidate.write_artifacts(corpus, tmp_path)
    packet_path = tmp_path / 'unsigned-review-manifest.json'
    packet = json.loads(packet_path.read_text())
    packet['cases'][0]['human_review']['notes'] = 'Human work in progress'
    packet_path.write_text(json.dumps(packet)); old = packet_path.read_bytes()
    with pytest.raises(ValueError, match='human review work'):
        candidate.write_artifacts(corpus, tmp_path)
    assert packet_path.read_bytes() == old


def test_readable_review_preserves_future_semantic_fields_and_history():
    corpus = fixture()
    case = corpus['cases'][0]
    case['future_semantics'] = {'important': 'Inspect this requirement'}
    case['authoring_history'] = {'retired_draft': 'Retain this provenance'}
    sheet = candidate.artifacts(corpus)[f"review/{case['language']}.md"]
    assert 'Inspect this requirement' in sheet and 'Retain this provenance' in sheet
    assert '../unsigned-review-manifest.json' in sheet


def test_review_notes_in_markdown_are_not_overwritten(tmp_path):
    corpus = fixture(); candidate.write_artifacts(corpus, tmp_path)
    sheet = tmp_path / 'review/python.md'
    sheet.write_text(sheet.read_text() + '\nHuman review in progress\n')
    with pytest.raises(ValueError, match='Modified generated artifact'):
        candidate.write_artifacts(corpus, tmp_path)
    assert sheet.read_text().endswith('Human review in progress\n')


def test_source_backticks_cannot_break_out_of_review_fence():
    corpus = fixture(); case = corpus['cases'][0]
    case['files']['app.py'] = 'value = """\n```\ntext\n"""\n'
    case['content_sha256'] = source_digest(case['files'])
    sheet = candidate.artifacts(corpus)[f"review/{case['language']}.md"]
    assert '````'+case['language'] in sheet


def test_simultaneous_collectors_cannot_submit_duplicate_jobs(tmp_path):
    api = FakeAPI(fixture())
    with validation.evidence_lock(tmp_path):
        with pytest.raises(ValueError, match='Another static-evidence collector'):
            validation.run_validation(fixture(), tmp_path, api, limit_cases=1)
    assert not api.calls


def test_operational_completion_is_separate_from_proposed_label_agreement():
    corpus = fixture(); positive = next(c for c in corpus['cases'] if c['vulnerable'])
    result = assess_case(positive)
    assert result['operational_status'] == result['parser_status'] == 'completed'
    assert result['label_observation'] == 'expected_not_observed'
    assert result['human_review_required'] and not result['runtime_tested']


@pytest.mark.parametrize('mutation', ['parse','skip','missing_tool','profile','snapshot','finding_hash','ai'])
def test_incomplete_or_incompatible_evidence_never_passes(mutation):
    case = fixture()['cases'][0]; report = report_for(case, str(uuid.uuid4()))
    if mutation == 'parse': report['coverage'][-1]['errors'] = ['Parser failed']
    if mutation == 'skip':
        for entry in report['coverage']: entry['path_outcomes'] = []
    if mutation == 'missing_tool': report['coverage'].pop()
    if mutation == 'profile': report['profile_digests']['source'] = 'changed'
    if mutation == 'snapshot': report['meta']['snapshot']['files'] = {}
    if mutation == 'finding_hash': report['files'] = [{'path': 'app.py','issues':[{'id':'wrong','source_hash':'wrong'}]}]
    if mutation == 'ai': report['ai_analysis'] = {'provider': 'unexpected'}
    assert assess_case(case, report)['operational_status'] == 'incomplete'


def test_safe_extra_findings_are_observations_not_automatic_false_positives():
    case = fixture()['cases'][0]; report = report_for(case, str(uuid.uuid4()))
    report['files'] = [{'path':'app.py','issues':[{'id':'extra','family':'other','line':2,
      'source_hash':report['meta']['snapshot']['files']['app.py']}]}]
    result = assess_case(case,report)
    assert result['operational_status'] == 'completed'
    assert result['label_observation'] == 'unexpected_findings' and result['unexpected_finding_ids'] == ['extra']
    assert 'false_positives' not in result


def test_unknown_finding_path_without_hash_is_incompatible():
    case = fixture()['cases'][0]; report = report_for(case, str(uuid.uuid4()))
    report['files'] = [{'path':'absent.py','issues':[{'id':'unknown'}]}]
    assert assess_case(case, report)['operational_status'] == 'incomplete'


def test_skipped_bandit_for_python_is_incomplete_even_when_semgrep_passes():
    case = fixture()['cases'][0]; report = report_for(case, str(uuid.uuid4()))
    next(entry for entry in report['coverage'] if entry['tool'] == 'bandit')['status'] = 'skipped'
    assert assess_case(case, report)['operational_status'] == 'incomplete'


def test_bandit_must_account_for_each_python_file():
    case = fixture()['cases'][0]; report = report_for(case, str(uuid.uuid4()))
    next(entry for entry in report['coverage'] if entry['tool'] == 'bandit')['path_outcomes'] = []
    assert assess_case(case, report)['operational_status'] == 'incomplete'


class FakeAPI:
    def __init__(self, corpus, fail_submit=False, interrupt=False):
        self.corpus=corpus; self.fail_submit=fail_submit; self.interrupt=interrupt
        self.jobs={}; self.submitted=0; self.canceled=[]; self.calls=[]

    def request(self, method, path, **kwargs):
        self.calls.append((method,path))
        assert '/enhance' not in path and '/config/ai' not in path
        if path=='/capabilities': return capabilities()
        if path=='/projects': return {'id':str(uuid.uuid4())}
        if path=='/analyze':
            self.submitted+=1
            assert kwargs['data']['mode']=='static'
            if self.fail_submit: raise TimeoutError('Uncertain request')
            filename, data, mime=kwargs['files']['file']
            case=next(c for c in self.corpus['cases'] if c['id']+'.zip'==filename)
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                assert {p:archive.read(p).decode() for p in archive.namelist()}==case['files']
            job_id=str(uuid.uuid4());self.jobs[job_id]=case
            return {'job_id':job_id,'status':'queued'}
        job_id=path.split('/')[-1]
        if method=='DELETE': self.canceled.append(job_id);return {'status':'canceled'}
        if path.startswith('/jobs/'):
            if self.interrupt: self.interrupt=False;raise KeyboardInterrupt()
            return {'job_id':job_id,'status':'completed','config':{'mode':'static'},'source':{}}
        if path.startswith('/reports/'):return report_for(self.jobs[job_id],job_id)
        pytest.fail('Unexpected API request '+path)


def test_static_collection_resumes_jobs_and_reuses_exact_artifacts(tmp_path):
    corpus=fixture();api=FakeAPI(corpus)
    state=validation.run_validation(corpus,tmp_path,api,limit_cases=2,poll_seconds=0,progress=lambda _:None)
    assert api.submitted==2 and len(state['records'])==2
    assert not validation.summary(state)['collection_complete']
    validation.run_validation(corpus,tmp_path,api,limit_cases=2,poll_seconds=0,progress=lambda _:None)
    assert api.submitted==2
    record=next(iter(state['records'].values()))
    (tmp_path/record['report_artifact']).write_text('{}')
    with pytest.raises(ValueError,match='evidence'):
        validation.run_validation(corpus,tmp_path,api,limit_cases=2,poll_seconds=0)
    assert api.submitted==2


def test_uncertain_submission_is_not_automatically_duplicated(tmp_path):
    corpus=fixture();api=FakeAPI(corpus,fail_submit=True)
    with pytest.raises(TimeoutError):validation.run_validation(corpus,tmp_path,api,limit_cases=1)
    with pytest.raises(ValueError,match='uncertain'):
        validation.run_validation(corpus,tmp_path,api,limit_cases=1)
    assert api.submitted==1


def test_cancel_signals_only_active_static_jobs(tmp_path):
    corpus=fixture();api=FakeAPI(corpus,interrupt=True)
    with pytest.raises(KeyboardInterrupt):validation.run_validation(corpus,tmp_path,api,limit_cases=2)
    assert len(api.canceled)==2 and set(api.canceled)==set(api.jobs)
    state=json.loads((tmp_path/'state.json').read_text())
    assert all(r['status']=='cancel_requested' for r in state['records'].values())


def test_metadata_change_invalidates_checkpoint_before_new_submission(tmp_path):
    corpus=fixture();api=FakeAPI(corpus)
    validation.run_validation(corpus,tmp_path,api,limit_cases=1,poll_seconds=0,progress=lambda _:None)
    corpus['cases'][0]['rationale']+=' semantic change'
    with pytest.raises(ValueError,match='changed'):
        validation.run_validation(corpus,tmp_path,api,limit_cases=1)
    assert api.submitted==1


def test_implementation_change_invalidates_saved_assessments(tmp_path, monkeypatch):
    corpus=fixture(); api=FakeAPI(corpus)
    validation.run_validation(corpus,tmp_path,api,limit_cases=1,poll_seconds=0,progress=lambda _:None)
    monkeypatch.setattr(validation, 'implementation_digest', lambda: 'changed-implementation')
    with pytest.raises(ValueError,match='changed'):
        validation.run_validation(corpus,tmp_path,api,limit_cases=1)
    assert api.submitted==1


def test_invalid_input_rejected_without_any_api_request(tmp_path):
    corpus=fixture();api=FakeAPI(corpus);corpus['cases'][0]['files']={'../escape':'bad'}
    with pytest.raises(ValueError):validation.run_validation(corpus,tmp_path,api)
    assert not api.calls
