"""Application settings — Deployment_architecture.txt §5 lists the env
vars this backend needs: DATABASE_URL, JWT_SECRET, AI_API_KEY, ENVIRONMENT.

Loaded once as a module-level singleton (`settings`) so the rest of the
app imports `from app.config.settings import settings` rather than
re-reading the environment everywhere.
"""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    # Falls back to a local SQLite file so `main.py` and the test suite
    # run without a live Postgres instance — set DATABASE_URL (see
    # .env.example) to your Supabase connection string for real use. Same
    # DATABASE_URL also backs ai-data's own tables in production (see
    # README's "one migration chain" note) — both packages' tables live
    # in the same Supabase Postgres database.
    database_url: str = "sqlite:///./backend_local.db"

    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24  # 24h, tune later

    # AI_API_KEY per Deployment_architecture.txt — not used directly by
    # this module yet (Phase 1 doesn't touch AI orchestration), reserved
    # for the `ai` route added in a later phase.
    ai_api_key: str | None = None

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
