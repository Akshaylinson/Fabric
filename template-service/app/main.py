from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="Textile AI Template Service",
    description="Garment ingestion, segmentation, metadata extraction, and template package generation",
    version="1.0.0",
)

app.include_router(router)

