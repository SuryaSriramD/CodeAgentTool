"""Exercise reclaimed scan overlap through the real internal ASGI boundary."""
import asyncio
import json
import threading
import uuid

import httpx
import pytest

from ingestion.snapshots import SourceCanceled
from pipeline.orchestrator import remote_scan
from pipeline.store import Store


@pytest.mark.asyncio
async def test_reclaimed_dispatch_does_not_conflict_or_receive_stale_cancellation(tmp_path, monkeypatch):
    import analyzers.service as service
    import api.scanner as scanner

    store = Store(tmp_path / 'data')
    durable = store.create_job('scan', {'timeout_sec': 10, 'profile': 'security-v2'}, {'source': 'zip'})
    snapshot_id = durable['job_id']
    snapshot = tmp_path / 'snapshots' / snapshot_id
    (snapshot / 'source').mkdir(parents=True)
    (snapshot / 'manifest.json').write_text(json.dumps({'files': {}}))
    monkeypatch.setenv('SNAPSHOT_ROOT', str(tmp_path / 'snapshots'))
    monkeypatch.setenv('SCANNER_URL', 'http://scanner')
    monkeypatch.setattr(scanner, 'active', {})
    monkeypatch.setattr(scanner, 'slots', asyncio.Semaphore(2))

    first_started, second_started = threading.Event(), threading.Event()
    first_stopped, second_released, abort = threading.Event(), threading.Event(), threading.Event()
    calls, requests = [], []
    lock = threading.Lock()

    def scan(path, *, cancel, analyzers, profile, timeout_sec):
        with lock:
            index = len(calls)
            calls.append(cancel)
        assert analyzers == ['semgrep'] and profile == 'security-v2'
        if index == 0:
            first_started.set()
            while not cancel() and not abort.wait(.01):
                pass
            first_stopped.set()
            return {'status': 'completed', 'attempt': 'old'}
        assert index == 1
        second_started.set()
        while not second_released.wait(.01) and not abort.is_set():
            assert not cancel(), 'Cancellation of the old lease reached the new dispatch'
        assert not cancel()
        return {'status': 'completed', 'attempt': 'new'}

    monkeypatch.setattr(service, 'scan_workspace', scan)
    real_client = httpx.AsyncClient

    async def capture(request):
        requests.append((request.url.path, json.loads(request.content) if request.content else None))

    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kwargs: real_client(
        **kwargs, transport=httpx.ASGITransport(app=scanner.app), event_hooks={'request': [capture]}))
    old_claim = store.claim('old-worker')
    old_canceled = threading.Event()
    old = asyncio.create_task(remote_scan(old_claim, snapshot_id, old_canceled.is_set, ['semgrep']))
    fresh = None
    try:
        assert await asyncio.to_thread(first_started.wait, 5)
        # A suspended owner can still have an in-flight HTTP request after its
        # database lease expires and another attempt has claimed the same job.
        with store.connect(write=True) as db:
            db.execute('UPDATE jobs SET lease_until=0 WHERE job_id=?', (snapshot_id,))
        store.recover()
        new_claim = store.claim('new-worker')
        assert new_claim['job_id'] == old_claim['job_id']
        assert new_claim['_lease_owner'] != old_claim['_lease_owner']
        fresh = asyncio.create_task(remote_scan(new_claim, snapshot_id, lambda: False, ['semgrep']))
        assert await asyncio.to_thread(second_started.wait, 5), 'Recovered request conflicted with the old reservation'
        dispatched = [body for path, body in requests if path == '/scan']
        assert len(dispatched) == 2
        request_ids = [body['job_id'] for body in dispatched]
        assert len(set(request_ids)) == 2 and snapshot_id not in request_ids
        assert all(str(uuid.UUID(identifier)) == identifier for identifier in request_ids)
        assert all(body['snapshot_id'] == snapshot_id for body in dispatched)
        assert set(scanner.active) == set(request_ids)

        old_canceled.set()
        with pytest.raises(SourceCanceled):
            await asyncio.wait_for(old, 5)
        assert await asyncio.to_thread(first_stopped.wait, 5)
        assert not fresh.done() and not calls[1]()
        assert [path for path, _ in requests if path.startswith('/cancel/')] == ['/cancel/' + request_ids[0]]
        assert not store.finish(snapshot_id, 'completed', owner=old_claim['_lease_owner'])

        second_released.set()
        assert await asyncio.wait_for(fresh, 5) == {'status': 'completed', 'attempt': 'new'}
        assert store.finish(snapshot_id, 'completed', owner=new_claim['_lease_owner'])
        assert not scanner.active
    finally:
        abort.set()
        second_released.set()
        old_canceled.set()
        for task in (old, fresh):
            if task is not None and not task.done():
                task.cancel()
        await asyncio.gather(*(task for task in (old, fresh) if task is not None), return_exceptions=True)
