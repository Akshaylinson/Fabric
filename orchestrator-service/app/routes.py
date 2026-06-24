from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

_jobs: dict[str, dict[str, str]] = {}


class JobCreateRequest(BaseModel):
    workflow: str
    payload: dict[str, str] = Field(default_factory=dict)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "orchestrator-service"}


@router.post("/jobs")
def create_job(request: JobCreateRequest) -> dict[str, str]:
    job_id = str(uuid4())
    _jobs[job_id] = {
        "job_id": job_id,
        "workflow": request.workflow,
        "status": "queued",
        "retry_count": "0",
    }
    return _jobs[job_id]


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, str]:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/queues")
def queues() -> dict[str, list[str]]:
    return {
        "available": ["template", "fabric", "tryon"],
        "backend": ["redis"],
    }

