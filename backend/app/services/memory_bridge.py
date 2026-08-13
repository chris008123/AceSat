"""Memory bridge — Api_design.txt §11 (Store Memory / Retrieve Memory).

Thin wrapper around ai-data's `MemoryService`/`SQLAlchemyLongTermMemoryRepository`
— per the ai-data README's boundary note, `ai_memory` is an ai-data-owned
table, so this module doesn't reimplement persistence, it just opens a
session against ai-data's own `Base` (pointed at this backend's
`DATABASE_URL`, since both packages' tables live in the same physical
database — see README's "one shared Postgres database" note) and calls
into `ai_data.services.memory_service`.
"""

from __future__ import annotations

from uuid import UUID

from ai_data.models.db import get_session as ai_data_session_scope
from ai_data.models.enums import MemoryType
from ai_data.services.memory_service import MemoryService, SQLAlchemyLongTermMemoryRepository

from app.config.settings import settings
from app.utils.errors import ValidationAPIError

_VALID_MEMORY_TYPES = {t.value for t in MemoryType}


def store_memory(student_id: UUID, memory_type: str, data: dict) -> None:
    if memory_type not in _VALID_MEMORY_TYPES:
        raise ValidationAPIError(
            f"Unknown memory type {memory_type!r}; expected one of {sorted(_VALID_MEMORY_TYPES)}"
        )

    with ai_data_session_scope(settings.database_url) as session:
        service = MemoryService(long_term_repository=SQLAlchemyLongTermMemoryRepository(session))
        service.remember(student_id, MemoryType(memory_type), data)


def retrieve_memory(student_id: UUID, limit: int = 20) -> list[dict]:
    with ai_data_session_scope(settings.database_url) as session:
        service = MemoryService(long_term_repository=SQLAlchemyLongTermMemoryRepository(session))
        entries = service.recall(student_id, limit=limit)

    return [
        {"type": entry.memory_type.value, "data": entry.memory_data, "created_at": entry.created_at}
        for entry in entries
    ]
