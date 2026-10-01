"""Durable execution. The API submits jobs; a separate worker executes them."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import time
import uuid
import httpx
from ingestion.snapshots import SourceCanceled, SourceError, build_snapshot, fetch_github_archive, verify_snapshot
from pipeline.store import Store, now
from settings import Settings


def redact(value, settings):
    if isinstance(value, str):
        for secret in (settings.github_token, settings.openai_key, settings.workspace_password, settings.session_secret):
            if secret:
                value = value.replace(secret, "[redacted]")
        return value
    if isinstance(value, dict):
        return {redact(key, settings): redact(item, settings) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item, settings) for item in value]
    return value


def verify_profile(output, config, tool):
    expected = config.get('profile_digests') or {}
    actual = output.get('profile_digests') or {}
    kind = 'dependency' if tool == 'depcheck' else 'source'
    if expected.get(kind) and actual.get(kind) != expected[kind]:
        raise SourceError('Pinned ' + kind + ' scanner profile is unavailable or changed. Restore the recorded engine/rules/database, or submit a new scan to select the current profile.')


async def remote_scan(job, snapshot_id, cancel, analyzers=None):
    url = os.environ["SCANNER_URL"].rstrip("/")
    timeout = job["config"].get("timeout_sec", 600)
    # A recovered lease can dispatch while the previous request is still being
    # canceled. Its reservation and cancellation must identify that invocation,
    # not the durable job shared by both attempts.
    request_id = str(uuid.uuid4())
    async with httpx.AsyncClient(timeout=timeout + 60, trust_env=False) as client:
        request = asyncio.create_task(client.post(url + "/scan", json={
            "job_id": request_id, "snapshot_id": snapshot_id,
            "analyzers": analyzers or job["config"].get("analyzers"), "timeout_sec": max(1, int(timeout)),
            "profile": job["config"].get("profile", "security-v1")}))
        try:
            while not request.done():
                if cancel():
                    try:
                        await client.post(url + "/cancel/" + request_id, timeout=5)
                    finally:
                        request.cancel()
                    raise SourceCanceled("Canceled")
                await asyncio.sleep(0.2)
            response = await request
            if response.status_code != 200:
                raise RuntimeError(f"Scanner service failed (HTTP {response.status_code})")
            return response.json()
        finally:
            if not request.done():
                request.cancel()


class JobOrchestrator:
    def __init__(self, storage_base=None, max_workers=2, settings=None, scan_fn=None):
        self.settings = settings or (Settings(storage=Path(storage_base).resolve()) if storage_base else Settings())
        self.settings.prepare()
        self.store = Store(self.settings.storage)
        self.scan_fn = scan_fn

    def execute(self, job, stopping=lambda: False):
        job_id = job["job_id"]
        owner = job.get("_lease_owner")
        canceled = lambda: stopping() or self.store.is_canceled(job_id) or (owner and not self.store.owns(job_id, owner))
        try:
            if canceled():
                raise SourceCanceled("Canceled")
            if job["kind"] == "scan":
                self._scan(job, canceled)
            elif job["kind"] == "provider_check":
                from pipeline.provider_checks import execute_check
                execute_check(self, job, canceled)
            else:
                self._review(job, canceled)
        except SourceCanceled:
            pass  # Cancellation already persisted; shutdown is recovered when the worker releases its lease.
        except Exception as exc:
            if canceled():
                return
            from integration.workflow import ReviewCancelled, ReviewInterrupted
            if isinstance(exc, ReviewCancelled):
                return
            status = "interrupted" if isinstance(exc, ReviewInterrupted) else "failed"
            self.store.finish(job_id, status, self.settings.redact(str(exc)), owner=owner)

    def _scan(self, job, cancel):
        start = time.monotonic()
        job_id, config, source = job["job_id"], job["config"], dict(job["source"])
        source.pop("report_hash", None)
        self.store.progress(job_id, "source", 5, owner=job.get("_lease_owner"))
        snapshot_id = source.get("snapshot_id") or job_id
        root = self.settings.storage / "snapshots" / snapshot_id
        if (root / "manifest.json").exists():
            manifest = json.loads((root / "manifest.json").read_text())
            verify_snapshot(root / "source", manifest)
        else:
            archive = self.settings.storage / "uploads" / f"{job_id}.zip"
            if source["source"] == "github":
                source = fetch_github_archive(source, archive, self.settings, cancel)
            if not archive.is_file():
                raise SourceError("Source archive expired; submit a new scan")
            manifest = build_snapshot(archive, snapshot_id, self.settings, source, config, cancel)
        source.update(snapshot_id=snapshot_id, digest=manifest["digest"], commit=manifest["source"].get("commit"))
        if source.get("project_id") and source.get("repository_id"):
            source["project_id"] = self.store.resolve_repository_project(source["project_id"], source["repository_id"])
        if not self.store.set_source(job_id, source, owner=job.get("_lease_owner")):
            raise SourceCanceled("Worker no longer owns this scan")
        self.store.progress(job_id, "analyze", 20, owner=job.get("_lease_owner"))
        result = self._analyze(job, root / "source", manifest, cancel)
        if cancel():
            raise SourceCanceled("Canceled")
        verify_snapshot(root / "source", manifest)
        self.store.progress(job_id, "report", 90, owner=job.get("_lease_owner"))
        for file in result.get("files", []):
            for issue in file["issues"]:
                issue["file"] = file["path"]
                issue["source_hash"] = manifest["files"].get(file["path"])
                issue["id"] = hashlib.sha256(json.dumps([file["path"], issue.get("line"), issue.get("tool"),
                    issue.get("rule_id"), issue.get("message"), issue["source_hash"]], ensure_ascii=False).encode()).hexdigest()[:24]
        report = {"schema_version": "2.0", "job_id": job_id,
            "meta": {"tools": result.get("tools", []), "repo": source, "generated_at": now(),
                "duration_ms": int((time.monotonic() - start) * 1000), "labels": config.get("labels", []), "snapshot": manifest,
                "tool_runs": result.get("tool_runs", []), "rulepack_version": result.get("rulepack_version")},
            "summary": result.get("summary", {"critical": 0, "high": 0, "medium": 0, "low": 0}),
            "files": result.get("files", []), "coverage": result.get("coverage", []),
            "status": result.get("status", "failed"), "warnings": manifest["warnings"], "errors": result.get("errors", [])}
        report['profile_digests'] = result.get('profile_digests')
        report['profile_reproducibility'] = 'pinned' if config.get('profile_digests') else 'unverified'
        if not config.get('profile_digests'):
            report['warnings'] = [*report['warnings'], 'This historical or offline submission did not pin effective scanner versions; its original engine profile cannot be reproduced reliably.']
        from pipeline.projects import prepare_identity
        prepare_identity(report, root / "source", config)
        report_hash = self.store.publish_scan_report(job_id, redact(report, self.settings), job.get("_lease_owner"))
        if not report_hash:
            raise SourceCanceled("Worker no longer owns this scan")
        source["report_hash"] = report_hash
        self.store.progress(job_id, "report", 100, owner=job.get("_lease_owner"))
        status = result.get("status", "failed")
        self.store.finish(job_id, status, "No requested analyzer completed successfully" if status == "failed" else None,
            review_config=config.get("review") if config.get("mode") == "multi_agent" else None,
            source=source, owner=job.get("_lease_owner"))

    def _analyze(self, job, source_path, manifest, cancel):
        """Checkpoint each trusted scanner independently; reuse only successful steps."""
        selected = list(dict.fromkeys("depcheck" if name == "trivy" else name for name in
            (job["config"].get("analyzers") or ["semgrep", "bandit", "dotnet", "depcheck"])))
        started, outputs = time.monotonic(), []
        for index, name in enumerate(selected):
            if cancel():
                raise SourceCanceled("Canceled")
            key = "scanner:" + name
            digest = hashlib.sha256(json.dumps(["scan-v2", manifest["digest"], name, job["config"]], sort_keys=True).encode()).hexdigest()
            saved = self.store.load_step(job["job_id"], key)
            if saved and saved.get("input_hash") == digest and saved.get("status") in ("completed", "skipped"):
                if not self.scan_fn:
                    verify_profile(saved['output'], job['config'], name)
                outputs.append(saved["output"])
                continue
            remaining = job["config"].get("timeout_sec", 600) - (time.monotonic() - started)
            if remaining <= 0:
                outputs.append({"coverage": [{"tool": name, "status": "failed", "files_scanned": 0,
                    "errors": ["Scan time budget exhausted before this analyzer started"]}], "tools": [name]})
                continue
            record = {"role": "scanner", "tool": name, "status": "running", "input_hash": digest,
                "started_at": now(), "attempt": (saved or {}).get("attempt", 0) + 1}
            if not self.store.save_step(job["job_id"], key, record, owner=job.get("_lease_owner")):
                raise SourceCanceled("Worker no longer owns this scan")
            step_started = time.monotonic()
            bounded_job = {**job, "config": {**job["config"], "timeout_sec": remaining}}
            if os.getenv("SCANNER_URL") and not self.scan_fn:
                output = asyncio.run(remote_scan(bounded_job, manifest["id"], cancel, [name]))
            else:
                scan_fn = self.scan_fn
                if scan_fn is None:
                    from analyzers.service import scan_workspace
                    scan_fn = scan_workspace
                kwargs = {"analyzers": [name], "timeout_sec": remaining, "cancel": cancel}
                if not self.scan_fn:
                    kwargs["profile"] = job["config"].get("profile", "security-v1")
                output = scan_fn(str(source_path), **kwargs)
            if cancel():
                raise SourceCanceled("Canceled")
            if not self.scan_fn:
                verify_profile(output, job['config'], name)
            statuses = [entry["status"] for entry in output.get("coverage", [])]
            record.update(status="skipped" if statuses and all(s == "skipped" for s in statuses)
                else output.get("status", "failed"), output=redact(output, self.settings), finished_at=now(),
                duration_ms=int((time.monotonic() - step_started) * 1000))
            if not self.store.save_step(job["job_id"], key, record, owner=job.get("_lease_owner")):
                raise SourceCanceled("Worker no longer owns this scan")
            outputs.append(output)
            self.store.progress(job["job_id"], name, 20 + round((index + 1) / len(selected) * 65), owner=job.get("_lease_owner"))
        coverage, tools, files, errors, tool_runs = [], [], {}, [], []
        for output in outputs:
            coverage.extend(output.get("coverage", []))
            tools.extend(output.get("tools", []))
            if any(item.get("status") != "skipped" for item in output.get("coverage", [])):
                errors.extend(output.get("errors", []))
            tool_runs.extend(output.get("tool_runs", []))
            for file in output.get("files", []):
                issues = files.setdefault(file["path"], {})
                for issue in file.get("issues", []):
                    identity = json.dumps([issue.get(k) for k in ("tool", "rule_id", "line", "message")])
                    issues[identity] = issue
        summary = {level: 0 for level in ("critical", "high", "medium", "low")}
        for issues in files.values():
            for issue in issues.values():
                summary[issue["severity"]] += 1
        statuses = [entry["status"] for entry in coverage]
        successful = {"completed", "succeeded"}
        status = "completed" if statuses and all(s in successful | {"skipped"} for s in statuses) and any(s in successful for s in statuses) else (
            "partial" if statuses and (any(s in successful | {"partial"} for s in statuses)
                or all(s == "skipped" for s in statuses)) else "failed")
        if statuses and all(s == "skipped" for s in statuses):
            errors.append("No applicable checks ran for the selected analyzers")
        return {"files": [{"path": path, "issues": list(issues.values())} for path, issues in sorted(files.items())],
            "coverage": coverage, "tools": list(dict.fromkeys(tools)), "tool_runs": tool_runs,
            "summary": summary, "status": status, "errors": list(dict.fromkeys(errors)),
            "profile_digests": next((output.get('profile_digests') for output in outputs if output.get('profile_digests')), None),
            "rulepack_version": next((output.get("rulepack_version") for output in outputs if output.get("rulepack_version")), None)}

    def _review(self, job, cancel):
        from integration.workflow import run_review
        parent = job["parent_job_id"]
        report, source = self.store.review_input(job["job_id"], job.get("_lease_owner"))
        if not report:
            raise SourceError("Frozen source report is unavailable")
        job = {**job, "source": source}
        snapshot_id = job["source"].get("snapshot_id")
        if not snapshot_id:
            raise SourceError("This historical report has no source snapshot; submit a new scan")
        root = self.settings.storage / "snapshots" / snapshot_id
        if not (root / "manifest.json").is_file():
            raise SourceError("Source snapshot expired; submit a new scan")
        manifest = json.loads((root / "manifest.json").read_text())
        verify_snapshot(root / "source", manifest)
        self.store.progress(job["job_id"], "agent_review", 10, owner=job.get("_lease_owner"))
        config = {**job["config"], "api_key": self.settings.openai_key,
            "base_url": self.settings.ollama_url if job["config"].get("provider") == "ollama" else None,
            "_sensitive_values": [value for value in (self.settings.github_token, self.settings.openai_key,
                self.settings.workspace_password, self.settings.session_secret) if value]}
        config["profile"] = (report.get("profiles") or {}).get("name", "security-v1")
        config["snapshot_digest"] = manifest["digest"]
        config["rule_digests"] = report.get("profiles") or {}

        async def validator(payload, *, is_cancelled):
            validation_id = str(uuid.uuid4())
            body = {"validation_id": validation_id, "snapshot_id": snapshot_id,
                "edits": payload["proposal"]["edits"], "target_findings": payload["target_findings"],
                "profile": config["profile"], "timeout_sec": min(120, max(1, int(payload["timeout_sec"])))}
            if not os.getenv("SCANNER_URL"):
                from analyzers.validation import validate_proposal
                return await asyncio.to_thread(validate_proposal, root, body, is_cancelled)
            url = os.environ["SCANNER_URL"].rstrip("/")
            async with httpx.AsyncClient(timeout=body["timeout_sec"] + 15, trust_env=False) as client:
                request = asyncio.create_task(client.post(url + "/validate", json=body))
                try:
                    while not request.done():
                        if is_cancelled():
                            try:
                                await client.post(url + "/cancel/" + validation_id, timeout=5)
                            finally:
                                request.cancel()
                            from integration.models import ReviewCancelled
                            raise ReviewCancelled("Proposal validation canceled")
                        await asyncio.sleep(0.2)
                    response = await request
                    response.raise_for_status()
                    return response.json()
                finally:
                    if not request.done():
                        request.cancel()
                    await asyncio.gather(request, return_exceptions=True)
        config["_validator"] = validator

        def on_step(key, data):
            if cancel():
                from integration.workflow import ReviewCancelled
                raise ReviewCancelled("Review canceled or worker lease lost")
            if not self.store.save_step(job["job_id"], key, redact(data, self.settings), owner=job.get("_lease_owner")):
                from integration.workflow import ReviewCancelled
                raise ReviewCancelled("Worker no longer owns this run")
            self.store.progress(job["job_id"], data.get("role", "agent_review"), 50, owner=job.get("_lease_owner"))

        from integration.workflow import ReviewInterrupted
        try:
            analysis = asyncio.run(run_review(report, str(root / "source"), config,
                on_step=on_step, load_step=lambda key: self.store.load_step(job["job_id"], key), is_cancelled=cancel))
        except ReviewInterrupted as exc:
            if getattr(exc, "partial_result", None) and not cancel():
                self._save_review_artifacts(job, report, exc.partial_result)
            raise
        if cancel():
            raise SourceCanceled("Canceled")
        self._save_review_artifacts(job, report, analysis)
        self.store.progress(job["job_id"], "report", 100, owner=job.get("_lease_owner"))
        status = {"complete": "completed", "partial": "partial", "failed": "failed"}.get(analysis["status"], "failed")
        self.store.finish(job["job_id"], status, self.settings.redact("; ".join(str(e) for e in analysis.get("errors", []))) or None,
                          owner=job.get("_lease_owner"))

    def _save_review_artifacts(self, job, report, analysis):
        enhanced = redact({**report, "ai_analysis": analysis, "review_run_id": job["job_id"]}, self.settings)
        if not self.store.publish_review(job["job_id"], enhanced, job.get("_lease_owner")):
            raise SourceCanceled("Worker no longer owns this review")


def get_orchestrator(storage_base=None):
    return JobOrchestrator(storage_base)
