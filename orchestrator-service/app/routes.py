from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from textile_shared.persistence import PersistentJsonStore, service_state_dir

router = APIRouter()

_JOBS = PersistentJsonStore(service_state_dir("orchestrator-service") / "jobs.json", default_factory=dict)


class JobCreateRequest(BaseModel):
    workflow: str
    entity_id: str | None = None
    action: str | None = None
    parent_job_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str = "queued"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "orchestrator-service"}


@router.post("/jobs")
def create_job(request: JobCreateRequest) -> dict[str, Any]:
    jobs = _JOBS.load()
    job_id = f"job_{uuid4().hex[:12]}"
    timestamp = datetime.now(timezone.utc).isoformat()
    job = {
        "job_id": job_id,
        "workflow": request.workflow,
        "entity_id": request.entity_id,
        "action": request.action,
        "parent_job_id": request.parent_job_id,
        "status": request.status,
        "retry_count": 0,
        "payload": request.payload,
        "created_at": timestamp,
        "updated_at": timestamp,
        "child_job_ids": [],
    }
    if request.parent_job_id and request.parent_job_id in jobs:
        jobs[request.parent_job_id].setdefault("child_job_ids", []).append(job_id)
        jobs[request.parent_job_id]["updated_at"] = timestamp
    jobs[job_id] = job
    _JOBS.save(jobs)
    return job


@router.get("/jobs")
def list_jobs() -> dict[str, list[dict[str, Any]]]:
    jobs = _JOBS.load()
    return {"items": list(jobs.values())}


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    jobs = _JOBS.load()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/queues")
def queues() -> dict[str, list[str]]:
    jobs = _JOBS.load()
    pending = [job_id for job_id, job in jobs.items() if job.get("status") in {"queued", "running"}]
    return {
        "available": ["template", "fabric", "tryon"],
        "backend": ["redis"],
        "tracked_jobs": pending,
    }
