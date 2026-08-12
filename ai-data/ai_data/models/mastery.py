"""Topic mastery representation.

Maps to hackathon prompt section 4 ("Topic Mastery"). Not present as its own
table in 10_Database_Design.md (the closest is the coarser `progress_records`,
which tracks per-subject score/mastery_level over time, not per-topic
attempts/accuracy/trend) — proposed here as a new AI/Data-owned table.
Confirm with Backend Engineer before running the migration.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ai_data.models.base import Base
from ai_data.models.enums import MasteryTrend


class TopicMastery(BaseModel):
    """Computed, not hand-entered — `services/mastery_engine.py` (Phase 2)
    is the only thing that should produce these. Never hard-code values,
    per the prompt's explicit instruction in section 4."""

    student_id: UUID
    topic: str
    attempts: int = Field(ge=0)
    correct_answers: int = Field(ge=0)
    accuracy: float = Field(ge=0.0, le=1.0)
    recent_accuracy: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Accuracy over the most recent window only"
    )
    difficulty_adjusted_performance: float | None = Field(
        default=None,
        description="Accuracy weighted by question difficulty; higher than raw "
        "accuracy means the student is doing well on harder questions.",
    )
    mastery_score: float = Field(ge=0.0, le=1.0)
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How much to trust this mastery score, based on sample size "
        "— low attempt counts should report low confidence, not a misleadingly "
        "precise mastery_score.",
    )
    last_practiced: datetime | None = None
    trend: MasteryTrend = MasteryTrend.INSUFFICIENT_DATA


class TopicMasteryRecord(Base):
    """Persisted snapshot of a `TopicMastery` computation.

    Storing snapshots (rather than only computing on the fly) lets the
    Analytics Agent and progress dashboard show mastery-over-time without
    recomputing from the full `answers` history on every request.
    """

    __tablename__ = "topic_mastery"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    # No SQLAlchemy ForeignKey object here on purpose: `student_profiles` is
    # a backend-owned table not defined in this module's metadata (see
    # README boundary note), so this Base can't resolve a cross-module FK.
    # Once both Bases share one Alembic migration chain, the Backend
    # Engineer should add the actual FK constraint at the DB level.
    student_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    topic: Mapped[str] = mapped_column(String, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    recent_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    difficulty_adjusted_performance: Mapped[float | None] = mapped_column(Float, nullable=True)
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_practiced: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trend: Mapped[str] = mapped_column(String, default=MasteryTrend.INSUFFICIENT_DATA.value)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
