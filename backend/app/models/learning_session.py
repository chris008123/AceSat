"""`learning_sessions` table — Database_design.txt §5.7.

Distinct from `Assessment`/`Answer`: an assessment is the diagnostic test;
a learning session is a regular practice session afterward (per
Api_design.txt §9 "Start Session" / "Complete Session" and
Backend_architecture.txt §12's post-lesson flow: Learning Service ->
Database Update -> Analytics Agent -> Planning Agent -> New
Recommendation).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("student_profiles.id"), index=True)
    mission: Mapped[str | None] = mapped_column(String, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    questions_completed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
