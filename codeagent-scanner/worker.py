"""Run with `python -m worker`. API imports never launch workers."""
from concurrent.futures import ThreadPoolExecutor
import logging
import signal
import threading
import time
import uuid
from pipeline.orchestrator import JobOrchestrator
from settings import Settings


class Worker:
    def __init__(self, settings=None, scan_fn=None):
        self.settings = settings or Settings()
        self.orchestrator = JobOrchestrator(settings=self.settings, scan_fn=scan_fn)
        self.store = self.orchestrator.store
        self.owner = str(uuid.uuid4())
        self.stop = threading.Event()

    def run(self):
        futures, heartbeat_at, cleanup_at = set(), 0, 0
        with ThreadPoolExecutor(max_workers=self.settings.max_jobs + 2) as pool:
            try:
                while not self.stop.is_set():
                    if time.monotonic() >= heartbeat_at:
                        self.store.recover()
                        self.store.heartbeat(self.owner, self.settings.worker_lease_sec)
                        heartbeat_at = time.monotonic() + 5
                    if time.monotonic() >= cleanup_at:
                        from pipeline.retention import cleanup
                        cleanup(self.store, self.settings)
                        cleanup_at = time.monotonic() + 3600
                    futures = {future for future in futures if not future.done()}
                    if len(futures) < self.settings.max_jobs + 2:
                        job = self.store.claim(self.owner, self.settings.max_jobs, self.settings.worker_lease_sec)
                        if job:
                            futures.add(pool.submit(self.orchestrator.execute, job, self.stop.is_set))
                            continue
                    self.stop.wait(0.25)
            finally:
                self.stop.set()
                for future in futures:
                    future.result()
                self.store.release_worker(self.owner)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = Worker()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: worker.stop.set())
    worker.run()
