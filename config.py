"""Typed environment settings for the CodeCraft Academy entrypoint.

The current Flask factory still reads environment variables for backwards
compatibility. This module provides a single documented settings boundary for
new code and future app package extraction.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 5000
    frontend_only: bool = False
    sandbox_url: str = ""
    submission_queue_mode: str = "thread"
    cors_origins: tuple[str, ...] = ("http://localhost:5000", "http://127.0.0.1:5000")

    @classmethod
    def from_env(cls):
        origins = tuple(item.strip() for item in os.getenv("CORS_ORIGINS", ",".join(cls.cors_origins)).split(",") if item.strip())
        return cls(
            environment=os.getenv("FLASK_ENV", "development").lower(),
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "5000")),
            frontend_only=os.getenv("FRONTEND_ONLY", "false").lower() == "true",
            sandbox_url=os.getenv("SANDBOX_URL", ""),
            submission_queue_mode=os.getenv("SUBMISSION_QUEUE_MODE", "thread").lower(),
            cors_origins=origins,
        )
