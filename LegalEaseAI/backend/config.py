from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root.
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    """
    Application configuration.
    """

    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.5-flash")

    demo_mode: bool = Field(default=True)

    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    backend_url: str = Field(
        default="http://127.0.0.1:8000"
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:8501",
            "http://127.0.0.1:8501",
        ]
    )

    logo_path: Path = Field(
        default=BASE_DIR / "assets" / "logo.png"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Load configuration from environment variables.
    """

    origins = os.getenv("CORS_ORIGINS", "")

    parsed_origins = [
        origin.strip()
        for origin in origins.split(",")
        if origin.strip()
    ]

    return Settings(
        gemini_api_key=os.getenv(
            "GEMINI_API_KEY",
            ""
        ).strip(),

        gemini_model=os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        ).strip(),

        demo_mode=os.getenv(
            "DEMO_MODE",
            "true"
        ).lower()
        in {"1", "true", "yes", "on"},

        api_host=os.getenv(
            "API_HOST",
            "0.0.0.0"
        ),

        api_port=int(
            os.getenv(
                "API_PORT",
                "8000"
            )
        ),

        backend_url=os.getenv(
            "BACKEND_URL",
            "http://127.0.0.1:8000"
        ),

        cors_origins=(
            parsed_origins
            or [
                "http://localhost:8501",
                "http://127.0.0.1:8501",
            ]
        ),
    )