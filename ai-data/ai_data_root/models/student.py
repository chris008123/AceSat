"""Student-facing data structures.

`Student` is a thin read model over the backend's `users` /
`student_profiles` tables (see README boundary note) — this module does not
own those tables, it just needs a typed shape to build profiles/context
from. `StudentLearningProfile` is the AI/Data-owned output described in the
hackathon prompt section "1. Student Learning Profile".
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ai_data.models.enums import Subject
from ai_data.models.mastery import TopicMastery


class Student(BaseModel):
    """Read model of `student_profiles` (+ the linked `users` row).

    Intentionally excludes anything not needed for AI personalization
    (no email, no password hash) per the prompt's "avoid storing
    unnecessary sensitive personal information" instruction.
    """

    student_id: UUID
    target_score: int = Field(gt=0, le=1600)
    current_score: int | None = Field(default=None, ge=0, le=1600)
    exam_date: date | None = None
    study_time_daily_minutes: int = Field(gt=0)
    confidence_level: int | None = Field(default=None, ge=1, le=5)
    learning_style: str | None = None


class RecentPerformanceSnapshot(BaseModel):
    """Rolling summary used inside a learning profile — not a table,
    computed by the performance engine (Phase 2)."""

    subject: Subject
    accuracy: float = Field(ge=0.0, le=1.0)
    questions_attempted: int = Field(ge=0)
    window_description: str = "last 20 responses"


class StudentLearningProfile(BaseModel):
    """The structured representation of a student's learning state.

    Maps directly to hackathon prompt section 1. This is what
    `services/student_profile.py` (Phase 3) produces and what
    `services/recommendation_context.py` / the AI Context Builder
    (Phase 4) consume.
    """

    student_id: UUID
    target_score: int
    current_estimated_score: int | None = None
    available_study_time_minutes: int
    exam_date: date | None = None

    strong_topics: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    topic_mastery: list[TopicMastery] = Field(default_factory=list)

    recent_performance: list[RecentPerformanceSnapshot] = Field(default_factory=list)
    confidence: int | None = Field(default=None, ge=1, le=5)
    study_consistency: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Fraction of expected study sessions actually completed, "
        "over a recent window.",
    )

    recommended_focus_areas: list[str] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=datetime.utcnow)
