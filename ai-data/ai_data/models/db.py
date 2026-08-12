"""Standalone engine/session for this module's own tables
(`topic_mastery`, `ai_memory`, `ai_logs`).

This is deliberately self-contained — it does not import or depend on
whatever session pattern the Backend Engineer sets up for their tables.
Two ways this gets used in the real deployment:

1. **Simplest for a hackathon**: everyone points at the same PostgreSQL
   instance. Set `DATABASE_URL` to the same value the backend uses, and
   `Base.metadata.create_all()` (or an Alembic migration) creates these
   three tables alongside the backend's.
2. **If the team wants a single session factory**: the Backend Engineer
   can inject their own `Session` into the repository functions instead of
   using `get_session()` here — the repository implementation in
   `memory_service.py` only needs a `Session`, not this specific factory.

Either way, nothing in `services/` other than this file and
`memory_service.py`'s concrete repository touches SQLAlchemy directly.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ai_data.models.base import Base

# Falls back to a local sqlite file so this module runs standalone (tests,
# a quick demo script) without a live Postgres instance. Point
# DATABASE_URL at the real Postgres connection string once one exists.
DEFAULT_DATABASE_URL = "sqlite:///./ai_data_local.db"


def get_engine(database_url: str | None = None):
    url = database_url or os.environ.get("AI_DATA_DATABASE_URL", DEFAULT_DATABASE_URL)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


def init_db(database_url: str | None = None) -> None:
    """Create `topic_mastery` / `ai_memory` / `ai_logs` if they don't exist.
    For the real Postgres deployment, prefer an Alembic migration instead —
    this is here so the module is runnable/testable standalone.
    """
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)


_SessionLocal: sessionmaker | None = None


def _get_sessionmaker(database_url: str | None = None) -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine(database_url)
        _SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return _SessionLocal


@contextmanager
def get_session(database_url: str | None = None) -> Iterator[Session]:
    session = _get_sessionmaker(database_url)()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
