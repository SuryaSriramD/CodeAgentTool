import io
import json
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from ingestion.snapshots import SourceCanceled, SourceError, build_snapshot, extract_zip, fetch_github_archive, verify_snapshot
from pipeline.orchestrator import JobOrchestrator
from pipeline.store import Store
from settings import Settings


@pytest.fixture
def settings(tmp_path):
    settings = Settings(storage=tmp_path, openai_key="", github_token="", workspace_password="", session_secret="", team_mode=False)
    settings.prepare()
    return settings


def archive(files=None):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as zipped:
        for name, value in (files or {"main.py": "import os\nos.system(input())\n"}).items():
            zipped.writestr(name, value)
    return data.getvalue()


def fake_scan(path, **kwargs):
    return {"tools": ["fixture-scanner"], "status": "completed",
        "summary": {"critical": 0, "high": 1, "medium": 0, "low": 0},
        "coverage": [{"tool": "fixture-scanner", "status": "succeeded", "files_scanned": 1, "files_discovered": 1, "errors": []}],
        "files": [{"path": "main.py", "issues": [{"tool": "fixture-scanner", "type": "command-injection", "message": "Untrusted shell command",
            "severity": "high", "file": "main.py", "line": 2, "rule_id": "test.command"}]}]}


def test_zip_scan_report_rerun_and_events(settings):
    with TestClient(create_app(settings)) as client:
        submitted = client.post("/analyze", files={"file": ("example.zip", archive(), "application/zip")})
        assert submitted.status_code == 202
        job_id = submitted.json()["job_id"]
        assert client.get("/jobs?status=queued").json()["total"] == 1
        assert client.get(f"/reports/{job_id}").status_code == 404
        worker = JobOrchestrator(settings=settings, scan_fn=fake_scan)
        worker.execute(worker.store.claim("test"))
        assert client.get(f"/jobs/{job_id}").json()["status"] == "completed"
        report = client.get(f"/reports/{job_id}").json()
        issue = report["files"][0]["issues"][0]
        assert issue["id"] and issue["source_hash"]
        assert report["meta"]["snapshot"]["files"]["main.py"] == issue["source_hash"]
        replay = client.get(f"/events/{job_id}", headers={"Last-Event-ID": "1"}).text
        assert "event: snapshot" in replay and "event: update" in replay
        assert "id: 1\n" not in replay
        rerun = client.post(f"/jobs/{job_id}/rerun", json={"latest": False})
        assert rerun.status_code == 202
        worker.execute(worker.store.claim("test"))
        assert client.get(f"/reports/{rerun.json()['job_id']}").json()["files"][0]["issues"][0]["id"] == issue["id"]


def test_cancel_cannot_be_overwritten(settings):
    store = Store(settings.storage)
    job = store.create_job("scan", {}, {"source": "zip"})
    store.claim("test")
    assert store.cancel(job["job_id"])
    assert not store.finish(job["job_id"], "completed")
    assert store.get(job["job_id"])["status"] == "canceled"


def test_transactional_claim_limits_and_review_dedup(settings):
    store = Store(settings.storage)
    for _ in range(8):
        store.create_job("scan", {}, {"source": "zip"})
    with ThreadPoolExecutor(max_workers=8) as pool:
        claims = list(pool.map(lambda n: store.claim(str(n), max_scans=2), range(8)))
    assert sum(bool(job) for job in claims) == 2
    parent = next(job["job_id"] for job in claims if job)
    with ThreadPoolExecutor(max_workers=8) as pool:
        reviews = list(pool.map(lambda _: store.create_job("review", {"provider": "ollama", "model": "x"}, {}, parent), range(8)))
    assert len({review["job_id"] for review in reviews}) == 1
    review = store.claim("local1")
    store.create_job("review", {"provider": "ollama", "model": "x"}, {}, "other-parent")
    assert review["kind"] == "review"
    assert store.claim("local2") is None


def test_recovery_retains_completed_steps_and_requires_explicit_retry(settings):
    store = Store(settings.storage)
    scan = store.create_job("scan", {}, {})
    store.claim("crashed")
    review = store.create_job("review", {"provider": "ollama"}, {}, scan["job_id"])
    store.claim("crashed")
    store.save_step(review["job_id"], "analyst", {"status": "completed", "output": {"ok": True}, "usage": {"total_tokens": 17}})
    store.save_step(review["job_id"], "author", {"status": "running", "attempt": 1})
    store.release_worker("crashed")
    assert store.get(scan["job_id"])["status"] == "queued"
    assert store.get(review["job_id"])["status"] == "interrupted"
    assert store.retry(review["job_id"])
    assert store.load_step(review["job_id"], "author")["status"] == "retry_requested"
    assert store.load_step(review["job_id"], "analyst")["usage"]["total_tokens"] == 17


@pytest.mark.parametrize("name", ["../escape.py", "/escape.py", "x/../../escape.py", "C:/escape.py", "x\\escape.py"])
def test_archive_traversal_rejected(settings, name):
    source = settings.storage / "bad.zip"
    source.write_bytes(archive({name: "bad"}))
    with pytest.raises(SourceError):
        extract_zip(source, settings.storage / "out", settings)
    assert not (settings.storage / "out").exists()


def test_archive_expansion_symlink_and_duplicate_limits(settings):
    source = settings.storage / "bad.zip"
    settings.max_expanded_size = 2
    source.write_bytes(archive({"a.py": "abc"}))
    with pytest.raises(SourceError, match="MAX_EXPANDED"):
        extract_zip(source, settings.storage / "out", settings)
    settings.max_expanded_size = 10000
    with zipfile.ZipFile(source, "w") as zipped:
        link = zipfile.ZipInfo("link")
        link.create_system = 3
        link.external_attr = 0o120777 << 16
        zipped.writestr(link, "/etc/passwd")
    with pytest.raises(SourceError, match="symlink"):
        extract_zip(source, settings.storage / "out", settings)
    source.write_bytes(archive({"a.py": "x", "A.py": "y"}))
    with pytest.raises(SourceError, match="case-colliding"):
        extract_zip(source, settings.storage / "out", settings)


def test_snapshot_exclusions_and_mutation_detection(settings):
    source = settings.storage / "source.zip"
    source.write_bytes(archive({"repo/a.py": "print(1)", "repo/.env": "SECRET=hidden",
                               "repo/node_modules/x.js": "junk", "repo/.github/workflows/test.yml": "name: ci"}))
    manifest = build_snapshot(source, "test", settings, {"source": "zip"}, {})
    root = settings.storage / "snapshots/test/source"
    assert set(manifest["files"]) == {"repo/a.py", "repo/.github/workflows/test.yml"}
    verify_snapshot(root, manifest)
    (root / "repo/a.py").write_text("changed")
    with pytest.raises(SourceError, match="changed"):
        verify_snapshot(root, manifest)


def test_private_github_resolves_ref_and_never_forwards_token(settings):
    settings.github_token = "private-test-token"
    calls = []
    sha = "a" * 40
    def handler(request):
        calls.append(request)
        if request.url.host == "codeload.github.com":
            assert "authorization" not in request.headers
            return httpx.Response(200, content=archive())
        assert request.headers["authorization"] == "Bearer private-test-token"
        if "/commits/" in request.url.path:
            return httpx.Response(200, json={"sha": sha})
        return httpx.Response(302, headers={"location": "https://codeload.github.com/org/private/zip/" + sha})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        source = fetch_github_archive({"source": "github", "url": "https://github.com/org/private", "ref": "feature/fix"},
            settings.storage / "private.zip", settings, client=client)
    assert source["commit"] == sha
    assert "private-test-token" not in json.dumps(source)
    assert len(calls) == 3


def test_expired_github_token_has_no_secret_in_error(settings):
    settings.github_token = "private-test-token"
    with httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(401, text=settings.github_token))) as client:
        with pytest.raises(SourceError) as error:
            fetch_github_archive({"source": "github", "url": "https://github.com/org/private", "ref": "main"},
                settings.storage / "private.zip", settings, client=client)
    assert settings.github_token not in str(error.value)


def test_api_auth_and_cross_origin_protection(settings):
    settings.workspace_password = "correct password"
    settings.session_secret = "x" * 32
    with TestClient(create_app(settings)) as client:
        assert client.get("/jobs").status_code == 401
        assert client.get("/auth/status").json() == {"required": True, "authenticated": False}
        assert client.post("/auth/login", json={"password": "bad"}).status_code == 401
        login = client.post("/auth/login", json={"password": "correct password"})
        assert login.status_code == 200 and "HttpOnly" in login.headers["set-cookie"]
        assert client.get("/jobs").status_code == 200
        assert client.post("/analyze", headers={"Origin": "https://evil.example"}).status_code == 403
        client.post("/auth/logout")
        assert client.get("/jobs").status_code == 401


def test_team_mode_requires_credentials(settings):
    settings.team_mode = True
    with pytest.raises(ValueError, match="WORKSPACE_PASSWORD"):
        settings.prepare()


def test_invalid_inputs_and_report_filters(settings):
    with TestClient(create_app(settings)) as client:
        assert client.post("/analyze").status_code == 400
        assert client.post("/analyze", data={"github_url": "https://token@github.com/org/repo"}).status_code == 400
        assert client.post("/analyze", data={"github_url": "https://github.com/org/repo", "mode": "invalid"}).status_code == 400
        assert client.get("/jobs?limit=0").status_code == 422
        assert client.patch("/config/ai", json={"api_key": "should-not-store"}).status_code == 400
        assert client.patch("/config/ai", json={"model": "GPT_4"}).status_code == 400
        assert client.patch("/config/ai", json={"provider": "ollama", "model": "local-model:latest"}).status_code == 200


def test_legacy_report_readable_and_not_duplicated(settings):
    store = Store(settings.storage)
    legacy = {"job_id": "old", "meta": {"repo": {"source": "zip"}, "generated_at": "2025-01-01", "tools": [], "labels": []},
              "summary": {"critical": 0, "high": 0, "medium": 0, "low": 0}, "files": []}
    store.write_artifact("reports/old.json", legacy)
    store.write_artifact("reports/old_enhanced.json", {**legacy, "ai_analysis": {"fixes": []}})
    with TestClient(create_app(settings)) as client:
        assert client.get("/reports").json()["total"] == 1
        assert client.get("/reports/old/enhanced").json()["ai_analysis"]["review_status"] == "unreviewed"
        assert client.post("/reports/old/enhance").status_code == 409


def test_restart_reuses_completed_analyzers(settings):
    calls = []
    def scan(path, **kwargs):
        name = kwargs["analyzers"][0]
        calls.append(name)
        if calls == ["semgrep", "bandit"]:
            raise SourceCanceled("Simulated worker shutdown")
        return {**fake_scan(path), "tools": [name], "coverage": [{"tool": name, "status": "completed"}]}
    store = Store(settings.storage)
    job = store.create_job("scan", {"analyzers": ["semgrep", "bandit"]}, {"source": "zip"})
    (settings.storage / "uploads" / (job["job_id"] + ".zip")).write_bytes(archive())
    worker = JobOrchestrator(settings=settings, scan_fn=scan)
    worker.execute(store.claim("first"))
    assert store.load_step(job["job_id"], "scanner:semgrep")["status"] == "completed"
    store.release_worker("first")
    worker.execute(store.claim("restarted"))
    assert calls == ["semgrep", "bandit", "bandit"]
    assert store.get(job["job_id"])["status"] == "completed"
    assert store.read_artifact(f"reports/{job['job_id']}.json")["summary"]["high"] == 1


def test_expired_or_canceled_worker_cannot_publish(settings):
    store = Store(settings.storage)
    job = store.create_job("scan", {}, {})
    stale = store.claim("stale", lease_sec=-1)["_lease_owner"]
    assert not store.save_step(job["job_id"], "late", {"status": "completed"}, owner=stale)
    assert not store.finish(job["job_id"], "completed", owner=stale)
    assert not store.write_run_artifact(job["job_id"], "reports/late.json", {}, owner=stale)
    store.recover()
    fresh = store.claim("fresh")["_lease_owner"]
    assert not store.finish(job["job_id"], "completed", owner=stale)
    store.cancel(job["job_id"])
    assert not store.write_run_artifact(job["job_id"], "reports/late.json", {}, owner=fresh)
    assert not (settings.storage / "reports/late.json").exists()


def test_static_completion_and_requested_review_are_atomic(settings):
    store = Store(settings.storage)
    job = store.create_job("scan", {}, {})
    owner = store.claim("worker")["_lease_owner"]
    config = {"provider": "ollama", "model": "fixture"}
    assert store.finish(job["job_id"], "completed", review_config=config, source={"snapshot_id": job["job_id"]}, owner=owner)
    child = store.get(store.get(job["job_id"])["latest_review_id"])
    assert child["kind"] == "review" and child["status"] == "queued" and child["config"] == config
    assert not store.finish(job["job_id"], "completed", review_config=config, owner=owner)
    assert store.list(kind="review")["total"] == 1
    assert any(e["data"].get("run_id") == child["job_id"] for e in store.events(job["job_id"]))


def test_worker_cancellation_stops_scheduling_and_shutdown_recovers(settings):
    from worker import Worker
    started, stopped = threading.Event(), threading.Event()
    calls = []
    def waiting_scanner(path, **kwargs):
        calls.append(kwargs["analyzers"][0])
        started.set()
        while not kwargs["cancel"]():
            time.sleep(0.02)
        stopped.set()
        raise SourceCanceled("Canceled scanner")
    store = Store(settings.storage)
    job = store.create_job("scan", {"analyzers": ["semgrep", "bandit"]}, {"source": "zip"})
    (settings.storage / "uploads" / (job["job_id"] + ".zip")).write_bytes(archive())
    worker = Worker(settings, scan_fn=waiting_scanner)
    thread = threading.Thread(target=worker.run)
    thread.start()
    try:
        assert started.wait(5)
        store.cancel(job["job_id"])
        assert stopped.wait(5)
        assert calls == ["semgrep"]
        assert store.get(job["job_id"])["status"] == "canceled"
    finally:
        worker.stop.set()
        thread.join(timeout=5)
    assert not thread.is_alive()


def test_upload_and_archive_file_count_limits(settings):
    settings.max_upload_size = 10
    settings.max_files = 1
    with TestClient(create_app(settings)) as client:
        response = client.post("/analyze", files={"file": ("large.zip", archive(), "application/zip")})
        assert response.status_code == 413
        assert client.get("/jobs").json()["total"] == 0
        assert not list((settings.storage / "uploads").glob("*.zip"))
    source = settings.storage / "too-many.zip"
    source.write_bytes(archive({"a.py": "x", "b.py": "y"}))
    with pytest.raises(SourceError, match="MAX_FILES"):
        extract_zip(source, settings.storage / "out", settings)


def test_review_artifact_version_is_retrievable(settings):
    store = Store(settings.storage)
    for version in ("review1", "review2"):
        store.write_artifact(f"reviews/{version}.json", {"job_id": "scan", "review_run_id": version,
            "schema_version": "2.0", "meta": {}, "summary": {}, "files": [], "ai_analysis": {"model": version}})
    with TestClient(create_app(settings)) as client:
        for version in ("review1", "review2"):
            report = client.get(f"/reviews/{version}").json()
            assert report["review_run_id"] == version and report["ai_analysis"]["model"] == version


def test_retention_keeps_active_snapshot_and_completed_review_metadata(settings):
    from pipeline.retention import cleanup
    store = Store(settings.storage)
    old = store.create_job("scan", {}, {"snapshot_id": "snapshot"})
    store.claim("test")
    store.finish(old["job_id"], "completed")
    store.write_artifact(f"reports/{old['job_id']}.json", {"source": "expired"})
    root = settings.storage / "snapshots/snapshot"
    root.mkdir()
    (root / "data.py").write_text("private source")
    import os
    os.utime(root, (1, 1))
    with store.connect(write=True) as db:
        db.execute("UPDATE jobs SET submitted_at='2020-01-01T00:00:00+00:00' WHERE job_id=?", (old["job_id"],))
    review = store.create_job("review", {"provider": "ollama"}, {"snapshot_id": "snapshot"}, old["job_id"])
    cleanup(store, settings)
    assert root.exists()  # Queued child still needs its parent's snapshot.
    assert (settings.storage / "reports" / (old["job_id"] + ".json")).exists()
    store.cancel(review["job_id"])
    cleanup(store, settings)
    assert not (settings.storage / "reports" / (old["job_id"] + ".json")).exists()
    assert store.get(old["job_id"])["status"] == "completed"


def test_failed_applicable_tool_is_not_clean_when_other_tools_skip(settings):
    def unavailable(path, **kwargs):
        name = kwargs["analyzers"][0]
        status = "failed" if name == "semgrep" else "skipped"
        return {"tools": [name], "status": "failed" if status == "failed" else "partial",
            "coverage": [{"tool": name, "status": status, "errors": ["Tool unavailable"] if status == "failed" else []}]}
    store = Store(settings.storage)
    job = store.create_job("scan", {}, {"source": "zip"})
    (settings.storage / "uploads" / (job["job_id"] + ".zip")).write_bytes(archive())
    JobOrchestrator(settings=settings, scan_fn=unavailable).execute(store.claim("test"))
    assert store.get(job["job_id"])["status"] == "failed"


def test_queue_capacity_is_atomic_under_concurrent_submissions(settings):
    from pipeline.store import QueueFull
    store = Store(settings.storage)
    for _ in range(98):
        store.create_job("scan", {}, {})
    def submit(_):
        try:
            return store.create_job("scan", {}, {})
        except QueueFull:
            return None
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(submit, range(8)))
    assert sum(item is not None for item in results) == 2
    assert store.list(status="queued")["total"] == 100


def test_streamed_request_is_bounded_before_multipart_spooling(settings):
    settings.max_upload_size = 10
    with TestClient(create_app(settings)) as client:
        # No Content-Length: the receive wrapper must enforce the limit itself.
        response = client.post("/auth/login", content=iter([b'{"password":"', b'x' * (1024 * 1024 + 100), b'"}']),
            headers={"Content-Type": "application/json"})
        assert response.status_code == 413
        assert client.post("/auth/login", content="not-json").status_code == 400


def test_readiness_does_not_offer_embedding_models_for_review(settings, monkeypatch):
    real_client = httpx.AsyncClient
    seen = []
    def handler(request):
        seen.append(str(request.url))
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "text-model"}, {"name": "embedding-model"}]})
        assert request.url.path == "/api/show"
        model = json.loads(request.content)["model"]
        return httpx.Response(200, json={"capabilities": ["completion" if model == "text-model" else "embedding"]})
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real_client(**kw, transport=httpx.MockTransport(handler)))
    with TestClient(create_app(settings)) as client:
        provider = client.get("/capabilities").json()["providers"]["ollama"]
        assert provider["available"] and provider["models"] == ["text-model"]
        assert provider["excluded_models"] == ["embedding-model"]
        assert all(url.startswith(settings.ollama_url) for url in seen)


def test_scan_latest_resolves_branch_again_instead_of_reusing_commit(settings):
    store = Store(settings.storage)
    source = {"source": "github", "url": "https://github.com/org/repo", "ref": "main",
        "commit": "a" * 40, "snapshot_id": "old-snapshot", "digest": "old-digest"}
    job = store.create_job("scan", {"mode": "static"}, source)
    with TestClient(create_app(settings)) as client:
        response = client.post(f"/jobs/{job['job_id']}/rerun", json={"latest": True})
        assert response.status_code == 202
        created = store.get(response.json()["job_id"])
        assert created["source"] == {"source": "github", "url": source["url"], "ref": "main"}
        pinned = store.create_job("scan", {}, {**source, "ref": source["commit"]})
        assert client.post(f"/jobs/{pinned['job_id']}/rerun", json={"latest": True}).status_code == 400


def test_interrupted_review_publishes_partial_artifact_and_preserves_steps(settings, monkeypatch):
    import integration.workflow as workflow
    settings.github_token = "configured-secret-canary"
    store = Store(settings.storage)
    scan = store.create_job("scan", {"analyzers": ["semgrep"]}, {"source": "zip"})
    (settings.storage / "uploads" / (scan["job_id"] + ".zip")).write_bytes(archive())
    worker = JobOrchestrator(settings=settings, scan_fn=fake_scan)
    worker.execute(store.claim("test"))
    parent = store.get(scan["job_id"])
    review = store.create_job("review", {"provider": "ollama", "model": "fixture-model"}, parent["source"], parent["job_id"])
    async def interrupted(report, path, config, *, on_step, **kwargs):
        assert settings.github_token in config["_sensitive_values"]
        on_step("finding:one:analyst:0", {"role": "analyst", "status": "completed", "output": {"explanation": settings.github_token}})
        error = workflow.ReviewInterrupted("Transport interrupted")
        error.partial_result = {"status": "interrupted", "triage": [], "proposals": [],
            "errors": [{"message": "Transport interrupted"}], "provider": "ollama", "model": "fixture-model"}
        raise error
    monkeypatch.setattr(workflow, "run_review", interrupted)
    worker.execute(store.claim("test"))
    saved = store.get(review["job_id"])
    assert saved["status"] == "interrupted"
    assert saved["steps"][0]["output"]["explanation"] == "[redacted]"
    with TestClient(create_app(settings)) as client:
        artifact = client.get(f"/reviews/{review['job_id']}")
        assert artifact.status_code == 200
        assert artifact.json()["ai_analysis"]["status"] == "interrupted"
        assert artifact.json()["review_run_id"] == review["job_id"]
        assert settings.github_token not in json.dumps(saved) + artifact.text
        assert client.post(f"/jobs/{review['job_id']}/retry").status_code == 202
        assert store.load_step(review["job_id"], "finding:one:analyst:0")["status"] == "completed"
