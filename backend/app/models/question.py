"""`questions` table — Database_design.txt §5.4.

Field names/shape match `ai_data.models.question.Question` closely on
purpose (subject/topic/difficulty/question_text/answer_options/
correct_answer) so the adapter in `app/schemas/question.py` (Phase 2) is a
near-direct mapping rather than a translation layer.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import JSON, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base

_JSONType = JSON().with_variant(JSONB, "postgresql")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    subject: Mapped[str] = mapped_column(String, index=True)
    topic: Mapped[str] = mapped_column(String, index=True)
    difficulty: Mapped[int] = mapped_column(Integer)
    question_text: Mapped[str] = mapped_column(Text)
    answer_options: Mapped[dict] = mapped_column(_JSONType)
    correct_answer: Mapped[str] = mapped_column(String)
    # Added for frontend integration: QuestionCard renders an explanation
    # once the student answers, mirroring `ai_data.models.question.
    # Question.explanation`. Nullable so existing rows / callers that
    # don't set it don't break.
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
