"""
Edify Backend — Application Configuration.

Loads all settings from environment variables via Pydantic BaseSettings.
Never hard-code secrets. Use .env file for local development.
"""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = "Edify"
    app_env: str = "development"
    debug: bool = True

    # ---- Backend ----
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # ---- Database ----
    database_url: str = "postgresql+asyncpg://edify:edify_dev_password@localhost:5432/edify"

    # ---- Redis ----
    redis_url: str = "redis://localhost:6379/0"

    # ---- JWT ----
    jwt_secret_key: str = "change-me-to-a-random-secret-in-production"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 30
    jwt_algorithm: str = "HS256"

    # ---- Google OAuth ----
    google_client_id: str = ""
    google_client_secret: str = ""

    # ---- Storage ----
    storage_path: str = "./storage"
    storage_music_dir: str = "music"
    storage_covers_dir: str = "covers"
    storage_temp_dir: str = "temp"
    max_upload_size_mb: int = 100

    # ---- CORS ----
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ---- Logging ----
    log_level: str = "INFO"
    log_format: str = "json"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            import json

            return json.loads(v)
        return v

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


# Singleton instance
settings = Settings()
