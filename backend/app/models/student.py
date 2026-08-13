"""`student_profiles` table — Database_design.txt §5.2.

This is the row `ai_data.services.student_profile.generate_student_profile()`
reads from (as its `Student` Pydantic model) — see `app/schemas/student.py`
(Phase 2) for the adapter between this ORM row and that Pydantic shape.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid

from app.database.connection import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), unique=True, index=True)

    target_score: Mapped[int] = mapped_column(Integer)
    current_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    study_time_daily: Mapped[int] = mapped_column(Integer)
    confidence_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    learning_style: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship(back_populates="student_profile")
