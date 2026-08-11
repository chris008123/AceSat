"""Memory service — hackathon prompt section 6, Phase 5.

Short-term memory is implemented as a simple in-process store here — good
enough for a hackathon demo. Swap `InMemoryShortTermStore` for a Redis-backed
one without changing callers if latency/scale becomes a problem.

Long-term memory retrieval is defined as a `Protocol` rather than
implemented against a concrete DB session, because that requires the
Backend Engineer's session/engine setup, which doesn't exist yet in this
repo. Implement `LongTermMemoryRepository` against SQLAlchemy once the
`ai_memory` table (see `models/memory.py`) is migrated.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from ai_data.models.memory import LongTermMemoryEntry, MemoryType, ShortTermMemory


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
