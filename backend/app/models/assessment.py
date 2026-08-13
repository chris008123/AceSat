"""`assessments` / `answers` tables — Database_design.txt §5.3, §5.5.

`Answer.confidence` and `.response_time` power the "AI Confidence System"
the design doc calls out — stored here, read by
`app/services/ai_bridge.py` when building `ai_data.models.assessment.
QuestionResponse` objects for the AI/Data layer.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("student_profiles.id"), index=True)
    assessment_type: Mapped[str] = mapped_column(String, default="diagnostic")
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    answers: Mapped[list["Answer"]] = relationship(back_populates="assessment")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    assessment_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("assessments.id"), index=True)
    student_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("student_profiles.id"), index=True)
    question_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("questions.id"), index=True)
    answer_given: Mapped[str] = mapped_column(String)
    correct: Mapped[bool] = mapped_column(Boolean)
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assessment: Mapped["Assessment"] = relationship(back_populates="answers")
