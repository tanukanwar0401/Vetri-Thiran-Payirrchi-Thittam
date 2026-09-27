from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routes import router


settings = get_settings()


app = FastAPI(
    title="LegalEase API",
    description=(
        "AI-powered legal document drafting API."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    router
)


@app.get("/")
def root() -> dict[str, str]:

    return {
        "name": "LegalEase API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, object]:

    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "gemini_model": settings.gemini_model,
    }