"""Assessment attempt + response data structures.

Read models over the backend-owned `assessments` / `answers` tables
(10_Database_Design.md §5.3, §5.5). The AI/Data layer needs these shapes as
input to the performance engine (Phase 2) — it does not own writing them.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ai_data.models.enums import ConfidenceLevel, DifficultyLevel, Subject


class QuestionResponse(BaseModel):
    """One row of `answers`."""

    response_id: UUID
    student_id: UUID
    question_id: UUID
    topic: str
    subject: Subject
    difficulty: DifficultyLevel
    answer_given: str
    correct: bool
    confidence: ConfidenceLevel | None = None
    response_time_seconds: int | None = Field(default=None, ge=0)
    answered_at: datetime


class AssessmentAttempt(BaseModel):
    """One row of `assessments`, with its responses attached so the
    performance engine can reconstruct exactly what happened, per the
    prompt's "3. Assessment Data" requirement."""

    assessment_id: UUID
    student_id: UUID
    assessment_type: str = Field(description="e.g. 'diagnostic', 'practice_set'")
    responses: list[QuestionResponse] = Field(default_factory=list)
    score: float | None = None
    duration_seconds: int | None = Field(default=None, ge=0)
    completed_at: datetime | None = None

    @property
    def total_questions(self) -> int:
        return len(self.responses)

    @property
    def correct_count(self) -> int:
        return sum(1 for r in self.responses if r.correct)
