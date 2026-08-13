from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.main import app


@pytest.fixture
def db_session(tmp_path):
    """Isolated SQLite DB per test, independent of the app's default
    `backend_local.db` file."""
    engine = create_engine(f"sqlite:///{tmp_path}/test_backend.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)
