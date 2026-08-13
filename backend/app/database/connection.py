"""Database connection — Backend_architecture.txt §4 puts this at
`database/connection.py`.

Owns the engine/session for backend-owned tables (`users`,
`student_profiles`, `questions`, `assessments`, `answers`,
`learning_sessions`, `study_plans`). Per the ai-data README's boundary
note, ai-data's tables (`topic_mastery`, `ai_memory`, `ai_logs`,
`concept_embeddings`) live in the same physical database but are defined
against ai-data's own `Base` — this module's `Base` only covers the tables
this backend is responsible for.
"""

from __future__ import annotations

from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config.settings import settings


class Base(DeclarativeBase):
    pass


def _connect_args(url: str) -> dict:
    return {"check_same_thread": False} if url.startswith("sqlite") else {}


engine = create_engine(settings.database_url, connect_args=_connect_args(settings.database_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create all backend-owned tables. Fine for local dev/tests; use the
    Alembic migration chain (`alembic/`) for anything that touches a real
    Postgres instance, since that's what also carries ai-data's tables
    (see `alembic/env.py`).
    """
    Base.metadata.create_all(engine)


def get_db() -> Iterator[Session]:
    """FastAPI dependency — `Depends(get_db)` in route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
