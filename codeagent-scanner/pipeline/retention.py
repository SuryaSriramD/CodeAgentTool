"""Retention only removes expired, inactive artifacts inside managed storage."""
from datetime import datetime, timedelta, timezone
import json
import shutil
from pipeline.store import TERMINAL


def cleanup(store, settings):
    snapshot_cutoff = datetime.now(timezone.utc) - timedelta(days=settings.snapshot_retention_days)
    report_cutoff = datetime.now(timezone.utc) - timedelta(days=settings.report_retention_days)
    with store.connect() as db:
        rows = [dict(row) for row in db.execute("SELECT job_id,parent_job_id,status,source,submitted_at FROM jobs")]
    retained_run = lambda row: row["status"] not in TERMINAL or row["status"] == "interrupted"
    needed_reports = {row["parent_job_id"] for row in rows if retained_run(row) and row["parent_job_id"]}
    needed_versions = {row["parent_job_id"] or row["job_id"] for row in rows
                       if retained_run(row) or datetime.fromisoformat(row["submitted_at"]) >= report_cutoff}
    protected = set()
    for row in rows:
        source = json.loads(row["source"])
        if retained_run(row) or datetime.fromisoformat(row["submitted_at"]) > snapshot_cutoff:
            protected.add(source.get("snapshot_id") or row["job_id"])
    for directory in ("snapshots", "tmp"):
        for path in (settings.storage / directory).iterdir():
            if path.name not in protected and path.stat().st_mtime < snapshot_cutoff.timestamp():
                if path.is_dir() and not path.is_symlink():
                    shutil.rmtree(path)
    for upload in (settings.storage / "uploads").glob("*.zip"):
        if upload.stem not in protected and upload.stat().st_mtime < snapshot_cutoff.timestamp():
            upload.unlink()
    for row in rows:
        if retained_run(row) or row["job_id"] in needed_reports or datetime.fromisoformat(row["submitted_at"]) >= report_cutoff:
            continue
        job_id = row["job_id"]
        for relative in (f"reports/{job_id}.json", f"reports/{job_id}_enhanced.json", f"reviews/{job_id}.json"):
            (settings.storage / relative).unlink(missing_ok=True)
        with store.connect(write=True) as db:
            # Leave job metadata for history, but remove source-bearing traces after report retention.
            db.execute("DELETE FROM events WHERE job_id=?", (job_id,))
            db.execute("DELETE FROM steps WHERE job_id=?", (job_id,))
    for directory in (settings.storage / "report_versions").glob("*"):
        if (directory.name not in needed_versions and directory.is_dir() and not directory.is_symlink()
                and directory.stat().st_mtime < report_cutoff.timestamp()):
            shutil.rmtree(directory)
