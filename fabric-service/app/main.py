from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="Textile AI Fabric Service",
    description="Fabric transfer and texture mapping for garment templates",
    version="1.0.0",
)

app.include_router(router)

