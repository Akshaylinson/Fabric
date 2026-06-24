from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="Textile AI Try-On Service",
    description="Human parsing, pose estimation, and try-on generation",
    version="1.0.0",
)

app.include_router(router)

