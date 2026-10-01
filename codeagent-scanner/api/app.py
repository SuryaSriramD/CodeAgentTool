"""HTTP API for the durable scanner. Execution belongs to the worker process."""
import asyncio
from contextlib import asynccontextmanager
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import time
import uuid

import httpx
from fastapi import FastAPI, HTTPException, Request, Query, Body
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import ValidationError

from ingestion.snapshots import SourceError, validate_github_url, github_repository_identity
from pipeline.contracts import Job, JobList, ReviewConfig, ScanReport, Submission
from pipeline.orchestrator import redact
from pipeline.store import Store, QueueFull, TERMINAL, now
from settings import Settings


class RequestBodyLimit:
    """Bound streamed multipart bytes before Starlette spools uploaded files."""
    def __init__(self, app, limit):
        self.app, self.limit = app, limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        try:
            declared = int(headers.get(b"content-length", b"0"))
        except ValueError:
            return await JSONResponse({"error": {"code": "400", "message": "Invalid Content-Length"}}, 400)(scope, receive, send)
        if declared > self.limit:
            return await JSONResponse({"error": {"code": "413", "message": "Request exceeds upload limit"}}, 413)(scope, receive, send)
        consumed = 0
        async def bounded_receive():
            nonlocal consumed
            message = await receive()
            if message["type"] == "http.request":
                consumed += len(message.get("body", b""))
                if consumed > self.limit:
                    raise HTTPException(413, "Request exceeds upload limit")
            return message
        await self.app(scope, bounded_receive, send)


def valid_id(value):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
        raise HTTPException(404, "Resource not found")
    return value


def create_app(settings=None):
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        settings.prepare()
        app.state.store = Store(settings.storage)
        yield

    app = FastAPI(title="CodeAgent Security Scanner", version="0.2.0", lifespan=lifespan)
    app.add_middleware(RequestBodyLimit, limit=settings.max_upload_size + 1024 * 1024)
    app.state.settings = settings
    login_attempts = {}

    def store():
        if not hasattr(app.state, "store"):
            settings.prepare()
            app.state.store = Store(settings.storage)
        return app.state.store

    def signature(value):
        key = settings.session_secret or hashlib.sha256(("codeagent-session:" + settings.workspace_password).encode()).hexdigest()
        return hmac.new(key.encode(), value.encode(), hashlib.sha256).hexdigest()

    def authenticated(request):
        if not settings.workspace_password:
            return True
        bearer = request.headers.get("authorization", "")
        if bearer.startswith("Bearer ") and hmac.compare_digest(bearer[7:], settings.workspace_password):
            return True
        token = request.cookies.get("codeagent_session", "")
        try:
            payload, sig = token.rsplit(".", 1)
            expiry = int(payload.split(".", 1)[0])
            return expiry > time.time() and hmac.compare_digest(signature(payload), sig)
        except (ValueError, TypeError):
            return False

    @app.middleware("http")
    async def access(request, call_next):
        # Reject cross-origin writes even on a password-free localhost installation.
        origin = request.headers.get("origin")
        allowed = {item.strip() for item in os.getenv("PUBLIC_ORIGIN", "http://localhost:3000,http://127.0.0.1:3000").split(",")}
        if origin and request.method not in ("GET", "HEAD", "OPTIONS") and origin not in allowed:
            return JSONResponse({"error": {"code": "FORBIDDEN", "message": "Origin is not allowed"}}, 403)
        if request.url.path not in ("/health", "/auth/status", "/auth/login") and not authenticated(request):
            return JSONResponse({"error": {"code": "UNAUTHORIZED", "message": "Sign in to this workspace"}}, 401)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return JSONResponse({"error": {"code": str(exc.status_code), "message": exc.detail}}, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse({"error": {"code": "INVALID_INPUT", "message": "Invalid request", "details": [
            {"location": list(error["loc"]), "message": error["msg"]} for error in exc.errors()]}}, 422)

    @app.exception_handler(QueueFull)
    async def queue_full(request, exc):
        return JSONResponse({"error": {"code": "429", "message": str(exc)}}, 429)

    @app.get("/health")
    def health():
        return {"status": "ok", "version": "0.2.0"}

    @app.get("/auth/status")
    def auth_status(request: Request):
        return {"required": bool(settings.workspace_password), "authenticated": authenticated(request)}

    @app.post("/auth/login")
    async def login(request: Request):
        host = request.client.host if request.client else "unknown"
        attempts = [t for t in login_attempts.get(host, []) if time.time() - t < 60]
        if len(attempts) >= 5:
            raise HTTPException(429, "Too many login attempts; wait one minute")
        try:
            payload = await request.json()
        except ValueError:
            raise HTTPException(400, "Send a JSON object containing the workspace password")
        if not isinstance(payload, dict) or not isinstance(payload.get("password"), str):
            raise HTTPException(400, "Password is required")
        if settings.workspace_password and not hmac.compare_digest(payload["password"], settings.workspace_password):
            login_attempts[host] = [*attempts, time.time()]
            raise HTTPException(401, "Incorrect workspace password")
        login_attempts.pop(host, None)
        token = f"{int(time.time()) + 43200}.{secrets.token_hex(16)}"
        response = JSONResponse({"authenticated": True})
        response.set_cookie("codeagent_session", token + "." + signature(token), httponly=True,
                            secure=settings.cookie_secure, samesite="strict", max_age=43200, path="/")
        return response

    @app.post("/auth/logout")
    def logout():
        response = JSONResponse({"authenticated": False})
        response.delete_cookie("codeagent_session", path="/")
        return response

    def ai_config():
        default = ReviewConfig(provider=os.getenv("AI_PROVIDER", "ollama"), model=os.getenv("AI_MODEL", "")).model_dump()
        return {**default, **store().get_setting("ai", {})}

    @app.get("/config/ai")
    def get_ai_config():
        config = ai_config()
        return {**config, "enabled": bool(config["model"]), "bridge_initialized": bool(config["model"]),
                "max_concurrent_reviews": 1 if config["provider"] == "ollama" else 2}

    @app.post("/config/ai/test", status_code=202, response_model=Submission)
    async def test_ai_config(body: dict = Body(default={})):
        from pipeline.provider_checks import connection_fingerprint
        config = validate_review(body)
        await ensure_provider(config)
        config["_connection_fingerprint"] = connection_fingerprint(settings, config["provider"], config["model"])
        if config["provider"] == "ollama":
            local = (await providers_available())["ollama"]
            config["_model_digest"] = local.get("model_digests", {}).get(config["model"])
        job = store().create_job("provider_check", config, {"source": "synthetic", "name": "Provider connection test"})
        return {"job_id": job["job_id"], "run_id": job["job_id"], "status": job["status"]}

    def validate_review(body):
        try:
            config = ReviewConfig(**{**ai_config(), **body}).model_dump()
        except ValidationError as exc:
            raise HTTPException(400, "; ".join(e["msg"] for e in exc.errors())) from exc
        if config["model"] and (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/@-]*", config["model"]) or config["model"].startswith("GPT_")):
            raise HTTPException(400, "Use an exact provider model ID, not a legacy GPT_* enum")
        return config

    @app.patch("/config/ai")
    def set_ai_config(body: dict = Body(...)):
        config = validate_review(body)
        store().set_setting("ai", config)
        return {"ok": True, "updated": body, **config}

    async def tools_available():
        if os.getenv("SCANNER_URL"):
            try:
                async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
                    response = await client.get(os.environ["SCANNER_URL"].rstrip("/") + "/capabilities")
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPError:
                return []
        from analyzers.service import get_capabilities
        return await asyncio.to_thread(get_capabilities)

    async def scanner_profiles():
        try:
            if os.getenv("SCANNER_URL"):
                async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                    response = await client.get(os.environ["SCANNER_URL"].rstrip("/") + "/profiles")
                    response.raise_for_status()
                    return response.json()
            from analyzers.profiles import profile_metadata
            return await asyncio.to_thread(lambda: {name: profile_metadata(name) for name in ('security-v1', 'security-v2')})
        except (httpx.HTTPError, OSError, ValueError):
            return {}

    async def providers_available():
        local = {"available": False, "models": [], "error": "Ollama is unavailable or has no installed model"}
        try:
            async with httpx.AsyncClient(timeout=3, trust_env=False) as client:
                response = await client.get(settings.ollama_url.rstrip("/") + "/api/tags")
                response.raise_for_status()
                tags = response.json().get("models", [])[:40]
                installed = [item["name"] for item in tags]
                async def can_generate(name):
                    try:
                        metadata = await client.post(settings.ollama_url.rstrip("/") + "/api/show", json={"model": name})
                        metadata.raise_for_status()
                        return name if "completion" in metadata.json().get("capabilities", []) else None
                    except (httpx.HTTPError, ValueError, TypeError, AttributeError):
                        return None
                models = [name for name in await asyncio.gather(*(can_generate(name) for name in installed)) if name]
                local = {"available": bool(models), "models": models,
                    "configured": True, "reachable": True,
                    "model_digests": {item["name"]: item.get("digest") for item in tags},
                    "excluded_models": [name for name in installed if name not in models],
                    "error": None if models else "Install an Ollama text-generation model with completion support before review"}
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
            pass
        from pipeline.provider_checks import connection_fingerprint
        configured = ai_config()
        providers = {"openai": {"available": bool(settings.openai_key), "models": [],
                "configured": bool(settings.openai_key), "reachable": None, "validated": False}, "ollama": local}
        for kind, item in providers.items():
            model = configured["model"] if configured["provider"] == kind else (item.get("models") or [None])[0]
            if model:
                saved = store().get_setting("provider_test:" + kind + ":" + model)
                if saved and saved.get("configuration_hash") == connection_fingerprint(settings, kind, model):
                    if kind != "ollama" or saved.get("model_digest") == item.get("model_digests", {}).get(model):
                        item["last_test"] = {k: v for k, v in saved.items() if k != "configuration_hash"}
                        item["validated"] = bool(saved.get("schema_test_passed"))
        return providers

    async def ensure_provider(config):
        if not config.get("model"):
            raise HTTPException(400, "Select a provider and model before starting AI review")
        if config["provider"] == "openai" and not settings.openai_key:
            raise HTTPException(503, "Configure OPENAI_API_KEY on the server")
        if config["provider"] == "ollama":
            local = (await providers_available())["ollama"]
            if config["model"] not in local["models"]:
                raise HTTPException(503, "The selected Ollama model is not installed or Ollama is unavailable")
            config["_model_digest"] = local.get("model_digests", {}).get(config["model"])

    @app.get("/capabilities")
    async def capabilities():
        from integration.workflow import WORKFLOW_VERSION, implementation_digest
        analyzers, providers, profile_digests = await asyncio.gather(tools_available(), providers_available(), scanner_profiles())
        online = store().worker_online()
        return {"ready": online and bool(analyzers) and all(a.get("available") for a in analyzers),
                "worker_online": online, "analyzers": analyzers, "providers": providers,
                "languages": sorted({lang for a in analyzers for lang in a.get("languages", [])}),
                "auth_required": bool(settings.workspace_password), "private_github": bool(settings.github_token),
                "max_upload_size": settings.max_upload_size, "proposal_only": True,
                "profiles": [{"id": "security-v1", "default": True, "status": "current"},
                             {"id": "security-v2", "default": False, "status": "candidate"}],
                "profile_digests": profile_digests,
                "workflow": {"version": WORKFLOW_VERSION, "implementation_hash": implementation_digest()},
                "release_gate": {"status": "candidate", "human_review_required": True}}

    @app.get("/tools")
    async def tools():
        items = await tools_available()
        return {"available": [t["name"] for t in items if t.get("available")],
                "default": [t["name"] for t in items], "versions": {t["name"]: t.get("version", "unknown") for t in items}}

    @app.get("/config/analyzers")
    async def analyzer_config():
        names = [tool["name"] for tool in await tools_available()]
        return {"defaults": names, "rulesets": {"semgrep": ["security-v1", "security-v2"]}, "allow_list": ["https://github.com/"]}

    @app.post("/analyze", status_code=202, response_model=Submission)
    @app.post("/analyze-async", status_code=202, response_model=Submission)
    async def submit(request: Request):
        if store().list(limit=1, status="queued")["total"] >= 100:
            raise HTTPException(429, "Job queue is full; retry later")
        form = await request.form(max_files=1, max_fields=30)
        url, upload = form.get("github_url"), form.get("file")
        if bool(url) == bool(upload):
            raise HTTPException(400, "Provide exactly one GitHub URL or ZIP file")
        mode = str(form.get("mode", "static"))
        if mode not in ("static", "multi_agent"):
            raise HTTPException(400, "Mode must be static or multi_agent")
        try:
            timeout = int(str(form.get("timeout_sec", "600")))
            if not 1 <= timeout <= 7200:
                raise ValueError()
        except ValueError:
            raise HTTPException(400, "timeout_sec must be between 1 and 7200")
        csv = lambda name: [part.strip() for part in str(form.get(name, "")).split(",") if part.strip()]
        config = {"mode": mode, "timeout_sec": timeout, "analyzers": csv("analyzers") or None,
                  "include": csv("include"), "exclude": csv("exclude"), "labels": csv("labels")}
        config["profile"] = str(form.get("profile", "security-v1"))
        if config["profile"] not in ("security-v1", "security-v2"):
            raise HTTPException(400, "Choose security-v1 or candidate security-v2")
        project_id = str(form.get("project_id") or "")
        if project_id:
            project = store().get_project(valid_id(project_id))
            if not project or project["kind"] != ("github" if url else "zip"):
                raise HTTPException(400, "Choose a project with the same source kind")
        if config["analyzers"] and set(config["analyzers"]) - {"semgrep", "bandit", "dotnet", "depcheck", "trivy"}:
            raise HTTPException(400, "Choose semgrep, bandit, dotnet, or depcheck analyzers")
        if mode == "multi_agent":
            config["review"] = validate_review({**{key: str(form[key]) for key in ("provider", "model", "min_severity") if key in form}, "workflow_mode": "multi_agent"})
            await ensure_provider(config["review"])
        job_id = str(uuid.uuid4())
        if url:
            try:
                owner, repository = validate_github_url(str(url))
            except SourceError as exc:
                raise HTTPException(400, str(exc)) from exc
            source = {"source": "github", "url": str(url), "ref": form.get("ref") or None, "commit": form.get("commit") or None}
            if any(value and (not isinstance(value, str) or len(value) > 250 or "\x00" in value) for value in (source["ref"], source["commit"])):
                raise HTTPException(400, "Invalid ref or commit")
            try:
                identity = await asyncio.to_thread(github_repository_identity, str(url), settings)
            except SourceError as exc:
                raise HTTPException(400, str(exc)) from exc
            source['url'] = identity['url']
            source['repository_id'] = identity['id']
            if not source['ref'] and not source['commit']:
                source['ref'] = identity['default_branch']
            project = store().create_project(owner + "/" + repository, 'github', 'github:' + str(identity['id']))
            project_id = project['id']
        else:
            if not hasattr(upload, "read") or not str(upload.filename).lower().endswith(".zip"):
                raise HTTPException(400, "Upload a ZIP archive")
            target = settings.storage / "uploads" / f"{job_id}.zip"
            size = 0
            try:
                with target.open("xb") as output:
                    while block := await upload.read(65536):
                        size += len(block)
                        if size > settings.max_upload_size:
                            raise HTTPException(413, "Upload exceeds MAX_UPLOAD_SIZE")
                        output.write(block)
            except BaseException:
                target.unlink(missing_ok=True)
                raise
            finally:
                await upload.close()
            source = {"source": "zip", "filename": Path(str(upload.filename).replace("\\", "/")).name}
        try:
            if not project_id:
                project_id = store().create_project(source.get("filename") or "Uploaded source")['id']
            stream = str(source.get("ref") or ("detached:" + source['commit'] if source.get("commit") else "default"))
            profiles = await scanner_profiles()
            if profiles.get(config['profile']):
                config['profile_digests'] = {key: profiles[config['profile']].get(key) for key in ('source', 'dependency')}
            baseline_id, baseline_hash = form.get("baseline_run_id"), form.get("baseline_hash")
            if baseline_id:
                valid_id(str(baseline_id))
            if baseline_hash and not re.fullmatch(r"[0-9a-f]{64}", str(baseline_hash)):
                raise HTTPException(400, "Invalid baseline report hash")
            source.update(project_id=project_id, stream=stream,
                baseline=store().pin_baseline(project_id, stream, config, baseline_id, baseline_hash))
            job = store().create_job("scan", config, source, job_id=job_id)
        except BaseException as exc:
            if source["source"] == "zip":
                target.unlink(missing_ok=True)
            if isinstance(exc, ValueError) and not isinstance(exc, QueueFull):
                raise HTTPException(400, str(exc)) from exc
            raise
        return {"job_id": job["job_id"], "status": job["status"]}

    @app.get("/jobs", response_model=JobList)
    def jobs(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), status: str | None = None, kind: str | None = None):
        return store().list(page, limit, status, kind)

    @app.get("/jobs/{job_id}", response_model=Job)
    def get_job(job_id: str):
        job = store().get(valid_id(job_id))
        if not job:
            raise HTTPException(404, "Job not found")
        return job

    @app.delete("/jobs/{job_id}")
    def cancel(job_id: str):
        if not store().cancel(valid_id(job_id)):
            raise HTTPException(409, "Job cannot be canceled in its current state")
        return {"job_id": job_id, "status": "canceled"}

    @app.post("/jobs/{job_id}/retry", status_code=202, response_model=Submission)
    def retry(job_id: str):
        if not store().retry(valid_id(job_id)):
            raise HTTPException(409, "Only failed, partial, or interrupted runs can be retried")
        return {"job_id": job_id, "status": "queued"}

    @app.post("/jobs/{job_id}/rerun", status_code=202, response_model=Submission)
    def rerun(job_id: str, body: dict = Body(default={})):
        original = get_job(job_id)
        if original["kind"] != "scan":
            raise HTTPException(409, "Rerun the original scan or retry this review")
        source = dict(original["source"])
        source.pop("report_hash", None)
        if source.get('project_id'):
            source['baseline'] = store().pin_baseline(source['project_id'], source.get('stream', 'default'), original['config'])
        if body.get("latest"):
            if source["source"] != "github":
                raise HTTPException(400, "Scan latest requires a GitHub source")
            if source.get("ref") and re.fullmatch(r"[0-9a-fA-F]{40,64}", str(source["ref"])):
                raise HTTPException(400, "This source is pinned to a commit; submit a new scan with a branch or tag to scan its latest ref")
            for key in ("snapshot_id", "digest", "commit"):
                source.pop(key, None)
        elif not source.get("snapshot_id") or not (settings.storage / "snapshots" / source["snapshot_id"] / "manifest.json").exists():
            raise HTTPException(409, "Snapshot unavailable; submit a new scan")
        job = store().create_job("scan", original["config"], source)
        return {"job_id": job["job_id"], "status": job["status"]}

    def read_report(job_id, enhanced=False, report_hash=None):
        job_id = valid_id(job_id)
        suffix = "_enhanced" if enhanced else ""
        if report_hash and not re.fullmatch(r"[0-9a-f]{64}", report_hash):
            raise HTTPException(400, "Invalid report version hash")
        report = store().read_artifact(f"report_versions/{job_id}/{report_hash}.json" if report_hash else f"reports/{job_id}{suffix}.json")
        if not report:
            raise HTTPException(404, "Enhanced report not available" if enhanced else "Report not found")
        if enhanced and report.get("report_hash"):
            current = store().read_artifact(f"reports/{job_id}.json")
            if not current or current.get("report_hash") != report["report_hash"]:
                raise HTTPException(404, "No enhanced report exists for the current static report version")
        if report.get("schema_version") != "2.0":
            report["schema_version"] = "1.0"
            report["legacy"] = True
            if "ai_analysis" in report:
                report["ai_analysis"]["review_status"] = "unreviewed"
            for file in report.get("files", []):
                for issue in file["issues"]:
                    issue.setdefault("file", file["path"])
                    issue.setdefault("id", hashlib.sha256(json.dumps(issue, sort_keys=True).encode()).hexdigest()[:24])
        return report

    @app.get("/reports/{job_id}", response_model=ScanReport)
    def report(job_id: str, report_hash: str | None = None):
        return read_report(job_id, report_hash=report_hash)

    @app.get("/reports/{job_id}/summary")
    def summary(job_id: str):
        return {"job_id": job_id, "summary": read_report(job_id)["summary"]}

    @app.get("/reports/{job_id}/enhanced", response_model=ScanReport)
    def enhanced(job_id: str):
        return read_report(job_id, True)

    @app.get("/reviews/{run_id}", response_model=ScanReport)
    def review_report(run_id: str):
        valid_id(run_id)
        artifact = store().read_artifact(f"reviews/{run_id}.json")
        if artifact is None:
            raise HTTPException(404, "Review artifact is not available; inspect the run's saved steps")
        return artifact

    @app.post("/reports/{job_id}/enhance", status_code=202, response_model=Submission)
    async def enhance(job_id: str, body: dict = Body(default={})):
        source_report = read_report(job_id)
        scan = store().get(job_id)
        if not scan or not scan["source"].get("snapshot_id"):
            raise HTTPException(409, "Historical report has no source snapshot; submit a new scan")
        if scan["status"] not in ("completed", "partial"):
            raise HTTPException(409, "Wait for a successful or partial static scan")
        if not (settings.storage / "snapshots" / scan["source"]["snapshot_id"] / "manifest.json").is_file():
            raise HTTPException(409, "Source snapshot expired; submit a new scan")
        config = validate_review(body)
        await ensure_provider(config)
        try:
            job = store().create_review(job_id, config)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        return {"job_id": job["job_id"], "run_id": job["job_id"], "status": job["status"]}

    def report_items():
        items = []
        for path in (settings.storage / "reports").glob("*.json"):
            if path.name.endswith("_enhanced.json"):
                continue
            try:
                data = json.loads(path.read_text())
                items.append({"job_id": data["job_id"], "repo_url": data["meta"]["repo"].get("url"),
                    "generated_at": data["meta"]["generated_at"], "summary": data["summary"],
                    "tools": data["meta"].get("tools", []), "labels": data["meta"].get("labels", []),
                    "status": data.get("status", "completed")})
            except (ValueError, KeyError):
                continue
        return sorted(items, key=lambda item: item["generated_at"], reverse=True)

    @app.get("/reports")
    def reports(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), severity: str | None = None,
                tool: str | None = None, repo: str | None = None, label: str | None = None,
                since: str | None = None, until: str | None = None):
        items = [item for item in report_items() if
            (not severity or item["summary"].get(severity, 0)) and (not tool or tool in item["tools"]) and
            (not repo or repo.lower() in (item["repo_url"] or "").lower()) and (not label or label in item["labels"]) and
            (not since or item["generated_at"] >= since) and (not until or item["generated_at"] <= until)]
        return {"items": items[(page - 1) * limit:page * limit], "total": len(items), "page": page, "limit": limit}

    @app.get("/dashboard/stats")
    def stats():
        items = report_items()
        return {"total_scans": len(items), "ai_enhanced_reports": len(list((settings.storage / "reports").glob("*_enhanced.json"))),
            "severity_distribution": {severity: sum(item["summary"].get(severity, 0) for item in items)
                                      for severity in ("critical", "high", "medium", "low")},
            "active_jobs": sum(store().list(limit=1, status=status)["total"] for status in ("queued", "running")),
            "recent_scans": items[:10]}

    @app.get("/events/{job_id}")
    async def events(job_id: str, request: Request, after: int = Query(0, ge=0)):
        get_job(job_id)
        try:
            cursor = max(after, int(request.headers.get("last-event-id", "0")))
        except ValueError:
            raise HTTPException(400, "Invalid event cursor")

        async def stream():
            nonlocal cursor
            yield f"event: snapshot\ndata: {json.dumps(store().get(job_id))}\n\n"
            idle = 0
            while not await request.is_disconnected():
                batch = store().events(job_id, cursor)
                for event in batch:
                    cursor = event["seq"]
                    yield f"id: {cursor}\nevent: update\ndata: {json.dumps(event)}\n\n"
                current = store().get(job_id)
                child = store().get(current["latest_review_id"]) if current.get("latest_review_id") else None
                if current["status"] in TERMINAL and (not child or child["status"] in TERMINAL) and not batch:
                    break
                idle += 1
                if idle % 15 == 0:
                    yield ": heartbeat\n\n"
                await asyncio.sleep(1)
        return StreamingResponse(stream(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    from api.project_routes import register_routes
    register_routes(app, store, read_report, review_report, valid_id, settings)
    return app


app = create_app()
