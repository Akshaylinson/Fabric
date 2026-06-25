from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title='Textile AI Fabric Service',
    description='OpenRouter FLUX garment rendering service for Workflow 2',
    version='2.0.0',
)

app.include_router(router)
