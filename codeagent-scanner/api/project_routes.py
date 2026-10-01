"""Authenticated project workflow and saved-artifact export routes."""
from pathlib import Path
import re
from fastapi import HTTPException, Query
from fastapi.responses import Response
from pipeline.contracts import Project, ProjectInput, ProjectList, TriageInput, NoteInput, ProposalSelection, ProjectFinding, ProjectFindingList, Comparison
from pipeline.exports import serialize, combined_diff
from pipeline.projects import ProjectConflict


def register_routes(app, store, read_report, review_report, valid_id, settings):
    def project(identifier):
        found = store().get_project(valid_id(identifier))
        if not found:
            raise HTTPException(404, 'Project not found')
        return found

    def version(value):
        if value and not re.fullmatch(r'[0-9a-f]{64}', value):
            raise HTTPException(400, 'Invalid report version hash')
        return value

    @app.get('/projects', response_model=ProjectList)
    def projects(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
        return store().projects(page, limit)

    @app.post('/projects', status_code=201, response_model=Project)
    def create_project(body: ProjectInput):
        try:
            return store().create_project(settings.redact(body.name), body.kind)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.get('/projects/{project_id}', response_model=Project)
    def get_project(project_id: str):
        return project(project_id)

    @app.get('/projects/{project_id}/findings', response_model=ProjectFindingList)
    def findings(project_id: str, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), status: str | None = None):
        project(project_id)
        return store().project_findings(project_id, page, limit, status)

    @app.patch('/projects/{project_id}/findings/{finding_id}/triage', response_model=ProjectFinding)
    def triage(project_id: str, finding_id: str, body: TriageInput):
        project(project_id)
        try:
            return store().set_triage(project_id, valid_id(finding_id), body.status, body.expected_revision,
                settings.redact(body.reason) if body.reason else None, body.category)
        except ProjectConflict as exc:
            raise HTTPException(409, str(exc)) from exc
        except KeyError as exc:
            raise HTTPException(404, 'Finding not found') from exc
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post('/projects/{project_id}/findings/{finding_id}/notes', status_code=201, response_model=ProjectFinding)
    def note(project_id: str, finding_id: str, body: NoteInput):
        project(project_id)
        try:
            return store().add_note(project_id, valid_id(finding_id), settings.redact(body.body))
        except KeyError as exc:
            raise HTTPException(404, 'Finding not found') from exc
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.get('/reports/{job_id}/comparison', response_model=Comparison)
    def comparison(job_id: str, report_hash: str | None = None, baseline_run_id: str | None = None, baseline_hash: str | None = None):
        try:
            return store().comparison(valid_id(job_id), version(report_hash),
                valid_id(baseline_run_id) if baseline_run_id else None, version(baseline_hash))
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    def export(data, format):
        annotations = {}
        if format == 'sarif' and data.get('project_id'):
            with store().connect() as db:
                for file in data.get('files', []):
                    for finding in file['issues']:
                        if finding.get('logical_id'):
                            item = store()._finding(db, data['project_id'], finding['logical_id'])
                            # Never apply a decision made against a different rule/evidence version.
                            if item and store().triage_signature(item) == store().triage_signature(finding):
                                annotations[finding['logical_id']] = item['triage']
        try:
            body, mime, extension = serialize(data, format, annotations)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        return Response(body, media_type=mime, headers={
            'Content-Disposition': f'attachment; filename="codeagent-{data.get("review_run_id") or data["job_id"]}.{extension}"',
            'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox"})

    @app.get('/reports/{job_id}/export')
    def export_report(job_id: str, format: str = 'json', report_hash: str | None = None):
        data = read_report(job_id, report_hash=version(report_hash))
        data = {**data, 'ai_analysis': None}
        return export(data, format)

    @app.get('/reviews/{run_id}/export')
    def export_review(run_id: str, format: str = 'json'):
        return export(review_report(run_id), format)

    @app.post('/reviews/{run_id}/proposals/export')
    def export_proposals(run_id: str, body: ProposalSelection):
        data = review_report(run_id)
        job = store().get(run_id)
        snapshot_id = job['source'].get('snapshot_id') if job else None
        if not snapshot_id:
            raise HTTPException(409, 'Proposal source is unavailable')
        root = settings.storage / 'snapshots' / snapshot_id / 'source'
        try:
            diff = combined_diff(data, body.proposal_ids, root)
        except (ValueError, OSError, UnicodeError) as exc:
            raise HTTPException(409, 'Combined diff is unavailable: ' + settings.redact(str(exc))) from exc
        return Response(diff, media_type='text/x-diff', headers={'Content-Disposition': f'attachment; filename="proposals-{run_id}.diff"'})
