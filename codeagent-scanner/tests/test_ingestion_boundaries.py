"""Cross-component regressions for source identity and scanner reservation."""
import asyncio
import hashlib
import json
import threading
import time
import uuid
import zipfile

import httpx
import pytest

from ingestion.snapshots import build_snapshot, verify_snapshot
from settings import Settings


def settings_for(path):
    settings = Settings(storage=path, team_mode=False)
    settings.prepare()
    return settings


def test_zip_filters_preserve_user_root_but_github_wrapper_is_removed(tmp_path):
    settings = settings_for(tmp_path)
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("src/a.py", "print(1)")
        stream.writestr("src/b.py", "print(2)")
    included = build_snapshot(archive, "included", settings, {"source": "zip"}, {"include": ["src/**"]})
    excluded = build_snapshot(archive, "excluded", settings, {"source": "zip"}, {"exclude": ["src/**"]})
    assert set(included["files"]) == {"src/a.py", "src/b.py"}
    assert excluded["files"] == {}
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("owner-repo-commit/src/a.py", "print(1)")
    github = build_snapshot(archive, "github", settings, {"source": "github"}, {"include": ["src/**"]})
    assert set(github["files"]) == {"src/a.py"}


def test_utf16_and_unsupported_binary_lock_keep_original_hashes(tmp_path):
    settings = settings_for(tmp_path)
    contents = {"Example.cs": "using System.Security.Cryptography; class Example { object Make() => MD5.Create(); }".encode("utf-16"),
        "bun.lockb": b"binary\0unsupported"}
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        for path, data in contents.items():
            stream.writestr(path, data)
    manifest = build_snapshot(archive, "snapshot", settings, {"source": "zip"}, {})
    root = settings.storage / "snapshots/snapshot/source"
    assert set(manifest["files"]) == set(contents)
    for path, data in contents.items():
        assert (root / path).read_bytes() == data
        assert manifest["files"][path] == hashlib.sha256(data).hexdigest()
    assert any("UTF-16" in warning and "Example.cs" in warning for warning in manifest["warnings"])
    verify_snapshot(root, manifest)


def scanner_case(tmp_path, monkeypatch):
    import api.scanner as scanner
    job_id = str(uuid.uuid4())
    source = tmp_path / job_id
    (source / "source").mkdir(parents=True)
    (source / "manifest.json").write_text(json.dumps({"files": {}}))
    monkeypatch.setenv("SNAPSHOT_ROOT", str(tmp_path))
    return scanner, {"job_id": job_id, "snapshot_id": job_id, "analyzers": ["semgrep"]}


@pytest.mark.asyncio
async def test_scanner_reserves_before_awaiting_snapshot_verification(tmp_path, monkeypatch):
    import analyzers.service as service
    scanner, body = scanner_case(tmp_path, monkeypatch)
    entered, release = threading.Event(), threading.Event()
    def verify(*_):
        entered.set()
        assert release.wait(5)
    monkeypatch.setattr(scanner, "verify_snapshot", verify)
    monkeypatch.setattr(service, "scan_workspace", lambda *args, **kw: {"status": "completed", "files": []})
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=scanner.app), base_url="http://scanner") as client:
        first = asyncio.create_task(client.post("/scan", json=body))
        try:
            assert await asyncio.to_thread(entered.wait, 5)
            duplicate = await client.post("/scan", json=body)
            assert duplicate.status_code == 409
        finally:
            release.set()
        assert (await first).status_code == 200
    assert body["job_id"] not in scanner.active


@pytest.mark.asyncio
async def test_scanner_cleanup_survives_cancelled_request_and_analyzer_error(tmp_path, monkeypatch):
    import analyzers.service as service
    from analyzers.base import AnalysisCancelled
    scanner, body = scanner_case(tmp_path, monkeypatch)
    started = threading.Event()
    monkeypatch.setattr(scanner, "verify_snapshot", lambda *_: None)
    def scan(*args, cancel, **kwargs):
        started.set()
        while not cancel():
            time.sleep(.01)
        raise AnalysisCancelled("Cancelled analyzer")
    monkeypatch.setattr(service, "scan_workspace", scan)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=scanner.app), base_url="http://scanner") as client:
        request = asyncio.create_task(client.post("/scan", json=body))
        assert await asyncio.to_thread(started.wait, 5)
        request.cancel()
        with pytest.raises((asyncio.CancelledError, AnalysisCancelled)):
            await request
    assert body["job_id"] not in scanner.active
