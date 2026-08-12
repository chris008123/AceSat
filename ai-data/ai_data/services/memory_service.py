"""Memory service — hackathon prompt section 6, Phase 5 (complete).

Short-term memory is a simple in-process store — good enough for a
hackathon demo. Swap `InMemoryShortTermStore` for a Redis-backed one
without changing callers if latency/scale becomes a problem.

Long-term memory has both the `LongTermMemoryRepository` interface and a
concrete `SQLAlchemyLongTermMemoryRepository` implementation against this
module's own `ai_memory` table (`models/db.py` — self-contained, doesn't
require the Backend Engineer's session setup; point `AI_DATA_DATABASE_URL`
at the shared Postgres instance once one exists, or wire the Backend
Engineer's own `Session` into the repository directly).

`MemoryService` ties both together into the single entry point the AI
Context Builder (Phase 4) and agents should call.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ai_data.models.memory import AIMemoryRecord, LongTermMemoryEntry, MemoryType, ShortTermMemory


class InMemoryShortTermStore:
    """Session-scoped cache. Not durable across process restarts — that's
    fine, short-term memory is meant to be current-session-only per the
    prompt's own definition.
    """

    def __init__(self) -> None:
        self._store: dict[UUID, ShortTermMemory] = {}

    def get(self, student_id: UUID) -> ShortTermMemory | None:
        return self._store.get(student_id)

    def set(self, memory: ShortTermMemory) -> None:
        self._store[memory.student_id] = memory

    def record_mistake(self, student_id: UUID, topic: str, max_recent: int = 5) -> None:
        memory = self._store.get(student_id) or ShortTermMemory(student_id=student_id)
        memory.recent_mistakes = ([topic] + memory.recent_mistakes)[:max_recent]
        self._store[student_id] = memory

    def clear(self, student_id: UUID) -> None:
        self._store.pop(student_id, None)


class LongTermMemoryRepository(Protocol):
    """Interface the Backend Engineer implements against `ai_memory`.

    Kept as a `Protocol` (structural typing) so this module has zero
    dependency on whichever session/connection pattern the backend uses.
    """

    def save(self, entry: LongTermMemoryEntry) -> None: ...

    def get_relevant(
        self,
        student_id: UUID,
        memory_types: list[MemoryType] | None = None,
        limit: int = 10,
    ) -> list[LongTermMemoryEntry]:
        """Return only what's relevant to the current task — never the
        student's entire history (prompt §6 instruction). Callers should
        pass `memory_types` to scope the query (e.g. only ACADEMIC memory
        for a Diagnostic Agent call, only PREFERENCE for a Coaching Agent
        tone decision).
        """
        ...


class SQLAlchemyLongTermMemoryRepository:
    """Concrete `LongTermMemoryRepository` against this module's own
    `ai_memory` table (see `models/db.py`). Fully self-contained — only
    needs a `Session`, so it can be pointed at the shared production
    database once one exists, or run against the local SQLite fallback for
    development/tests today.
    """

    def __init__(self, session: Session):
        self._session = session

    def save(self, entry: LongTermMemoryEntry) -> None:
        record = AIMemoryRecord(
            id=entry.memory_id,
            student_id=entry.student_id,
            memory_type=entry.memory_type.value,
            memory_data=entry.memory_data,
            created_at=entry.created_at,
        )
        self._session.merge(record)

    def get_relevant(
        self,
        student_id: UUID,
        memory_types: list[MemoryType] | None = None,
        limit: int = 10,
    ) -> list[LongTermMemoryEntry]:
        """Returns the most recent entries matching `student_id` (and
        `memory_types` if given), newest first, capped at `limit` — this is
        the "only what's relevant" scoping the prompt requires. Callers
        (e.g. the Diagnostic Agent) narrow further by passing a specific
        `memory_types` list rather than fetching everything and filtering
        client-side.
        """
        query = select(AIMemoryRecord).where(AIMemoryRecord.student_id == student_id)
        if memory_types:
            query = query.where(AIMemoryRecord.memory_type.in_([mt.value for mt in memory_types]))
        query = query.order_by(AIMemoryRecord.created_at.desc()).limit(limit)

        records = self._session.execute(query).scalars().all()
        return [
            LongTermMemoryEntry(
                memory_id=r.id,
                student_id=r.student_id,
                memory_type=MemoryType(r.memory_type),
                memory_data=r.memory_data,
                created_at=r.created_at,
            )
            for r in records
        ]


class MemoryService:
    """Single entry point that combines short-term + long-term memory —
    what the AI Context Builder and agents should actually depend on,
    rather than reaching into `InMemoryShortTermStore` /
    `LongTermMemoryRepository` separately.
    """

    def __init__(
        self,
        long_term_repository: LongTermMemoryRepository,
        short_term_store: InMemoryShortTermStore | None = None,
    ):
        self._long_term = long_term_repository
        self._short_term = short_term_store or InMemoryShortTermStore()

    def current_session(self, student_id: UUID) -> ShortTermMemory:
        return self._short_term.get(student_id) or ShortTermMemory(student_id=student_id)

    def record_mistake(self, student_id: UUID, topic: str) -> None:
        self._short_term.record_mistake(student_id, topic)

    def end_session(self, student_id: UUID) -> None:
        """Clears short-term memory. Callers that want the session's
        outcome retained should `remember()` it as long-term memory first
        — ending a session does not do that automatically, since not every
        short-term detail (e.g. the exact current question) is worth
        keeping long-term.
        """
        self._short_term.clear(student_id)

    def remember(self, student_id: UUID, memory_type: MemoryType, memory_data: dict) -> None:
        entry = LongTermMemoryEntry(student_id=student_id, memory_type=memory_type, memory_data=memory_data)
        self._long_term.save(entry)

    def recall(
        self,
        student_id: UUID,
        memory_types: list[MemoryType] | None = None,
        limit: int = 10,
    ) -> list[LongTermMemoryEntry]:
        return self._long_term.get_relevant(student_id, memory_types=memory_types, limit=limit)
