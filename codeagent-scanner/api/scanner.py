"""Internal scanner service: no model/GitHub credentials or public ports."""
import asyncio
import json
import os
from pathlib import Path
import threading
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Literal
from ingestion.snapshots import verify_snapshot

app = FastAPI(title="CodeAgent internal scanner")
active: dict[str, threading.Event] = {}
slots = asyncio.Semaphore(2)


class ScanInput(BaseModel):
    job_id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    snapshot_id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    profile: Literal["security-v1","security-v2"] = "security-v1"
    analyzers: list[str] | None = None
    timeout_sec: int = Field(default=600, ge=1, le=7200)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/capabilities")
def capabilities():
    from analyzers.service import get_capabilities
    return get_capabilities()


@app.get("/profiles")
def profiles():
    from analyzers.profiles import PROFILES, profile_metadata
    return {profile:profile_metadata(profile) for profile in PROFILES}


@app.post("/cancel/{job_id}")
def cancel(job_id: str):
    if job_id in active:
        active[job_id].set()
    return {"ok": True}


@app.post("/scan")
async def scan(body: ScanInput, request: Request):
    from analyzers.service import scan_workspace
    if body.job_id in active:
        raise HTTPException(409, "This scan is already active")
    # Reserve before the first await, so a duplicate cannot replace our stop event.
    stop = active[body.job_id] = threading.Event()
    task = None
    try:
        root = Path(os.getenv("SNAPSHOT_ROOT", "/data/snapshots")) / body.snapshot_id
        if not (root / "manifest.json").is_file():
            raise HTTPException(404, "Snapshot unavailable")
        await asyncio.to_thread(verify_snapshot, root / "source", json.loads((root / "manifest.json").read_text()))
        async with slots:
            task = asyncio.create_task(asyncio.to_thread(scan_workspace, str(root / "source"),
                analyzers=body.analyzers, timeout_sec=body.timeout_sec, cancel=stop.is_set, profile=body.profile))
            while not task.done():
                if await request.is_disconnected():
                    stop.set()
                await asyncio.sleep(0.2)
            return await task
    finally:
        stop.set()
        try:
            if task and not task.done():
                await task
        finally:
            active.pop(body.job_id, None)


class ValidationInput(BaseModel):
    validation_id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    snapshot_id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    profile: Literal["security-v1","security-v2"] = "security-v1"
    edits: list[dict] = Field(min_length=1,max_length=100)
    target_findings: list[dict] = Field(min_length=1,max_length=100)
    timeout_sec: int = Field(default=120,ge=1,le=120)


@app.post("/validate")
async def validate(body: ValidationInput, request: Request):
    from analyzers.validation import validate_proposal
    if body.validation_id in active:
        raise HTTPException(409,"This validation is already active")
    stop=active[body.validation_id]=threading.Event()
    task=None
    try:
        root=Path(os.getenv("SNAPSHOT_ROOT","/data/snapshots"))/body.snapshot_id
        if not (root/"manifest.json").is_file():raise HTTPException(404,"Snapshot unavailable")
        task=asyncio.create_task(asyncio.to_thread(validate_proposal,root,body.model_dump(),stop.is_set))
        while not task.done():
            if await request.is_disconnected():stop.set()
            await asyncio.sleep(.2)
        return await task
    finally:
        stop.set()
        try:
            if task and not task.done():await task
        finally:
            active.pop(body.validation_id,None)
