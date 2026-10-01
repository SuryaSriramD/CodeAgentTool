"""Versioned exports shared by the browser and API-client CLI."""
import csv
import difflib
import hashlib
import html
import io
import json
from pathlib import Path, PurePosixPath
from urllib.parse import quote


def findings(report):
    return [{**finding, 'file': file['path']} for file in report.get('files', []) for finding in file.get('issues', [])]


def sarif(report, triage=None):
    triage = triage or {}
    rules, results = {}, []
    for finding in findings(report):
        identifier = str(finding.get('tool', 'legacy')) + '/' + str(finding.get('rule_id', 'unknown'))
        cwes = finding.get('cwe') or []
        cwes = [cwes] if isinstance(cwes, str) else cwes
        rules.setdefault(identifier, {'id': identifier, 'shortDescription': {'text': str(finding.get('type') or finding.get('family') or identifier)},
            'properties': {'tags': [str(cwe) for cwe in cwes], 'precision': 'medium'}})
        item = {'ruleId': identifier, 'level': {'critical': 'error', 'high': 'error', 'medium': 'warning', 'low': 'note'}.get(finding.get('severity'), 'warning'),
            'message': {'text': str(finding.get('message', identifier))},
            'properties': {'occurrence_id': finding.get('id'), 'logical_id': finding.get('logical_id'),
                'analysis_kind': finding.get('analysis_kind'), 'review_required': True}}
        path = PurePosixPath(finding['file'])
        if path.is_absolute() or '..' in path.parts or '\\' in str(path):
            raise ValueError('Report contains a non-relative source path')
        location = {'artifactLocation': {'uri': quote(str(path), safe='/'), 'uriBaseId': '%SRCROOT%'}}
        if finding.get('line', 0) > 0:
            location['region'] = {'startLine': finding['line'], 'endLine': max(finding['line'], finding.get('end_line') or finding['line'])}
        item['locations'] = [{'physicalLocation': location}]
        if finding.get('fingerprint'):
            item['partialFingerprints'] = {'codeagent/v1': finding['fingerprint']}
        decision = triage.get(finding.get('logical_id')) or {}
        if decision.get('status') == 'dismissed' and not decision.get('requires_reconfirmation') and decision.get('reason'):
            item['suppressions'] = [{'kind': 'external', 'status': 'accepted', 'justification': decision['reason']}]
        results.append(item)
    notifications = []
    for coverage in report.get('coverage', []):
        if coverage.get('status') not in ('completed', 'skipped'):
            notifications.append({'level': 'error', 'descriptor': {'id': 'coverage/' + coverage['tool']},
                'message': {'text': '; '.join(map(str, coverage.get('errors', []))) or 'Incomplete analyzer coverage'}})
    if not report.get('coverage'):
        notifications.append({'level': 'warning', 'message': {'text': 'Historical report has no verifiable coverage evidence'}})
    run = {'tool': {'driver': {'name': 'CodeAgent', 'semanticVersion': '0.3.0', 'informationUri': 'https://github.com/',
                              'rules': [rules[key] for key in sorted(rules)]}}, 'results': results,
        'invocations': [{'executionSuccessful': report.get('status') == 'completed' and not notifications,
                         'toolExecutionNotifications': notifications}],
        'properties': {'report_hash': report.get('report_hash'), 'job_id': report['job_id'],
            'profile': report.get('profiles'), 'source_commit': report.get('meta', {}).get('repo', {}).get('commit'),
            'snapshot_digest': report.get('meta', {}).get('snapshot', {}).get('digest'), 'proposals_applied': False}}
    return {'$schema': 'https://json.schemastore.org/sarif-2.1.0.json', 'version': '2.1.0', 'runs': [run]}


def _json(value):
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)


def _identity(report):
    meta = report.get('meta') or {}
    return {'scan_id': report['job_id'], 'review_run_id': report.get('review_run_id'),
        'report_hash': report.get('report_hash'), 'project_id': report.get('project_id'),
        'stream': report.get('stream'), 'generated_at': meta.get('generated_at'),
        'repository': meta.get('repo'), 'snapshot_digest': (meta.get('snapshot') or {}).get('digest'),
        'profiles': report.get('profiles'), 'status': report.get('status'), 'summary': report.get('summary')}


def _sections(report):
    """Structured saved evidence shared by all human-readable export formats."""
    yield 'Report identity', _json(_identity(report))
    yield 'Limitations', 'Proposals are unapplied and runtime-untested. Static validation does not establish runtime correctness.'
    warnings = report.get('warnings') or (report.get('meta', {}).get('snapshot') or {}).get('warnings')
    if warnings:
        yield 'Source warnings', _json(warnings)
    yield 'Analysis coverage', _json(report.get('coverage') or [])
    if not report.get('coverage'):
        yield 'Coverage limitation', 'Historical report has no verifiable coverage evidence.'
    for finding in findings(report):
        yield 'Finding ' + str(finding.get('id', 'historical')), _json(finding)
    analysis = report.get('ai_analysis')
    if analysis:
        yield 'Agent review', _json({key: value for key, value in analysis.items() if key != 'proposals'})
        for proposal in analysis.get('proposals') or []:
            yield 'Proposal ' + str(proposal.get('id', 'historical')), _json({key: value for key, value in proposal.items() if key not in ('diff', 'edits')})
            yield 'Proposed diff ' + str(proposal.get('id', 'historical')), proposal.get('diff') or 'No patch diff was produced.'


def serialize(report, format='json', triage=None):
    if format == 'json':
        return json.dumps(report, indent=2, ensure_ascii=False), 'application/json', 'json'
    if format == 'sarif':
        return json.dumps(sarif(report, triage), indent=2, ensure_ascii=False), 'application/sarif+json', 'sarif'
    if format == 'csv':
        stream = io.StringIO(newline='')
        writer = csv.writer(stream)
        columns = ('Record', 'ID', 'Severity', 'Tool', 'File', 'Line', 'Message', 'Status', 'Details', 'Diff', 'Report version')
        writer.writerow(columns)
        def safe(value):
            text = '' if value is None else str(value)
            return "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) or text.startswith(('\t', '\r')) else text
        def row(record, identifier='', severity='', tool='', file='', line='', message='', status='', details=None, diff=''):
            writer.writerow([safe(value) for value in (record, identifier, severity, tool, file, line, message, status,
                _json(details) if details is not None else '', diff, report.get('report_hash', ''))])
        row('report', report['job_id'], status=report.get('status'), details=_identity(report))
        row('limitation', message='Proposals are unapplied and runtime-untested. Static validation does not establish runtime correctness.')
        for entry in findings(report):
            row('finding', entry.get('id'), entry.get('severity'), entry.get('tool'), entry.get('file'), entry.get('line'),
                entry.get('message'), details=entry)
        for coverage in report.get('coverage') or []:
            row('coverage', tool=coverage.get('tool'), status=coverage.get('status'), details=coverage)
        if not report.get('coverage'):
            row('coverage', status='unavailable', message='Historical report has no verifiable coverage evidence.')
        warnings = report.get('warnings') or (report.get('meta', {}).get('snapshot') or {}).get('warnings')
        if warnings:
            row('source_warnings', details=warnings)
        analysis = report.get('ai_analysis')
        if analysis:
            row('agent_review', report.get('review_run_id'), status=analysis.get('status'),
                details={key: value for key, value in analysis.items() if key != 'proposals'})
            for proposal in analysis.get('proposals') or []:
                row('proposal', proposal.get('id'), message=proposal.get('explanation'), status=proposal.get('status'),
                    details={key: value for key, value in proposal.items() if key not in ('diff', 'edits')}, diff=proposal.get('diff'))
        return stream.getvalue(), 'text/csv; charset=utf-8', 'csv'
    if format in ('md', 'markdown'):
        # Saved evidence is indented code, so repository/model Markdown and HTML
        # cannot inject links, active markup, or closing fences into this report.
        lines = ['# CodeAgent security report', '']
        for title, content in _sections(report):
            title = html.escape(title).replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]').replace('`', '\\`').replace('\n', ' ')
            lines.extend(['## ' + title, '', *('    ' + line for line in str(content).splitlines()), ''])
        return '\n'.join(lines), 'text/markdown; charset=utf-8', 'md'
    if format == 'html':
        body = ''.join('<section><h2>' + html.escape(title) + '</h2><pre>' + html.escape(str(content)) + '</pre></section>'
                       for title, content in _sections(report))
        page = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        page += "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'\"><title>CodeAgent security report</title>"
        page += '<style>body{font:15px/1.6 system-ui;max-width:1000px;margin:32px auto;padding:0 20px;color:#172033}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f8;padding:16px;border-radius:6px}section{margin:32px 0}</style></head><body><h1>CodeAgent security report</h1>'
        return page + body + '</body></html>', 'text/html; charset=utf-8', 'html'
    raise ValueError('Choose json, sarif, csv, html, or md')


def combined_diff(report, selected_ids, source_root):
    selected_ids = list(selected_ids)
    if len(set(selected_ids)) != len(selected_ids):
        raise ValueError('Select each proposal once')
    proposals = {p['id']: p for p in (report.get('ai_analysis') or {}).get('proposals', [])}
    changes, originals = {}, {}
    root = Path(source_root).resolve(strict=True)
    for identifier in selected_ids:
        proposal = proposals.get(identifier)
        if (not proposal or proposal.get('status') != 'reviewed' or (proposal.get('review') or {}).get('decision') != 'approve'
                or (proposal.get('validation') or {}).get('status') != 'passed'
                or set(proposal.get('conflicts') or []) & set(selected_ids)):
            raise ValueError('Every selected proposal must pass review and static validation without conflicts')
        for edit in proposal['edits']:
            relative = PurePosixPath(edit['file'])
            if relative.is_absolute() or '..' in relative.parts or '\\' in str(relative):
                raise ValueError('Invalid proposal path')
            path = root.joinpath(*relative.parts)
            if any(p.is_symlink() for p in (path, *path.parents) if p != root):
                raise ValueError('Proposal path contains a symlink')
            path.resolve(strict=True).relative_to(root)
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != edit['source_hash'].removeprefix('sha256:'):
                raise ValueError('Proposal source hash is stale')
            original = originals.setdefault(str(relative), raw.decode('utf-8'))
            if original.count(edit['original']) != 1:
                raise ValueError('Proposal original is ambiguous or unavailable')
            start = original.index(edit['original'])
            change = (start, start + len(edit['original']), edit['replacement'])
            bucket = changes.setdefault(str(relative), [])
            if change in bucket:
                continue
            if any(start < end and prior_start < change[1] for prior_start, end, _ in bucket):
                raise ValueError('Selected proposals contain overlapping edits')
            bucket.append(change)
    output = []
    for file in sorted(changes):
        before, after = originals[file], originals[file]
        for start, end, replacement in sorted(changes[file], reverse=True):
            after = after[:start] + replacement + after[end:]
        for line in difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile='a/' + file, tofile='b/' + file):
            output.append(line if line.endswith('\n') else line + '\n\\ No newline at end of file\n')
    return ''.join(output)
