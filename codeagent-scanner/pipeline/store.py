"""SQLite job queue and append-only event log for a single-host installation."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sqlite3
import time
import uuid
from pipeline.projects import ProjectStoreMixin

TERMINAL = {"completed", "partial", "failed", "canceled", "interrupted"}


class QueueFull(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


class Store(ProjectStoreMixin):
    def __init__(self, storage: Path):
        self.storage = Path(storage)
        self.storage.mkdir(parents=True, exist_ok=True)
        self.path = self.storage / "codeagent.sqlite3"
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY, kind TEXT NOT NULL, parent_job_id TEXT,
                    status TEXT NOT NULL, config TEXT NOT NULL, config_hash TEXT NOT NULL,
                    source TEXT NOT NULL, progress TEXT, submitted_at TEXT NOT NULL,
                    started_at TEXT, finished_at TEXT, error TEXT,
                    lease_owner TEXT, lease_until REAL, cancel_requested INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS queue ON jobs(status, submitted_at);
                CREATE INDEX IF NOT EXISTS children ON jobs(parent_job_id, submitted_at);
                CREATE TABLE IF NOT EXISTS steps (
                    job_id TEXT NOT NULL, key TEXT NOT NULL, data TEXT NOT NULL,
                    PRIMARY KEY(job_id,key)
                );
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL,
                    event TEXT NOT NULL, data TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS job_events ON events(job_id,seq);
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS workers (id TEXT PRIMARY KEY, heartbeat REAL NOT NULL);
            """)
        with self.connect(write=True) as db:
            # Older databases stored the worker ID in lease_owner. Preserve it as
            # worker identity; subsequent claims always receive a fresh token.
            columns = {row["name"] for row in db.execute("PRAGMA table_info(jobs)")}
            if "lease_worker" not in columns:
                db.execute("ALTER TABLE jobs ADD COLUMN lease_worker TEXT")
                db.execute("UPDATE jobs SET lease_worker=lease_owner WHERE lease_owner IS NOT NULL")
            self.migrate_projects(db)

    @contextmanager
    def connect(self, write=False):
        db = sqlite3.connect(self.path, timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=15000")
        try:
            if write:
                db.execute("BEGIN IMMEDIATE")
            yield db
            if write:
                db.commit()
        except BaseException:
            if write:
                db.rollback()
            raise
        finally:
            db.close()

    def _event(self, db, job_id, event, data):
        db.execute("INSERT INTO events(job_id,event,data,created_at) VALUES(?,?,?,?)",
                   (job_id, event, encoded(data), now()))
        parent = db.execute("SELECT parent_job_id FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if parent and parent[0]:
            db.execute("INSERT INTO events(job_id,event,data,created_at) VALUES(?,?,?,?)",
                       (parent[0], event, encoded({**data, "run_id": job_id}), now()))

    def create_job(self, kind, config, source, parent_job_id=None, job_id=None):
        with self.connect(write=True) as db:
            return self._create_job(db, kind, config, source, parent_job_id, job_id)

    def _create_job(self, db, kind, config, source, parent_job_id=None, job_id=None):
        job_id = job_id or str(uuid.uuid4())
        digest = hashlib.sha256(encoded(config).encode()).hexdigest()
        if kind == "review":
            candidates = db.execute("""SELECT job_id,source FROM jobs WHERE parent_job_id=? AND kind='review'
                AND config_hash=? AND status IN ('queued','running','completed')
                ORDER BY submitted_at DESC""", (parent_job_id, digest)).fetchall()
            for existing in candidates:
                if json.loads(existing["source"]).get("report_hash") == source.get("report_hash"):
                    return self._get(db, existing["job_id"])
        if kind == "provider_check":
            existing = db.execute("SELECT job_id FROM jobs WHERE kind='provider_check' AND config_hash=? AND status IN ('queued','running')", (digest,)).fetchone()
            if existing:
                return self._get(db, existing[0])
        if db.execute("SELECT COUNT(*) FROM jobs WHERE status='queued'").fetchone()[0] >= 100:
            raise QueueFull("Job queue is full; retry later")
        db.execute("""INSERT INTO jobs(job_id,kind,parent_job_id,status,config,config_hash,source,submitted_at)
                      VALUES(?,?,?,'queued',?,?,?,?)""",
                   (job_id, kind, parent_job_id, encoded(config), digest, encoded(source), now()))
        self._event(db, job_id, "queued", {"status": "queued", "kind": kind})
        return self._get(db, job_id)

    def _decode(self, row):
        data = dict(row)
        for field in ("config", "source", "progress"):
            data[field] = json.loads(data[field]) if data[field] else None
        for field in ("lease_owner", "lease_worker", "lease_until", "config_hash"):
            data.pop(field, None)
        data["cancel_requested"] = bool(data["cancel_requested"])
        return data

    def _get(self, db, job_id):
        row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not row:
            return None
        data = self._decode(row)
        data["steps"] = [{"key": r["key"], **json.loads(r["data"])} for r in db.execute(
            "SELECT key,data FROM steps WHERE job_id=? ORDER BY rowid", (job_id,))]
        data["latest_review_id"] = self._latest_review(db, job_id, data["source"].get("report_hash"))
        return data

    def _latest_review(self, db, parent, report_hash):
        for child in db.execute("SELECT job_id,source FROM jobs WHERE parent_job_id=? AND kind='review' ORDER BY submitted_at DESC,rowid DESC", (parent,)):
            if not report_hash or json.loads(child["source"]).get("report_hash") == report_hash:
                return child["job_id"]
        return None

    def get(self, job_id):
        with self.connect() as db:
            return self._get(db, job_id)

    def list(self, page=1, limit=20, status=None, kind=None):
        where, args = [], []
        if status:
            where.append("status=?")
            args.append(status)
        if kind:
            where.append("kind=?")
            args.append(kind)
        clause = " WHERE " + " AND ".join(where) if where else ""
        with self.connect() as db:
            total = db.execute("SELECT COUNT(*) FROM jobs" + clause, args).fetchone()[0]
            rows = db.execute("SELECT job_id FROM jobs" + clause + " ORDER BY submitted_at DESC LIMIT ? OFFSET ?",
                              (*args, limit, (page - 1) * limit)).fetchall()
            return {"items": [self._get(db, r[0]) for r in rows], "total": total, "page": page, "limit": limit}

    def claim(self, owner, max_scans=2, lease_sec=30):
        with self.connect(write=True) as db:
            active = db.execute("SELECT kind,config FROM jobs WHERE status='running'").fetchall()
            scans = sum(r["kind"] == "scan" for r in active)
            reviews = [json.loads(r["config"]).get("provider") for r in active if r["kind"] in ("review", "provider_check")]
            for row in db.execute("SELECT * FROM jobs WHERE status='queued' AND cancel_requested=0 ORDER BY submitted_at").fetchall():
                if row["kind"] == "scan" and scans >= max_scans:
                    continue
                provider = json.loads(row["config"]).get("provider")
                if row["kind"] in ("review", "provider_check") and (len(reviews) >= 2 or (provider == "ollama" and "ollama" in reviews)):
                    continue
                lease_token = uuid.uuid4().hex
                db.execute("""UPDATE jobs SET status='running',started_at=COALESCE(started_at,?),
                    finished_at=NULL,error=NULL,lease_owner=?,lease_worker=?,lease_until=? WHERE job_id=?""",
                           (now(), lease_token, owner, time.time() + lease_sec, row["job_id"]))
                self._event(db, row["job_id"], "started", {"status": "running"})
                return {**self._get(db, row["job_id"]), "_lease_owner": lease_token}
        return None

    def heartbeat(self, owner, lease_sec=30):
        with self.connect(write=True) as db:
            db.execute("INSERT OR REPLACE INTO workers VALUES(?,?)", (owner, time.time()))
            db.execute("UPDATE jobs SET lease_until=? WHERE lease_worker=? AND status='running'", (time.time() + lease_sec, owner))

    def worker_online(self):
        with self.connect() as db:
            return bool(db.execute("SELECT 1 FROM workers WHERE heartbeat>? LIMIT 1", (time.time() - 45,)).fetchone())

    def release_worker(self, owner):
        with self.connect(write=True) as db:
            db.execute("DELETE FROM workers WHERE id=?", (owner,))
            db.execute("UPDATE jobs SET lease_until=0 WHERE lease_worker=? AND status='running'", (owner,))
        self.recover()

    def recover(self):
        with self.connect(write=True) as db:
            expired = db.execute("SELECT * FROM jobs WHERE status='running' AND lease_until<?", (time.time(),)).fetchall()
            for row in expired:
                steps = db.execute("SELECT key,data FROM steps WHERE job_id=?", (row["job_id"],)).fetchall()
                uncertain = False
                for step in steps:
                    data = json.loads(step["data"])
                    if row["kind"] in ("review", "provider_check") and data.get("status") == "running":
                        if data.get('role') == 'validator':
                            data.update(status='retry_requested', error='Worker stopped during deterministic validation; safely retrying.')
                        else:
                            data.update(status="interrupted", error="Worker stopped during a model call; its outcome is uncertain. Retry explicitly.")
                            uncertain = True
                        db.execute("UPDATE steps SET data=? WHERE job_id=? AND key=?", (encoded(data), row["job_id"], step["key"]))
                status = "interrupted" if uncertain else "queued"
                error = "Interrupted model call requires explicit retry" if uncertain else None
                db.execute("UPDATE jobs SET status=?,error=?,lease_owner=NULL,lease_worker=NULL,lease_until=NULL WHERE job_id=?", (status, error, row["job_id"]))
                self._event(db, row["job_id"], "recovered", {"status": status, "error": error})

    def cancel(self, job_id):
        with self.connect(write=True) as db:
            row = db.execute("SELECT status FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row or row[0] not in ("queued", "running", "interrupted"):
                return False
            ids = [job_id] + [r[0] for r in db.execute("SELECT job_id FROM jobs WHERE parent_job_id=? AND status IN ('queued','running','interrupted')", (job_id,))]
            for target in ids:
                db.execute("UPDATE jobs SET status='canceled',cancel_requested=1,finished_at=? WHERE job_id=?", (now(), target))
                for step in db.execute("SELECT key,data FROM steps WHERE job_id=?", (target,)).fetchall():
                    data = json.loads(step["data"])
                    if data.get("status") == "running":
                        data.update(status="cancelled", error={"code": "cancelled", "message": "Canceled by user"})
                        db.execute("UPDATE steps SET data=? WHERE job_id=? AND key=?", (encoded(data), target, step["key"]))
                self._event(db, target, "finished", {"status": "canceled"})
            return True

    def is_canceled(self, job_id):
        with self.connect() as db:
            row = db.execute("SELECT cancel_requested,status FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            return not row or bool(row[0]) or row[1] == "canceled"

    def owns(self, job_id, owner):
        with self.connect() as db:
            return bool(db.execute("SELECT 1 FROM jobs WHERE job_id=? AND lease_owner=? AND status='running' AND lease_until>?",
                                   (job_id, owner, time.time())).fetchone())

    def retry(self, job_id):
        with self.connect(write=True) as db:
            row = db.execute("SELECT status FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row or row[0] not in ("failed", "partial", "interrupted"):
                return False
            for step in db.execute("SELECT key,data FROM steps WHERE job_id=?", (job_id,)).fetchall():
                data = json.loads(step["data"])
                if data.get("status") in ("failed", "running", "interrupted"):
                    data["status"] = "retry_requested"
                    db.execute("UPDATE steps SET data=? WHERE job_id=? AND key=?", (encoded(data), job_id, step["key"]))
            db.execute("UPDATE jobs SET status='queued',cancel_requested=0,error=NULL,finished_at=NULL,lease_owner=NULL,lease_worker=NULL,lease_until=NULL WHERE job_id=?", (job_id,))
            self._event(db, job_id, "retry_requested", {"status": "queued"})
            return True

    def progress(self, job_id, phase, percent, owner=None):
        with self.connect(write=True) as db:
            if owner and not self._owns(db, job_id, owner):
                return False
            changed = db.execute("UPDATE jobs SET progress=? WHERE job_id=? AND status='running'", (encoded({"phase": phase, "percent": percent}), job_id)).rowcount
            if changed:
                self._event(db, job_id, "progress", {"phase": phase, "percent": percent})

    def set_source(self, job_id, source, owner=None):
        with self.connect(write=True) as db:
            if owner and not self._owns(db, job_id, owner):
                return False
            db.execute("UPDATE jobs SET source=? WHERE job_id=?", (encoded(source), job_id))
            return True

    def _owns(self, db, job_id, owner):
        return bool(db.execute("SELECT 1 FROM jobs WHERE job_id=? AND status='running' AND lease_owner=? AND lease_until>?",
                               (job_id, owner, time.time())).fetchone())

    def finish(self, job_id, status, error=None, review_config=None, source=None, owner=None):
        if status not in TERMINAL:
            raise ValueError("Invalid terminal status")
        with self.connect(write=True) as db:
            if owner and not db.execute("SELECT 1 FROM jobs WHERE job_id=? AND lease_owner=? AND lease_until>?", (job_id, owner, time.time())).fetchone():
                return False
            changed = db.execute("""UPDATE jobs SET status=?,error=?,finished_at=?,lease_owner=NULL,lease_worker=NULL,lease_until=NULL
                WHERE job_id=? AND status='running' AND cancel_requested=0""", (status, error, now(), job_id)).rowcount
            if changed:
                self._event(db, job_id, "finished", {"status": status, "error": error})
                # Static completion and requested review submission are one transaction.
                if review_config is not None and status in ("completed", "partial"):
                    child_id = str(uuid.uuid4())
                    digest = hashlib.sha256(encoded(review_config).encode()).hexdigest()
                    db.execute("""INSERT INTO jobs(job_id,kind,parent_job_id,status,config,config_hash,source,submitted_at)
                        VALUES(?,'review',?,'queued',?,?,?,?)""",
                        (child_id, job_id, encoded(review_config), digest, encoded(source or {}), now()))
                    self._event(db, child_id, "queued", {"status": "queued", "kind": "review"})
            return bool(changed)

    def save_step(self, job_id, key, data, owner=None):
        with self.connect(write=True) as db:
            row = db.execute("SELECT status,lease_owner,lease_until FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row or row[0] != "running" or (owner and (row[1] != owner or (row[2] or 0) <= time.time())):
                return False
            db.execute("INSERT OR REPLACE INTO steps VALUES(?,?,?)", (job_id, key, encoded(data)))
            self._event(db, job_id, "agent_step", {"key": key, **data})
            return True

    def load_step(self, job_id, key):
        with self.connect() as db:
            row = db.execute("SELECT data FROM steps WHERE job_id=? AND key=?", (job_id, key)).fetchone()
            return json.loads(row[0]) if row else None

    def events(self, job_id, after=0, limit=200):
        with self.connect() as db:
            return [{**dict(r), "data": json.loads(r["data"])} for r in db.execute(
                "SELECT * FROM events WHERE job_id=? AND seq>? ORDER BY seq LIMIT ?", (job_id, after, limit))]

    def get_setting(self, key, default=None):
        with self.connect() as db:
            row = db.execute("SELECT data FROM settings WHERE key=?", (key,)).fetchone()
            return json.loads(row[0]) if row else default

    def set_setting(self, key, value):
        with self.connect(write=True) as db:
            db.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, encoded(value)))

    def write_artifact(self, relative, value):
        target = self.storage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(target.name + "." + uuid.uuid4().hex + ".tmp")
        temp.write_text(encoded(value), encoding="utf-8")
        temp.replace(target)

    def write_run_artifact(self, job_id, relative, value, owner=None):
        """Fence publication against cancellation and a superseding worker lease."""
        with self.connect(write=True) as db:
            row = db.execute("SELECT status,lease_owner,lease_until FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row or row[0] != "running" or (owner and (row[1] != owner or (row[2] or 0) <= time.time())):
                return False
            self.write_artifact(relative, value)
            return True

    def _freeze_report(self, scan_id, report):
        content = {key: value for key, value in report.items() if key != "report_hash"}
        digest = hashlib.sha256(encoded(content).encode()).hexdigest()
        frozen = {**content, "report_hash": digest}
        path = f"report_versions/{scan_id}/{digest}.json"
        if not (self.storage / path).is_file():
            self.write_artifact(path, frozen)
        return frozen

    def publish_scan_report(self, job_id, report, owner=None):
        """Publish the current report and its immutable version under one lease fence."""
        with self.connect(write=True) as db:
            row = db.execute("SELECT status,source FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row or row["status"] != "running" or (owner and not self._owns(db, job_id, owner)):
                return None
            report = self.index_report(db, job_id, report)
            frozen = self._freeze_report(job_id, report)
            self.save_scan_index(db, job_id, frozen)
            source = {**json.loads(row["source"]), "report_hash": frozen["report_hash"]}
            self.write_artifact(f"reports/{job_id}.json", frozen)
            # An enhanced report for an earlier static result is not current.
            previous = self.read_artifact(f"reports/{job_id}_enhanced.json")
            if previous and previous.get("report_hash") != frozen["report_hash"]:
                (self.storage / f"reports/{job_id}_enhanced.json").unlink(missing_ok=True)
            db.execute("UPDATE jobs SET source=? WHERE job_id=?", (encoded(source), job_id))
            return frozen["report_hash"]

    def create_review(self, parent_id, config):
        """Freeze the current static result and deduplicate only its exact review input."""
        with self.connect(write=True) as db:
            parent = db.execute("SELECT kind,status,source FROM jobs WHERE job_id=?", (parent_id,)).fetchone()
            if not parent or parent["kind"] != "scan" or parent["status"] not in {"completed", "partial"}:
                raise ValueError("Wait for a successful or partial static scan")
            report = self.read_artifact(f"reports/{parent_id}.json")
            if not report:
                raise ValueError("Source report is unavailable")
            frozen = self._freeze_report(parent_id, report)
            source = {**json.loads(parent["source"]), "report_hash": frozen["report_hash"]}
            db.execute("UPDATE jobs SET source=? WHERE job_id=?", (encoded(source), parent_id))
            if not report.get("report_hash"):
                self.write_artifact(f"reports/{parent_id}.json", frozen)
            return self._create_job(db, "review", config, source, parent_id)

    def review_input(self, job_id, owner=None):
        """Legacy queued reviews bind once; versioned runs never fall back to newer data."""
        with self.connect(write=True) as db:
            row = db.execute("SELECT parent_job_id,status,source FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row or row["status"] != "running" or (owner and not self._owns(db, job_id, owner)):
                return None, None
            source = json.loads(row["source"])
            digest = source.get("report_hash")
            if digest:
                report = self.read_artifact(f"report_versions/{row['parent_job_id']}/{digest}.json")
            else:
                report = self.read_artifact(f"reports/{row['parent_job_id']}.json")
                if report:
                    report = self._freeze_report(row["parent_job_id"], report)
                    source["report_hash"] = report["report_hash"]
                    db.execute("UPDATE jobs SET source=? WHERE job_id=?", (encoded(source), job_id))
            return report, source

    def publish_review(self, job_id, enhanced, owner=None):
        with self.connect(write=True) as db:
            row = db.execute("SELECT parent_job_id,status,source FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row or row["status"] != "running" or (owner and not self._owns(db, job_id, owner)):
                return False
            parent = row["parent_job_id"]
            self.write_artifact(f"reviews/{job_id}.json", enhanced)
            current = db.execute("SELECT source FROM jobs WHERE job_id=?", (parent,)).fetchone()
            current_hash = json.loads(current["source"]).get("report_hash") if current else None
            review_hash = json.loads(row["source"]).get("report_hash")
            if ((not current_hash or current_hash == review_hash) and
                    self._latest_review(db, parent, current_hash) == job_id):
                self.write_artifact(f"reports/{parent}_enhanced.json", enhanced)
            return True

    def read_artifact(self, relative):
        path = self.storage / relative
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
