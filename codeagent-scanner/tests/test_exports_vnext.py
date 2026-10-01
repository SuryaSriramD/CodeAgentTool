"""Saved-report export boundaries, shared by the browser and API-client CLI."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path

import pytest
from jsonschema.validators import validator_for

from pipeline.exports import combined_diff, sarif, serialize


@pytest.fixture
def saved_report():
    finding = {'id': 'occurrence-1', 'logical_id': 'logical-1', 'fingerprint': 'v1:fingerprint',
        'tool': 'semgrep', 'rule_id': 'sql-injection', 'file': 'src/query file.py', 'line': 2, 'end_line': 4,
        'type': 'SQL injection', 'message': 'User input reaches a query', 'severity': 'high', 'cwe': ['CWE-89'],
        'analysis_kind': 'taint', 'snippet': 'SENSITIVE_SOURCE_SNIPPET'}
    proposal = {'id': 'proposal-1', 'finding_ids': ['occurrence-1'], 'status': 'reviewed',
        'review': {'decision': 'approve', 'comments': ['Use the bound parameter API']},
        'validation': {'status': 'passed', 'targeted_findings_remaining': [], 'new_findings': []},
        'explanation': 'Bind values separately from SQL', 'diff': '--- a/src/query.py\n+++ b/src/query.py\n-query(user)\n+query("?", user)\n',
        'edits': [], 'applied': False, 'runtime_tested': False}
    return {'schema_version': '2.0', 'job_id': 'scan-1', 'review_run_id': 'review-1', 'report_hash': 'a' * 64,
        'project_id': 'project-1', 'stream': 'main', 'status': 'partial',
        'profiles': {'name': 'security-v2'}, 'summary': {'critical': 0, 'high': 1, 'medium': 0, 'low': 0},
        'meta': {'generated_at': '2026-09-25T00:00:00Z', 'repo': {'source': 'github', 'commit': 'f' * 40},
                 'snapshot': {'digest': 'snapshot-digest', 'warnings': ['Submodule source excluded']}},
        'files': [{'path': finding['file'], 'issues': [finding]}],
        'coverage': [{'tool': 'semgrep', 'status': 'partial', 'version': '1.178.0', 'files_scanned': 1,
                      'files_discovered': 2, 'errors': ['A different file failed to parse']}],
        'ai_analysis': {'status': 'completed', 'triage': {'disposition': 'confirmed'},
                        'errors': ['One lower severity finding was outside the budget'], 'proposals': [proposal]}}


@pytest.mark.parametrize('format', ['json', 'csv', 'md', 'markdown', 'html'])
def test_full_report_formats_preserve_version_coverage_and_review(saved_report, format):
    before = copy.deepcopy(saved_report)
    output, _, _ = serialize(saved_report, format)
    for text in ['scan-1', 'review-1', 'a' * 64, 'snapshot-digest', 'A different file failed to parse',
                 'proposal-1', 'Bind values separately', 'targeted_findings_remaining', 'approve',
                 'One lower severity finding', 'Submodule source excluded']:
        assert text in output
    if format != 'json':
        assert 'unapplied' in output and 'runtime-untested' in output
    assert saved_report == before
    assert serialize(saved_report, format)[0] == output


def test_csv_quotes_every_user_controlled_cell_and_preserves_proposal_fields(saved_report):
    saved_report['files'][0]['issues'][0]['message'] = ' =HYPERLINK("https://malicious.invalid")'
    saved_report['ai_analysis']['proposals'][0]['explanation'] = '\t=1+1'
    saved_report['ai_analysis']['proposals'][0]['diff'] = '@SUM(1+1)\nsecond line,"quoted"'
    rows = list(csv.DictReader(io.StringIO(serialize(saved_report, 'csv')[0])))
    finding = next(row for row in rows if row['Record'] == 'finding')
    proposal = next(row for row in rows if row['Record'] == 'proposal')
    assert finding['Message'].startswith("' =")
    assert proposal['Message'].startswith("'\t=")
    assert proposal['Diff'] == '\'@SUM(1+1)\nsecond line,"quoted"'
    assert json.loads(proposal['Details'])['validation']['status'] == 'passed'
    assert any(row['Record'] == 'coverage' and row['Status'] == 'partial' for row in rows)


def test_html_escapes_repository_and_model_text(saved_report):
    dangerous = '</pre><script>window.pwned=true</script><img src=x onerror=alert(1)>'
    saved_report['files'][0]['issues'][0]['message'] = dangerous
    saved_report['ai_analysis']['proposals'][0]['diff'] = dangerous
    saved_report['ai_analysis']['proposals'][0]['id'] = dangerous
    text = serialize(saved_report, 'html')[0]
    assert '<script>' not in text and '<img src=x' not in text
    assert '&lt;script&gt;' in text and 'Content-Security-Policy' in text
    assert "default-src 'none'" in text


def test_markdown_model_content_cannot_close_a_fence(saved_report):
    saved_report['ai_analysis']['proposals'][0]['diff'] = '```\n[click](javascript:alert(1))\n<script>bad()</script>'
    text = serialize(saved_report, 'md')[0]
    assert '\n    ```\n    [click]' in text
    assert '\n<script>' not in text and '\n[click]' not in text


@pytest.mark.parametrize('format', ['csv', 'md', 'html'])
def test_legacy_coverage_absence_remains_visible(saved_report, format):
    saved_report.pop('coverage')
    saved_report.pop('ai_analysis')
    assert 'Historical report has no verifiable coverage evidence' in serialize(saved_report, format)[0]


def test_sarif_validates_offline_against_pinned_official_schema(saved_report):
    schema = json.loads((Path(__file__).parent / 'fixtures/sarif/sarif-schema-2.1.0.json').read_text())
    validator = validator_for(schema)(schema)
    output = sarif(saved_report, {'logical-1': {'status': 'dismissed', 'reason': 'Documented safe caller'}})
    validator.validate(output)
    result = output['runs'][0]['results'][0]
    assert result['locations'][0]['physicalLocation']['artifactLocation']['uri'] == 'src/query%20file.py'
    assert result['partialFingerprints'] == {'codeagent/v1': 'v1:fingerprint'}
    assert result['suppressions'][0] == {'kind': 'external', 'status': 'accepted', 'justification': 'Documented safe caller'}
    assert output['runs'][0]['invocations'][0]['executionSuccessful'] is False
    assert 'failed to parse' in output['runs'][0]['invocations'][0]['toolExecutionNotifications'][0]['message']['text']
    encoded = json.dumps(output)
    assert 'SENSITIVE_SOURCE_SNIPPET' not in encoded
    assert 'query("?", user)' not in encoded
    assert 'proposals' not in output['runs'][0]


def test_sarif_reconfirmation_and_unreasoned_dismissals_do_not_suppress(saved_report):
    for triage in [{'status': 'dismissed', 'reason': 'Old review', 'requires_reconfirmation': True},
                   {'status': 'dismissed'}, {'status': 'confirmed', 'reason': 'Confirmed'}]:
        assert 'suppressions' not in sarif(saved_report, {'logical-1': triage})['runs'][0]['results'][0]


@pytest.mark.parametrize('path', ['../outside.py', '/absolute.py', 'src\\escape.py'])
def test_sarif_refuses_nonrelative_paths(saved_report, path):
    saved_report['files'][0]['path'] = path
    with pytest.raises(ValueError, match='non-relative'):
        sarif(saved_report)


def _proposal(identifier, original, replacement, content, conflicts=None):
    return {'id': identifier, 'status': 'reviewed', 'review': {'decision': 'approve'},
        'validation': {'status': 'passed'}, 'conflicts': conflicts or [],
        'edits': [{'file': 'app.py', 'source_hash': hashlib.sha256(content).hexdigest(),
                   'original': original, 'replacement': replacement}]}


def test_combined_diff_accepts_only_selected_compatible_edits_without_mutation(tmp_path):
    content = b'first = unsafe_one\nsecond = unsafe_two\n'
    (tmp_path / 'app.py').write_bytes(content)
    a = _proposal('a', 'unsafe_one', 'safe_one', content, conflicts=['unselected-conflict'])
    b = _proposal('b', 'unsafe_two', 'safe_two', content)
    report = {'ai_analysis': {'proposals': [a, b]}}
    output = combined_diff(report, ['a', 'b'], tmp_path)
    assert '+first = safe_one' in output and '+second = safe_two' in output
    assert (tmp_path / 'app.py').read_bytes() == content
    assert output == combined_diff(report, ['b', 'a'], tmp_path)


@pytest.mark.parametrize('failure', ['stale', 'overlap', 'conflict', 'unreviewed', 'failed-validation', 'duplicate-id', 'ambiguous-original'])
def test_combined_diff_rejects_unsafe_or_ineligible_selection(tmp_path, failure):
    content = b'first = unsafe_one\nsecond = unsafe_two\n'
    (tmp_path / 'app.py').write_bytes(content)
    a = _proposal('a', 'unsafe_one', 'safe_one', content)
    b = _proposal('b', 'unsafe_two', 'safe_two', content)
    selected = ['a', 'b']
    if failure == 'stale': a['edits'][0]['source_hash'] = 'b' * 64
    elif failure == 'overlap': b['edits'][0].update(original='first = unsafe_one', replacement='first = another')
    elif failure == 'conflict': a['conflicts'] = ['b']
    elif failure == 'unreviewed': a['review']['decision'] = 'reject'
    elif failure == 'failed-validation': a['validation']['status'] = 'failed'
    elif failure == 'duplicate-id': selected = ['a', 'a']
    elif failure == 'ambiguous-original': a['edits'][0]['original'] = 'unsafe_'
    with pytest.raises(ValueError):
        combined_diff({'ai_analysis': {'proposals': [a, b]}}, selected, tmp_path)
    assert (tmp_path / 'app.py').read_bytes() == content
