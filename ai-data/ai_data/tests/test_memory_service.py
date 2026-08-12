from __future__ import annotations

import pytest

from ai_data.models.db import get_session, init_db
from ai_data.models.enums import MemoryType
from ai_data.services.memory_service import (
    InMemoryShortTermStore,
    MemoryService,
    SQLAlchemyLongTermMemoryRepository,
)


@pytest.fixture
def memory_db(tmp_path):
    """Isolated SQLite file per test so tests don't share state."""
    db_url = f"sqlite:///{tmp_path}/test_ai_data.db"
    init_db(db_url)
    return db_url


def test_short_term_records_and_caps_recent_mistakes(student_id):
    store = InMemoryShortTermStore()
    for topic in ["A", "B", "C", "D", "E", "F"]:
        store.record_mistake(student_id, topic, max_recent=5)

    memory = store.get(student_id)
    assert len(memory.recent_mistakes) == 5
    assert memory.recent_mistakes[0] == "F"  # most recent first


def test_short_term_clear(student_id):
    store = InMemoryShortTermStore()
    store.record_mistake(student_id, "Algebra")
    store.clear(student_id)
    assert store.get(student_id) is None


def test_long_term_save_and_recall(student_id, memory_db):
    from ai_data.models.memory import LongTermMemoryEntry

    with get_session(memory_db) as session:
        repo = SQLAlchemyLongTermMemoryRepository(session)
        repo.save(
            LongTermMemoryEntry(
                student_id=student_id,
                memory_type=MemoryType.ACADEMIC,
                memory_data={"weak_topic": "Reading Inference", "strength": "Vocabulary"},
            )
        )

    with get_session(memory_db) as session:
        repo = SQLAlchemyLongTermMemoryRepository(session)
        results = repo.get_relevant(student_id)
        assert len(results) == 1
        assert results[0].memory_data["weak_topic"] == "Reading Inference"


def test_long_term_scoped_by_memory_type(student_id, memory_db):
    from ai_data.models.memory import LongTermMemoryEntry

    with get_session(memory_db) as session:
        repo = SQLAlchemyLongTermMemoryRepository(session)
        repo.save(
            LongTermMemoryEntry(
                student_id=student_id, memory_type=MemoryType.ACADEMIC, memory_data={"a": 1}
            )
        )
        repo.save(
            LongTermMemoryEntry(
                student_id=student_id, memory_type=MemoryType.PREFERENCE, memory_data={"b": 2}
            )
        )

    with get_session(memory_db) as session:
        repo = SQLAlchemyLongTermMemoryRepository(session)
        academic_only = repo.get_relevant(student_id, memory_types=[MemoryType.ACADEMIC])
        assert len(academic_only) == 1
        assert academic_only[0].memory_type == MemoryType.ACADEMIC


def test_memory_service_combines_both_layers(student_id, memory_db):
    with get_session(memory_db) as session:
        service = MemoryService(long_term_repository=SQLAlchemyLongTermMemoryRepository(session))

        service.record_mistake(student_id, "Quadratic Equations")
        session_state = service.current_session(student_id)
        assert "Quadratic Equations" in session_state.recent_mistakes

        service.remember(student_id, MemoryType.GOAL, {"target_score": 1450})
        recalled = service.recall(student_id, memory_types=[MemoryType.GOAL])
        assert recalled[0].memory_data["target_score"] == 1450

        service.end_session(student_id)
        assert service.current_session(student_id).recent_mistakes == []
