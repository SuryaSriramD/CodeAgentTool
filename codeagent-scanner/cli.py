"""API-client CLI. It never executes submitted code or runs a second scanner stack."""
import argparse
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import zipfile

import httpx
from ingestion.policy import IGNORED_DIRS, excluded_source_path
from ingestion.snapshots import matches
from pipeline.projects import ProjectStoreMixin

TERMINAL = {'completed', 'partial', 'failed', 'canceled', 'interrupted'}
SEVERITY = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}


class CLIError(Exception):
    pass


def archive_source(root, output, include=(), exclude=(), max_files=10000, max_expanded=524288000, max_archive=52428800):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise CLIError('Local source must be a directory')
    count, size = 0, 0
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for directory, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and not d.startswith('._')
                and not matches(Path(directory, d).relative_to(root).as_posix(), exclude)
                and not matches(Path(directory, d).relative_to(root).as_posix() + '/', exclude))
            if any(Path(directory, d).is_symlink() for d in dirs):
                raise CLIError('Source contains a directory symlink; remove or exclude it')
            for name in sorted(files):
                path = Path(directory, name)
                relative = path.relative_to(root).as_posix()
                if (excluded_source_path(relative)
                        or (include and not matches(relative, include)) or matches(relative, exclude)):
                    continue
                if path.is_symlink() or not path.is_file():
                    raise CLIError('Source contains a symlink or special file: ' + relative)
                count += 1
                size += path.stat().st_size
                if count > max_files or size > max_expanded:
                    raise CLIError('Source exceeds the configured archive limits')
                archive.write(path, relative)
                if output.tell() > max_archive:
                    raise CLIError('Compressed source exceeds the upload limit')
    if output.tell() > max_archive:
        raise CLIError('Compressed source exceeds the upload limit')
    output.seek(0)


def policy_result(report, threshold='high', policy='all', comparison=None, initialize=False, dismissed=()):
    if report.get('status') != 'completed' or not report.get('coverage') or any(c.get('status') not in ('completed', 'skipped') for c in report['coverage']):
        return 2
    issues = [issue for file in report.get('files', []) for issue in file.get('issues', [])]
    if policy == 'new':
        if not comparison or not comparison.get('has_baseline'):
            return 0 if initialize else 2
        if comparison.get('status') != 'completed' or any(i['classification'] in ('not_assessed', 'ambiguous') for i in comparison.get('items', [])):
            return 2
        issues = [item['finding'] for item in comparison['items'] if item['classification'] == 'new']
    return int(any(SEVERITY.get(issue.get('severity'), 3) <= SEVERITY[threshold]
        and issue.get('logical_id') not in dismissed for issue in issues))


class Client:
    def __init__(self, server, token=None):
        if not server.startswith(('http://', 'https://')):
            raise CLIError('Server must be an HTTP or HTTPS API URL')
        self.http = httpx.Client(base_url=server.rstrip('/') + '/', timeout=60, trust_env=False,
            follow_redirects=False, headers={'Authorization': 'Bearer ' + token} if token else {})

    def request(self, method, path, **kwargs):
        response = self.http.request(method, path.lstrip('/'), **kwargs)
        if response.status_code >= 300:
            try:
                error = response.json().get('error', {})
                message = error.get('message', 'Request failed') if isinstance(error, dict) else str(error)
            except (ValueError, AttributeError):
                message = 'Request failed'
            raise CLIError(f'API HTTP {response.status_code}: {message}')
        return response

    def json(self, method, path, **kwargs):
        return self.request(method, path, **kwargs).json()

    def wait(self, identifier, timeout=1800):
        deadline, previous = time.monotonic() + timeout, None
        while time.monotonic() < deadline:
            job = self.json('GET', f'/jobs/{identifier}')
            state = (job['status'], (job.get('progress') or {}).get('phase'))
            if state != previous:
                print(f'{identifier}: {state[0]} {state[1] or ""}', file=sys.stderr)
                previous = state
            if job['status'] in TERMINAL:
                return job
            time.sleep(1)
        raise CLIError('Wait timed out; the saved job remains available: ' + identifier)

    def named_project(self, name):
        page, found = 1, []
        while True:
            projects = self.json('GET', '/projects', params={'page': page, 'limit': 100})
            found.extend(p for p in projects['items'] if p['name'] == name and p['kind'] == 'zip')
            if page * 100 >= projects['total']:
                break
            page += 1
        if len(found) > 1:
            raise CLIError('Several ZIP projects share this name; use --project with its ID')
        return found[0]['id'] if found else self.json('POST', '/projects', json={'name': name})['id']

    def dismissals(self, project_id, report):
        if not project_id:
            return set()
        signatures = {issue.get('logical_id'): ProjectStoreMixin.triage_signature(issue)
                      for file in report.get('files', []) for issue in file.get('issues', [])}
        page, found = 1, set()
        while True:
            payload = self.json('GET', f'/projects/{project_id}/findings', params={'status': 'dismissed', 'page': page, 'limit': 100})
            found.update(item['logical_id'] for item in payload['items']
                         if item['triage']['status'] == 'dismissed'
                         and not item['triage'].get('requires_reconfirmation')
                         and signatures.get(item['logical_id']) == ProjectStoreMixin.triage_signature(item))
            if page * 100 >= payload['total']:
                return found
            page += 1


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument('--server', default=os.environ.get('CODEAGENT_URL', 'http://localhost:8000'))
    actions = root.add_subparsers(dest='command', required=True)
    scan = actions.add_parser('scan')
    scan.add_argument('path', nargs='?')
    scan.add_argument('--github')
    scan.add_argument('--ref')
    scan.add_argument('--commit')
    scan.add_argument('--project')
    scan.add_argument('--project-name')
    scan.add_argument('--profile', choices=['security-v1', 'security-v2'], default='security-v1')
    scan.add_argument('--include', action='append', default=[])
    scan.add_argument('--exclude', action='append', default=[])
    scan.add_argument('--baseline-run-id')
    scan.add_argument('--baseline-hash')
    scan.add_argument('--initialize-baseline', action='store_true')
    scan.add_argument('--policy', choices=['all', 'new'], default='all')
    scan.add_argument('--severity', choices=list(SEVERITY), default='high')
    scan.add_argument('--review', action='store_true')
    scan.add_argument('--provider', choices=['ollama', 'openai'])
    scan.add_argument('--model')
    scan.add_argument('--timeout', type=int, default=1800)
    scan.add_argument('--format', choices=['json', 'sarif'], default='json')
    scan.add_argument('--output', type=Path)
    wait = actions.add_parser('wait')
    wait.add_argument('run_id')
    wait.add_argument('--timeout', type=int, default=1800)
    cancel = actions.add_parser('cancel')
    cancel.add_argument('run_id')
    compare = actions.add_parser('compare')
    compare.add_argument('run_id')
    compare.add_argument('--report-hash')
    compare.add_argument('--baseline-run-id')
    compare.add_argument('--baseline-hash')
    export = actions.add_parser('export')
    export.add_argument('run_id')
    export.add_argument('--review', action='store_true')
    export.add_argument('--report-hash')
    export.add_argument('--format', choices=['json', 'sarif', 'csv', 'html', 'md'], default='json')
    export.add_argument('--output', type=Path)
    return root


def write_output(content, destination):
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    else:
        sys.stdout.buffer.write(content + (b'' if content.endswith(b'\n') else b'\n'))


def main(argv=None):
    args = parser().parse_args(argv)
    client, active, review = None, None, None
    try:
        client = Client(args.server, os.environ.get('CODEAGENT_TOKEN'))
        if args.command == 'cancel':
            print(json.dumps(client.json('DELETE', '/jobs/' + args.run_id)))
            return 0
        if args.command == 'wait':
            active = args.run_id
            job = client.wait(active, args.timeout)
            print(json.dumps(job))
            return 0 if job['status'] == 'completed' else 130 if job['status'] == 'canceled' else 2
        if args.command == 'compare':
            comparison = client.json('GET', f'/reports/{args.run_id}/comparison', params={
                key: getattr(args, key) for key in ('report_hash', 'baseline_run_id', 'baseline_hash') if getattr(args, key)})
            print(json.dumps(comparison, indent=2))
            return 0 if comparison['status'] == 'completed' else 2
        if args.command == 'export':
            route = f'/reviews/{args.run_id}/export' if args.review else f'/reports/{args.run_id}/export'
            params = {'format': args.format, **({'report_hash': args.report_hash} if args.report_hash and not args.review else {})}
            write_output(client.request('GET', route, params=params).content, args.output)
            return 0
        if bool(args.path) == bool(args.github):
            raise CLIError('Provide exactly one local directory or --github URL')
        if args.review and not (args.provider and args.model):
            raise CLIError('--review requires an explicit --provider and --model')
        if args.path and not (args.project or args.project_name):
            raise CLIError('Local scans require an explicit --project ID or --project-name')
        if args.timeout <= 0:
            raise CLIError('--timeout must be positive')
        data = {'mode': 'static', 'profile': args.profile, 'include': ','.join(args.include), 'exclude': ','.join(args.exclude)}
        data.update({key: getattr(args, key) for key in ('ref', 'commit', 'baseline_run_id', 'baseline_hash') if getattr(args, key)})
        if args.project:
            data['project_id'] = args.project
        if args.github:
            data['github_url'] = args.github
            submission = client.json('POST', '/analyze', data=data)
        else:
            path = Path(args.path).resolve(strict=True)
            if not args.project:
                data['project_id'] = client.named_project(args.project_name or path.name)
            with tempfile.TemporaryFile() as archive:
                archive_source(path, archive, args.include, args.exclude)
                submission = client.json('POST', '/analyze', data=data, files={'file': (path.name + '.zip', archive, 'application/zip')})
        active = scan_id = submission['job_id']
        job = client.wait(active, args.timeout)
        if job['status'] == 'canceled':
            return 130
        report = client.json('GET', f'/reports/{scan_id}')
        export_path = f'/reports/{scan_id}/export'
        if args.review and job['status'] in ('completed', 'partial'):
            print(f'Explicit review: {args.provider} / {args.model}', file=sys.stderr)
            submission = client.json('POST', f'/reports/{scan_id}/enhance', json={'provider': args.provider, 'model': args.model})
            active = submission['run_id']
            review = client.wait(active, args.timeout)
            if review['status'] != 'completed':
                print('Review incomplete; retained artifacts remain available.', file=sys.stderr)
            if review['status'] == 'canceled':
                return 130
            export_path = f'/reviews/{active}/export'
        comparison = client.json('GET', f'/reports/{scan_id}/comparison') if args.policy == 'new' else None
        write_output(client.request('GET', export_path, params={'format': args.format}).content, args.output)
        dismissed = client.dismissals(report.get('project_id'), report)
        result = policy_result(report, args.severity, args.policy, comparison, args.initialize_baseline, dismissed)
        if args.review and (not review or review['status'] != 'completed'):
            return 2
        return result
    except KeyboardInterrupt:
        if active and client:
            try:
                client.json('DELETE', '/jobs/' + active)
            except (CLIError, httpx.HTTPError):
                pass
        return 130
    except (CLIError, httpx.HTTPError, OSError, ValueError, KeyError) as exc:
        message = str(exc)
        token = os.environ.get('CODEAGENT_TOKEN')
        if token:
            message = message.replace(token, '[redacted]')
        print('CodeAgent: ' + message, file=sys.stderr)
        return 2
    finally:
        if client:
            client.http.close()


if __name__ == '__main__':
    raise SystemExit(main())
