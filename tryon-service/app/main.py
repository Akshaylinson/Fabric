from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title='Textile AI Try-On Service',
    description='API-driven Workflow 3 virtual try-on service',
    version='2.0.0',
)

app.include_router(router)
