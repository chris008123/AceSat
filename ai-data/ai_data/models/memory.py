"""AI memory representation — hackathon prompt section 6 ("Student Memory")
and 10_Database_Design.md §5.9 (`ai_memory`) / §5.10 (`ai_logs`).

Split into short-term (current session, not persisted to Postgres — kept in
whatever session cache the Backend Engineer chooses, e.g. Redis) and
long-term (persisted, retrieved selectively — never the student's entire
history on every request, per the prompt's explicit instruction).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import JSON, DateTime, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ai_data.models.base import Base
from ai_data.models.enums import MemoryType

# Generic types that render correctly on both Postgres (production) and
# SQLite (local dev / tests, see models/db.py) — `Uuid` maps to native
# UUID on Postgres and CHAR(32) on SQLite; the JSON variant maps to JSONB
# on Postgres and JSON (TEXT-backed) on SQLite.
_JSONType = JSON().with_variant(JSONB, "postgresql")


class ShortTermMemory(BaseModel):
    """Current session state only. Not a DB table — session-cache shaped
    (e.g. Redis, or an in-memory dict during a hackathon demo)."""

    student_id: UUID
    current_question_id: UUID | None = None
    current_topic: str | None = None
    recent_mistakes: list[str] = Field(
        default_factory=list, description="Topic names from the last few incorrect answers"
    )
    conversation_summary: str | None = Field(
        default=None, description="Short running summary, not the full transcript"
    )
    session_started_at: datetime = Field(default_factory=datetime.utcnow)


class LongTermMemoryEntry(BaseModel):
    """One row of `ai_memory`. `memory_data` shape depends on `memory_type`
    (see hackathon prompt §6 for the four categories: academic, behavior,
    preference/goal)."""

    memory_id: UUID = Field(default_factory=uuid4)
    student_id: UUID
    memory_type: MemoryType
    memory_data: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AIDecisionLog(BaseModel):
    """One row of `ai_logs` — records what an agent decided and why, so
    recommendations stay explainable (prompt §8)."""

    log_id: UUID = Field(default_factory=uuid4)
    student_id: UUID
    agent_name: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AIMemoryRecord(Base):
    __tablename__ = "ai_memory"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    # See mastery.py comment: no cross-module FK object until Bases merge.
    student_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    memory_type: Mapped[str] = mapped_column(String, index=True)
    memory_data: Mapped[dict] = mapped_column(_JSONType)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AILogRecord(Base):
    __tablename__ = "ai_logs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    # See mastery.py comment: no cross-module FK object until Bases merge.
    student_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    agent_name: Mapped[str] = mapped_column(String, index=True)
    input_data: Mapped[dict] = mapped_column(_JSONType)
    output_data: Mapped[dict] = mapped_column(_JSONType)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
