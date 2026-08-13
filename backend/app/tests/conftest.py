from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
import app.database.connection as db_connection
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
def client(tmp_path, monkeypatch):
    """A TestClient wired to its own isolated SQLite file, so Phase 2/3
    tests (auth, assessments, ai bridge) don't share state with each other
    or with the dev-convenience `backend_local.db`.
    """
    db_url = f"sqlite:///{tmp_path}/test_backend_api.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    monkeypatch.setattr(db_connection, "engine", engine)
    monkeypatch.setattr(db_connection, "SessionLocal", SessionLocal)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[db_connection.get_db] = override_get_db
    Base.metadata.create_all(engine)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Registers + logs in a demo student, returns bearer auth headers."""
    client.post("/auth/register", json={"email": "sarah@email.com", "password": "supersecure1"})
    r = client.post("/auth/login", json={"email": "sarah@email.com", "password": "supersecure1"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seeded_questions(client):
    """Seeds a small question bank directly via the DB session the
    fixture-overridden app is using — enough questions/attempts across two
    topics to clear ai-data's evidence thresholds (min 3 attempts for
    weak/strong, min 10 for trend detection).
    """
    from app.database.connection import SessionLocal
    from app.models.question import Question

    db = SessionLocal()
    questions = []
    for i in range(12):
        q = Question(
            subject="reading",
            topic="Reading Inference",
            difficulty=3,
            question_text=f"inference question {i}",
            answer_options={"A": "x", "B": "y"},
            correct_answer="A",
        )
        db.add(q)
        questions.append(q)
    for i in range(4):
        q = Question(
            subject="math",
            topic="Linear Equations",
            difficulty=2,
            question_text=f"algebra question {i}",
            answer_options={"A": "x", "B": "y"},
            correct_answer="B",
        )
        db.add(q)
        questions.append(q)
    db.commit()
    for q in questions:
        db.refresh(q)
    db.close()
    return questions

