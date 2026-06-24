from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="Textile AI Orchestrator Service",
    description="Workflow orchestration, queue handling, retry logic, and job status tracking",
    version="1.0.0",
)

app.include_router(router)

