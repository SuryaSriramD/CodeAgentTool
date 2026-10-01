"""Regression checks for lease fencing, frozen report inputs, and credential sinks."""
import io
import json
import os
import sqlite3
import time
import zipfile

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from pipeline.orchestrator import JobOrchestrator, redact
from pipeline.retention import cleanup
from pipeline.store import Store
from settings import Settings


@pytest.fixture
def settings(tmp_path):
    value = Settings(storage=tmp_path, openai_key="server-test-key", github_token="", workspace_password="", session_secret="", team_mode=False)
    value.prepare()
    return value


def report(scan_id, message):
    return {"schema_version": "2.0", "job_id": scan_id, "meta": {"repo": {}}, "summary": {"high": 1},
            "files": [{"path": "main.py", "issues": [{"id": message, "tool": "fixture", "type": "command", "message": message,
                "file": "main.py", "line": 2, "rule_id": "test", "severity": "high"}]}]}


def publish_scan(store, job, message, status="partial", worker="scanner"):
    claim = store.claim(worker)
    assert claim["job_id"] == job["job_id"]
    digest = store.publish_scan_report(job["job_id"], report(job["job_id"], message), claim["_lease_owner"])
    assert store.finish(job["job_id"], status, owner=claim["_lease_owner"])
    return digest


def test_same_worker_reclaim_fences_every_old_mutation(settings):
    store = Store(settings.storage)
    job = store.create_job("scan", {}, {"source": "zip"})
    old = store.claim("same-worker", lease_sec=-1)
    store.recover()
    current = store.claim("same-worker")
    assert old["_lease_owner"] != current["_lease_owner"]
    stale = old["_lease_owner"]
    assert not store.owns(job["job_id"], stale)
    assert not store.save_step(job["job_id"], "late", {"status": "completed"}, owner=stale)
    assert not store.progress(job["job_id"], "late", 100, owner=stale)
    assert not store.set_source(job["job_id"], {"bad": True}, owner=stale)
    assert not store.publish_scan_report(job["job_id"], report(job["job_id"], "late"), stale)
    assert not store.write_run_artifact(job["job_id"], "reports/late.json", {}, stale)
    assert not store.finish(job["job_id"], "completed", owner=stale)
    store.heartbeat("same-worker", 60)
    assert store.owns(job["job_id"], current["_lease_owner"])
    assert store.get(job["job_id"])["source"] == {"source": "zip"}
    assert "lease_worker" not in store.get(job["job_id"])
    store.release_worker("same-worker")
    assert store.get(job["job_id"])["status"] == "queued"


def test_legacy_database_migrates_worker_identity_without_reusing_claim_token(settings):
    path = settings.storage / "codeagent.sqlite3"
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE jobs (job_id TEXT PRIMARY KEY,kind TEXT NOT NULL,parent_job_id TEXT,
            status TEXT NOT NULL,config TEXT NOT NULL,config_hash TEXT NOT NULL,source TEXT NOT NULL,
            progress TEXT,submitted_at TEXT NOT NULL,started_at TEXT,finished_at TEXT,error TEXT,
            lease_owner TEXT,lease_until REAL,cancel_requested INTEGER NOT NULL DEFAULT 0)""")
        db.execute("""INSERT INTO jobs(job_id,kind,status,config,config_hash,source,submitted_at,lease_owner,lease_until)
            VALUES('legacy','scan','running','{}','hash','{}','2026-01-01T00:00:00+00:00','old-worker',?)""", (time.time() + 30,))
    store = Store(settings.storage)
    store.heartbeat("old-worker")
    assert store.owns("legacy", "old-worker")  # Only the already-existing claim uses the legacy token.
    store.release_worker("old-worker")
    claim = store.claim("old-worker")
    assert claim["_lease_owner"] != "old-worker" and not store.owns("legacy", "old-worker")
    Store(settings.storage)  # Migration is idempotent.


def test_report_retry_changes_review_identity_and_preserves_frozen_input(settings):
    store = Store(settings.storage)
    scan = store.create_job("scan", {}, {"source": "zip", "snapshot_id": "source"})
    first_hash = publish_scan(store, scan, "first")
    config = {"provider": "ollama", "model": "model"}
    review1 = store.create_review(scan["job_id"], config)
    claim1 = store.claim("worker")
    old_input, _ = store.review_input(review1["job_id"], claim1["_lease_owner"])
    assert old_input["report_hash"] == first_hash
    assert store.finish(review1["job_id"], "completed", owner=claim1["_lease_owner"])
    assert store.create_review(scan["job_id"], config)["job_id"] == review1["job_id"]
    assert store.retry(scan["job_id"])
    second_hash = publish_scan(store, scan, "additional-finding", status="completed")
    review2 = store.create_review(scan["job_id"], config)
    assert review2["job_id"] != review1["job_id"] and second_hash != first_hash
    assert review2["source"]["report_hash"] == second_hash
    assert store.read_artifact(f"report_versions/{scan['job_id']}/{first_hash}.json")["files"][0]["issues"][0]["message"] == "first"
    assert store.get(scan["job_id"])["latest_review_id"] == review2["job_id"]


def test_old_review_cannot_publish_as_latest_after_static_version_changes(settings):
    store = Store(settings.storage)
    scan = store.create_job("scan", {}, {"source": "zip"})
    publish_scan(store, scan, "old")
    review1 = store.create_review(scan["job_id"], {"provider": "ollama", "model": "one"})
    old = store.claim("old-reviewer")
    old_report, _ = store.review_input(old["job_id"], old["_lease_owner"])
    store.retry(scan["job_id"])
    publish_scan(store, scan, "new", status="completed")
    assert store.get(scan["job_id"])["latest_review_id"] is None
    assert store.publish_review(old["job_id"], {**old_report, "review_run_id": old["job_id"]}, old["_lease_owner"])
    assert store.read_artifact(f"reviews/{old['job_id']}.json")
    assert store.read_artifact(f"reports/{scan['job_id']}_enhanced.json") is None


def test_old_retry_cannot_replace_newer_review_for_same_report(settings):
    store = Store(settings.storage)
    scan = store.create_job("scan", {}, {})
    publish_scan(store, scan, "same", status="completed")
    first = store.create_review(scan["job_id"], {"provider": "ollama", "model": "one"})
    old_claim = store.claim("worker")
    old_report, _ = store.review_input(first["job_id"], old_claim["_lease_owner"])
    store.finish(first["job_id"], "partial", owner=old_claim["_lease_owner"])
    second = store.create_review(scan["job_id"], {"provider": "ollama", "model": "two"})
    new_claim = store.claim("worker")
    latest = {**old_report, "review_run_id": second["job_id"]}
    store.publish_review(second["job_id"], latest, new_claim["_lease_owner"])
    store.finish(second["job_id"], "completed", owner=new_claim["_lease_owner"])
    store.retry(first["job_id"])
    retried = store.claim("worker")
    assert store.publish_review(first["job_id"], {**old_report, "review_run_id": first["job_id"]}, retried["_lease_owner"])
    assert store.read_artifact(f"reports/{scan['job_id']}_enhanced.json")["review_run_id"] == second["job_id"]


def test_missing_pinned_version_never_falls_back_to_newer_report(settings):
    store = Store(settings.storage)
    scan = store.create_job("scan", {}, {})
    digest = publish_scan(store, scan, "original", status="completed")
    review = store.create_review(scan["job_id"], {"provider": "ollama", "model": "one"})
    claim = store.claim("worker")
    (settings.storage / f"report_versions/{scan['job_id']}/{digest}.json").unlink()
    store.write_artifact(f"reports/{scan['job_id']}.json", report(scan["job_id"], "different"))
    value, source = store.review_input(review["job_id"], claim["_lease_owner"])
    assert value is None and source["report_hash"] == digest


@pytest.mark.parametrize("status", ["queued", "interrupted"])
def test_retention_preserves_pinned_version_for_pending_reviews(settings, status):
    store = Store(settings.storage)
    scan = store.create_job("scan", {}, {"snapshot_id": "source"})
    digest = publish_scan(store, scan, "retained", status="completed")
    review = store.create_review(scan["job_id"], {"provider": "ollama", "model": "one"})
    root = settings.storage / "snapshots/source"
    root.mkdir()
    (root / "main.py").write_text("source")
    version_dir = settings.storage / f"report_versions/{scan['job_id']}"
    os.utime(root, (1, 1)); os.utime(version_dir, (1, 1))
    with store.connect(write=True) as db:
        db.execute("UPDATE jobs SET submitted_at='2020-01-01T00:00:00+00:00'")
        db.execute("UPDATE jobs SET status=? WHERE job_id=?", (status, review["job_id"]))
    cleanup(store, settings)
    assert (version_dir / f"{digest}.json").is_file() and root.is_dir()
    store.cancel(review["job_id"])
    cleanup(store, settings)
    assert not version_dir.exists()


def test_api_enhance_freezes_current_report_and_deduplicates_that_version(settings):
    store = Store(settings.storage)
    scan = store.create_job("scan", {}, {"source": "zip", "snapshot_id": "source"})
    root = settings.storage / "snapshots/source"
    root.mkdir(); (root / "manifest.json").write_text("{}")
    publish_scan(store, scan, "one")
    config = {"provider": "openai", "model": "test-model"}
    with TestClient(create_app(settings)) as client:
        response = client.post(f"/reports/{scan['job_id']}/enhance", json=config)
        assert response.status_code == 202
        old_id = response.json()["job_id"]
        claim = store.claim("worker")
        store.finish(old_id, "completed", owner=claim["_lease_owner"])
        assert client.post(f"/reports/{scan['job_id']}/enhance", json=config).json()["job_id"] == old_id
        store.retry(scan["job_id"]); publish_scan(store, scan, "two", status="completed")
        changed = client.post(f"/reports/{scan['job_id']}/enhance", json=config)
        assert changed.status_code == 202 and changed.json()["job_id"] != old_id


def test_orchestrator_uses_frozen_report_and_masks_keys_and_terminal_errors(settings, monkeypatch):
    import integration.workflow as workflow
    secret = "credential-canary-54102"
    settings.github_token = secret
    store = Store(settings.storage)
    scan = store.create_job("scan", {"analyzers": ["semgrep"]}, {"source": "zip"})
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as zipped:
        zipped.writestr("main.py", "import os\nos.system(input())\n")
    (settings.storage / "uploads" / f"{scan['job_id']}.zip").write_bytes(data.getvalue())
    def scanner(path, **kwargs):
        return {**report(scan["job_id"], "frozen-message"), "status": "completed", "tools": ["semgrep"],
                "coverage": [{"tool": "semgrep", "status": "completed"}]}
    worker = JobOrchestrator(settings=settings, scan_fn=scanner)
    worker.execute(store.claim("scanner"))
    review = store.create_review(scan["job_id"], {"provider": "ollama", "model": "fake"})
    store.write_artifact(f"reports/{scan['job_id']}.json", report(scan["job_id"], "mutable-newer-message"))
    async def check_input(report_value, *args, **kwargs):
        assert report_value["files"][0]["issues"][0]["message"] == "frozen-message"
        return {"status": "partial", "triage": [], "proposals": [], "errors": [{"message": secret}],
                "metadata": {secret: {"nested": secret}}}
    monkeypatch.setattr(workflow, "run_review", check_input)
    worker.execute(store.claim("reviewer"))
    job = store.get(review["job_id"])
    assert job["status"] == "partial" and secret not in json.dumps(job)
    artifact = store.read_artifact(f"reviews/{review['job_id']}.json")
    assert secret not in json.dumps(artifact) and "[redacted]" in artifact["ai_analysis"]["metadata"]
    assert secret not in json.dumps(redact({"meta": {"files": {secret + ".py": "hash"}}}, settings))
