"""Project history and conservative, deterministic finding matching.

Occurrence IDs remain report-local. Logical IDs are opaque and fingerprints are
only matching evidence: ambiguous matches never inherit human decisions.
"""
from collections import Counter
from bisect import bisect_left
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import uuid


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def profile_config(config):
    return digest({**{key: config.get(key) for key in ('profile', 'analyzers', 'include', 'exclude')},
                   'source_digest': (config.get('profile_digests') or {}).get('source')})


def normalize_evidence(text):
    # Preserve literals and identifiers; ignore layout and comments outside strings.
    tokens = re.findall(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|//[^\n]*|/\*[\s\S]*?\*/|\#[^\n]*|[\w$]+|[^\s]''', text)
    return [token for token in tokens if not token.startswith(('//', '/*', '#'))]


def stable_database(value):
    """Advisory age is display metadata, never database identity."""
    if isinstance(value, dict):
        return {key: stable_database(item) for key, item in value.items()
                if key not in ('age_seconds', 'age_hours', 'checked_at')}
    return value


def prepare_identity(report, source_root, config):
    """Attach non-source-bearing matching evidence before freezing the report."""
    policy = {k: config.get(k) for k in ('profile', 'include', 'exclude')}
    policy['ingestion_version'] = 2
    tools = {}
    for coverage in report.get('coverage', []):
        tool = coverage['tool']
        tools[tool] = digest({'policy': policy, 'tool': tool, 'version': coverage.get('version'),
            'effective_profile': (report.get('profile_digests') or {}).get('dependency' if tool == 'depcheck' else 'source'),
            'rules': coverage.get('rule_digest') or coverage.get('rules_digest') or coverage.get('rulepack_version')
                or report.get('meta', {}).get('rulepack_version'),
            'database': {k: stable_database(v) for k, v in coverage.items() if k.startswith(('database', 'db_', 'advisory'))}
                if tool == 'depcheck' else None})
    report['profiles'] = {'source': digest({k: v for k, v in tools.items() if k != 'depcheck'}),
        'dependency': tools.get('depcheck'), 'tools': tools, 'config': profile_config(config),
        'name': config.get('profile', 'security-v1')}
    for file in report.get('files', []):
        try:
            path = (Path(source_root) / file['path']).resolve(strict=True)
            path.relative_to(Path(source_root).resolve())
            raw = path.read_bytes()
            text = raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8')
        except (OSError, ValueError, UnicodeError):
            text = ''
        lines = text.splitlines()
        nonempty = [(index, part) for index, line in enumerate(lines) if (part := normalize_evidence(line))]
        positions = [index for index, _ in nonempty]
        for finding in file['issues']:
            start = max(1, finding.get('line') or 1)
            end = max(start, finding.get('end_line') or start)
            tokens = normalize_evidence('\n'.join(lines[start - 1:end]))
            package = finding.get('dependency') or finding.get('package')
            if isinstance(package, dict):
                anchor = [package.get('ecosystem'), file['path'], package.get('purl') or package.get('name'),
                          package.get('advisory_id') or finding.get('rule_id')]
                # A versioned PURL must not invalidate advisory tracking after upgrades.
                if isinstance(anchor[2], str):
                    anchor[2] = re.sub(r'@[^/@?#]+(?=[?#]|$)', '', anchor[2])
            else:
                anchor = [finding.get('tool'), finding.get('rule_id'), file['path'], tokens]
            finding['fingerprint'] = 'v1:' + digest(anchor)
            # Match the occurrence using its source span, but invalidate human
            # decisions when nearby input/guard literals or package versions change.
            # Blank lines and comments do not change this bounded context.
            first, last = bisect_left(positions, start - 1), bisect_left(positions, end)
            before = [part for _, part in nonempty[max(0, first - 4):first]]
            after = [part for _, part in nonempty[last:last + 4]]
            finding['evidence_digest'] = digest(package if isinstance(package, dict)
                else [before, tokens, after]) if tokens or isinstance(package, dict) else None
            finding['rule_digest'] = tools.get(finding.get('tool'))
            finding['tracking_supported'] = bool(tokens or isinstance(package, dict))
    return report


class ProjectConflict(ValueError):
    pass


class ProjectStoreMixin:
    def migrate_projects(self, db):
        statements = [
            "CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY,name TEXT NOT NULL,kind TEXT NOT NULL,repository_key TEXT UNIQUE,created_at TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS project_aliases (alias TEXT PRIMARY KEY,project_id TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS scan_indexes (job_id TEXT NOT NULL,report_hash TEXT NOT NULL,project_id TEXT NOT NULL,stream TEXT NOT NULL,submitted_at TEXT NOT NULL,config_hash TEXT NOT NULL,data TEXT NOT NULL,PRIMARY KEY(job_id,report_hash))",
            "CREATE INDEX IF NOT EXISTS project_scans ON scan_indexes(project_id,stream,submitted_at)",
            "CREATE TABLE IF NOT EXISTS project_findings (id TEXT PRIMARY KEY,project_id TEXT NOT NULL,fingerprint TEXT NOT NULL,data TEXT NOT NULL,updated_at TEXT NOT NULL)",
            "CREATE INDEX IF NOT EXISTS matching_findings ON project_findings(project_id,fingerprint)",
            "CREATE TABLE IF NOT EXISTS finding_triage (finding_id TEXT PRIMARY KEY,status TEXT NOT NULL,revision INTEGER NOT NULL,reason TEXT,category TEXT,signature TEXT,updated_at TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS finding_history (seq INTEGER PRIMARY KEY AUTOINCREMENT,finding_id TEXT NOT NULL,kind TEXT NOT NULL,data TEXT NOT NULL,created_at TEXT NOT NULL)",
        ]
        for sql in statements:
            db.execute(sql)

    def create_project(self, name, kind='zip', repository_key=None):
        name = str(name).strip()
        if not name or len(name) > 160 or kind not in ('zip', 'github'):
            raise ValueError('Choose a project name of 1–160 characters and a valid source kind')
        with self.connect(write=True) as db:
            if repository_key:
                alias = db.execute('SELECT p.* FROM project_aliases a JOIN projects p ON p.id=a.project_id WHERE a.alias=?', (repository_key,)).fetchone()
                if alias:
                    return dict(alias)
                row = db.execute('SELECT * FROM projects WHERE repository_key=?', (repository_key,)).fetchone()
                if row:
                    return dict(row)
            item = {'id': str(uuid.uuid4()), 'name': name, 'kind': kind,
                    'repository_key': repository_key, 'created_at': timestamp()}
            db.execute('INSERT INTO projects VALUES(:id,:name,:kind,:repository_key,:created_at)', item)
            if repository_key:
                db.execute('INSERT OR REPLACE INTO project_aliases VALUES(?,?)', (repository_key, item['id']))
            return item

    def get_project(self, project_id):
        with self.connect() as db:
            row = db.execute('SELECT * FROM projects WHERE id=?', (project_id,)).fetchone()
            return dict(row) if row else None

    def projects(self, page=1, limit=20):
        with self.connect() as db:
            rows = db.execute('SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?', (limit, (page - 1) * limit))
            return {'items': [dict(row) for row in rows], 'total': db.execute('SELECT count(*) FROM projects').fetchone()[0],
                    'page': page, 'limit': limit}

    def pin_baseline(self, project_id, stream, config, run_id=None, report_hash=None):
        with self.connect() as db:
            if run_id:
                sql = 'SELECT * FROM scan_indexes WHERE project_id=? AND job_id=?'
                args = [project_id, run_id]
                if report_hash:
                    sql += ' AND report_hash=?'
                    args.append(report_hash)
                rows = db.execute(sql + ' ORDER BY rowid DESC', args).fetchall()
                if not rows:
                    raise ValueError('Baseline report is unavailable or belongs to another project')
                row = rows[0]
            else:
                row = db.execute('''SELECT s.* FROM scan_indexes s JOIN jobs j ON j.job_id=s.job_id
                    WHERE s.project_id=? AND s.stream=? AND s.config_hash=? AND j.status='completed'
                    ORDER BY s.submitted_at DESC,s.rowid DESC LIMIT 1''',
                    (project_id, stream, profile_config(config))).fetchone()
            return {'job_id': row['job_id'], 'report_hash': row['report_hash']} if row else None

    def resolve_repository_project(self, project_id, repository_id):
        """Upgrade the URL identity after GitHub returns its immutable repository ID."""
        if not repository_id:
            return project_id
        key = 'github:' + str(repository_id)
        with self.connect(write=True) as db:
            match = db.execute('SELECT id FROM projects WHERE repository_key=?', (key,)).fetchone()
            if match and match[0] != project_id:
                # Keep previously pinned history intact; use the established ID for new records.
                db.execute('UPDATE project_aliases SET project_id=? WHERE project_id=?', (match[0], project_id))
                return match[0]
            db.execute('UPDATE projects SET repository_key=? WHERE id=?', (key, project_id))
        return project_id

    def index_report(self, db, job_id, report):
        """Called under the report publisher's claim fence and transaction."""
        row = db.execute('SELECT source,config,submitted_at FROM jobs WHERE job_id=?', (job_id,)).fetchone()
        source, config = json.loads(row['source']), json.loads(row['config'])
        project = source.get('project_id')
        if not project:
            return report
        report.update(project_id=project, stream=source.get('stream', 'default'), baseline=source.get('baseline'))
        findings = [finding for file in report.get('files', []) for finding in file.get('issues', [])]
        counts = Counter(finding.get('fingerprint') for finding in findings)
        for finding in findings:
            fingerprint = finding.get('fingerprint')
            if not fingerprint:
                continue
            candidates = db.execute('SELECT id,data FROM project_findings WHERE project_id=? AND fingerprint=?',
                                    (project, fingerprint)).fetchall()
            match = None
            if counts[fingerprint] == 1 and len(candidates) == 1 and finding.get('tracking_supported'):
                match = candidates[0]
            elif candidates and finding.get('tracking_supported'):
                unchanged = [c for c in candidates if all(json.loads(c['data']).get(k) == finding.get(k)
                             for k in ('source_hash', 'line', 'file'))]
                if len(unchanged) == 1:
                    match = unchanged[0]
            finding['logical_id'] = match['id'] if match else str(uuid.uuid4())
            finding['tracking_ambiguous'] = bool(not match and (len(candidates) > 1 or counts[fingerprint] > 1))
            compact = {k: v for k, v in finding.items() if k not in ('suggestion', 'evidence', 'trace', 'code', 'snippet')}
            compact['latest_occurrence'] = {'job_id': job_id, 'id': finding['id'], 'line': finding.get('line')}
            compact['latest_submitted_at'] = row['submitted_at']
            compact['stream'] = source.get('stream', 'default')
            previous_data = json.loads(match['data']) if match else None
            if previous_data and previous_data.get('latest_submitted_at', '') > row['submitted_at']:
                continue
            if previous_data and self.triage_signature(previous_data) != self.triage_signature(compact):
                saved = db.execute('SELECT revision FROM finding_triage WHERE finding_id=?', (finding['logical_id'],)).fetchone()
                if saved:
                    db.execute('UPDATE finding_triage SET revision=revision+1,updated_at=? WHERE finding_id=?',
                               (timestamp(), finding['logical_id']))
                    db.execute('INSERT INTO finding_history(finding_id,kind,data,created_at) VALUES(?,?,?,?)',
                        (finding['logical_id'], 'evidence_changed', encode({'revision': saved['revision'] + 1,
                            'requires_reconfirmation': True, 'actor': 'scanner', 'job_id': job_id}), timestamp()))
            db.execute('INSERT OR REPLACE INTO project_findings VALUES(?,?,?,?,?)',
                (finding['logical_id'], project, fingerprint, encode(compact), timestamp()))
        return report

    def save_scan_index(self, db, job_id, frozen):
        if not frozen.get('project_id'):
            return
        row = db.execute('SELECT config,submitted_at FROM jobs WHERE job_id=?', (job_id,)).fetchone()
        # Compact evidence supports comparisons after source/report retention expires.
        data = {k: frozen.get(k) for k in ('job_id', 'report_hash', 'project_id', 'stream', 'profiles', 'baseline', 'status', 'coverage')}
        snapshot = frozen.get('meta', {}).get('snapshot', {})
        data['inventory'] = snapshot.get('files', {})
        data['source_inventory'] = snapshot.get('source_inventory', [])
        data['inventory_complete'] = snapshot.get('inventory_complete') is True
        data['snapshot_warnings'] = snapshot.get('warnings', [])
        data['findings'] = [{k: v for k, v in issue.items() if k not in ('suggestion', 'evidence', 'trace', 'code', 'snippet')}
                            for file in frozen.get('files', []) for issue in file.get('issues', [])]
        db.execute('INSERT OR REPLACE INTO scan_indexes VALUES(?,?,?,?,?,?,?)', (job_id, frozen['report_hash'],
            frozen['project_id'], frozen['stream'], row['submitted_at'], profile_config(json.loads(row['config'])), encode(data)))

    @staticmethod
    def triage_signature(finding):
        return digest([finding.get('fingerprint'), finding.get('rule_digest'), finding.get('evidence_digest')])

    def _finding(self, db, project_id, finding_id):
        row = db.execute('SELECT * FROM project_findings WHERE id=? AND project_id=?', (finding_id, project_id)).fetchone()
        if not row:
            return None
        item = json.loads(row['data'])
        item.update(id=finding_id, logical_id=finding_id, project_id=project_id)
        saved = db.execute('SELECT * FROM finding_triage WHERE finding_id=?', (finding_id,)).fetchone()
        triage = dict(saved) if saved else {'status': 'open', 'revision': 0, 'reason': None, 'category': None}
        if saved and saved['signature'] != self.triage_signature(item):
            triage.update(previous_status=saved['status'], status='open', requires_reconfirmation=True)
        triage.pop('signature', None)
        item['triage'] = triage
        history = [{'seq': r['seq'], 'kind': r['kind'], **json.loads(r['data']), 'created_at': r['created_at']}
                   for r in db.execute('SELECT * FROM finding_history WHERE finding_id=? ORDER BY seq', (finding_id,))]
        item['history'] = history
        item['notes'] = [event for event in history if event['kind'] == 'note']
        return item

    def project_findings(self, project_id, page=1, limit=20, status=None):
        with self.connect() as db:
            rows = db.execute('SELECT id FROM project_findings WHERE project_id=? ORDER BY updated_at DESC', (project_id,))
            items = [self._finding(db, project_id, r['id']) for r in rows]
            latest = {}
            for row in db.execute('SELECT stream,data FROM scan_indexes WHERE project_id=? ORDER BY submitted_at DESC,rowid DESC', (project_id,)):
                if row['stream'] not in latest:
                    latest[row['stream']] = json.loads(row['data'])
            for item in items:
                current = latest.get(item.get('stream', 'default'))
                if not current:
                    continue
                present = next((f for f in current['findings'] if f.get('logical_id') == item['logical_id']), None)
                if present:
                    state, reason = ('ambiguous', 'Finding evidence cannot be matched uniquely') if present.get('tracking_ambiguous') else ('existing', None)
                else:
                    previous = db.execute('SELECT data FROM scan_indexes WHERE job_id=? ORDER BY rowid DESC LIMIT 1',
                        (item['latest_occurrence']['job_id'],)).fetchone()
                    state, reason = self._absence(current, json.loads(previous[0]), item) if previous else ('not_assessed', 'Previous scan evidence is unavailable')
                item['assessment'] = {'classification': state, 'reason': reason, 'stream': current['stream'],
                    'job_id': current['job_id'], 'report_hash': current['report_hash']}
        if status:
            items = [item for item in items if item['triage']['status'] == status]
        return {'items': items[(page - 1) * limit:page * limit], 'total': len(items), 'page': page, 'limit': limit}

    def set_triage(self, project_id, finding_id, status, expected_revision, reason=None, category=None):
        if status not in ('open', 'confirmed', 'dismissed'):
            raise ValueError('Choose open, confirmed, or dismissed')
        if reason is not None and (not isinstance(reason, str) or len(reason) > 4000):
            raise ValueError('Reason must contain at most 4000 characters')
        if status == 'dismissed' and (not reason or not reason.strip() or category not in ('false_positive', 'accepted_risk', 'not_actionable')):
            raise ValueError('Dismissal requires a reason and a supported category')
        with self.connect(write=True) as db:
            item = self._finding(db, project_id, finding_id)
            if not item:
                raise KeyError('Finding not found')
            if type(expected_revision) is not int or item['triage']['revision'] != expected_revision:
                raise ProjectConflict('Finding changed; reload before saving')
            revision = expected_revision + 1
            db.execute('INSERT OR REPLACE INTO finding_triage VALUES(?,?,?,?,?,?,?)',
                (finding_id, status, revision, reason, category, self.triage_signature(item), timestamp()))
            db.execute('INSERT INTO finding_history(finding_id,kind,data,created_at) VALUES(?,?,?,?)',
                (finding_id, 'triage', encode({'status': status, 'reason': reason, 'category': category,
                    'revision': revision, 'actor': 'workspace user'}), timestamp()))
            return self._finding(db, project_id, finding_id)

    def add_note(self, project_id, finding_id, body):
        if not isinstance(body, str) or not body.strip() or len(body) > 10000:
            raise ValueError('Notes must contain 1–10000 characters')
        with self.connect(write=True) as db:
            if not self._finding(db, project_id, finding_id):
                raise KeyError('Finding not found')
            db.execute('INSERT INTO finding_history(finding_id,kind,data,created_at) VALUES(?,?,?,?)',
                       (finding_id, 'note', encode({'body': body.strip(), 'actor': 'workspace user'}), timestamp()))
            return self._finding(db, project_id, finding_id)

    def scan_index(self, job_id, report_hash=None):
        with self.connect() as db:
            args = [job_id]
            sql = 'SELECT data FROM scan_indexes WHERE job_id=?'
            if report_hash:
                sql += ' AND report_hash=?'
                args.append(report_hash)
            row = db.execute(sql + ' ORDER BY rowid DESC LIMIT 1', args).fetchone()
            return json.loads(row[0]) if row else None

    def comparison(self, job_id, report_hash=None, baseline_run_id=None, baseline_hash=None):
        current = self.scan_index(job_id, report_hash)
        if not current:
            raise ValueError('This report lacks project tracking evidence')
        reference = {'job_id': baseline_run_id, 'report_hash': baseline_hash} if baseline_run_id else current.get('baseline')
        baseline = self.scan_index(reference['job_id'], reference.get('report_hash')) if reference else None
        if reference and not baseline:
            raise ValueError('Baseline evidence is unavailable')
        if baseline and baseline['project_id'] != current['project_id']:
            raise ValueError('Baseline must belong to the same project')
        items, reasons = [], set()
        if baseline:
            current_tools = (current.get('profiles') or {}).get('tools', {})
            previous_tools = (baseline.get('profiles') or {}).get('tools', {})
            for tool in set(current_tools) | set(previous_tools):
                if not self._compatible(current, baseline, tool):
                    reasons.add('Scanner profile changed: ' + tool)
        old = {f['logical_id']: f for f in baseline['findings']} if baseline else {}
        matched = set()
        for finding in current['findings']:
            previous = old.get(finding.get('logical_id'))
            state = 'existing' if previous else 'new'
            reason = None
            if not baseline:
                state, reason = 'not_assessed', 'No baseline selected'
            elif finding.get('tracking_ambiguous') or not finding.get('tracking_supported'):
                state, reason = 'ambiguous', 'Finding evidence cannot be matched uniquely'
            elif not self._compatible(current, baseline, finding['tool']):
                state, reason = 'not_assessed', 'Relevant scanner profile changed'
            if previous:
                matched.add(previous['logical_id'])
            if reason:
                reasons.add(reason)
            items.append({'classification': state, 'finding': finding, 'baseline_finding': previous, 'reason': reason})
        for identifier, finding in old.items():
            if identifier in matched:
                continue
            state, reason = self._absence(current, baseline, finding)
            if reason:
                reasons.add(reason)
            items.append({'classification': state, 'finding': finding, 'baseline_finding': finding, 'reason': reason})
        return {'has_baseline': bool(baseline), 'current': {'job_id': job_id, 'report_hash': current['report_hash']},
            'baseline': {'job_id': baseline['job_id'], 'report_hash': baseline['report_hash']} if baseline else None,
            'items': items, 'counts': dict(Counter(i['classification'] for i in items)),
            'comparability_reasons': sorted(reasons), 'status': 'incomplete' if reasons else 'completed'}

    @staticmethod
    def _compatible(current, baseline, tool):
        a = (current.get('profiles') or {}).get('tools', {}).get(tool)
        b = (baseline.get('profiles') or {}).get('tools', {}).get(tool)
        return bool(a and b and a == b)

    def _absence(self, current, baseline, finding):
        if finding.get('tracking_ambiguous') or not finding.get('tracking_supported'):
            return 'ambiguous', 'Baseline finding was not uniquely trackable'
        if not self._compatible(current, baseline, finding['tool']):
            return 'not_assessed', 'Relevant scanner profile changed'
        # Changed/duplicated evidence must not make an old occurrence look fixed.
        neighbors = [f for f in current['findings'] if f['file'] == finding['file']
                     and f['tool'] == finding['tool'] and f['rule_id'] == finding['rule_id']]
        if neighbors:
            return 'ambiguous', 'Related finding remains with changed or ambiguous evidence'
        if finding['file'] not in current.get('inventory', {}):
            if current.get('inventory_complete') and finding['file'] not in current.get('source_inventory', []):
                return 'resolved', None
            return 'not_assessed', 'File is absent but complete ingestion could not be established'
        coverage = next((c for c in current.get('coverage', []) if c['tool'] == finding['tool']), {})
        if finding['file'] in coverage.get('scanned_paths', []) and coverage.get('status') in ('completed', 'partial'):
            outcomes = coverage.get('file_outcomes') or coverage.get('path_outcomes') or {}
            if isinstance(outcomes, list):
                outcomes = {outcome.get('path'): outcome for outcome in outcomes if isinstance(outcome, dict)}
            outcome = outcomes.get(finding['file']) if isinstance(outcomes, dict) else None
            if outcome and (outcome.get('status') if isinstance(outcome, dict) else outcome) not in ('completed', 'scanned', 'parsed'):
                return 'not_assessed', 'The file was not successfully checked'
            # Older partial reports cannot establish which rule failed on a path.
            if coverage.get('status') == 'partial' and not outcome:
                return 'not_assessed', 'Partial coverage lacks a successful per-file outcome'
            return 'resolved', None
        return 'not_assessed', 'The relevant file and scanner did not complete'
