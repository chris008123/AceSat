"""Planning Agent output contract — AI_Agent_architecture.txt §4.2 /
hackathon prompt's Planning Agent section.

Input to the agent producing this is a `DiagnosticResult` plus
`StudentContext` (exam date, available study time, goal) — output-only
shape here, per Phase 1 scope.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class StudyPlanItem(BaseModel):
    """One scheduled activity. `reason` is required on every item —
    Prompt_strategy.txt §6 is explicit: 'Do not create generic schedules.
    Every recommendation must have a reason.'
    """

    day: str = Field(description="e.g. 'Monday', or an ISO date string for a dated plan.")
    topic: str
    duration_minutes: int = Field(gt=0, le=240)
    activity: str = Field(description="e.g. 'Practice', 'Review lesson', 'Timed drill'.")
    reason: str = Field(description="Concrete reason this activity was scheduled, e.g. "
                         "'accuracy on this topic is 48%, below the 60% mastery threshold'.")


class StudyPlan(BaseModel):
    """Structured output of the Planning Agent — matches the hackathon
    prompt's Planning Agent JSON example (goal / priority_topics /
    weekly_plan)."""

    student_id: UUID
    goal: str = Field(description="e.g. 'Improve SAT Math from 1050 to 1400'.")
    priority_topics: list[str] = Field(default_factory=list)
    weekly_plan: list[StudyPlanItem] = Field(default_factory=list)

    total_weekly_minutes: int | None = Field(
        default=None, description="Sum of weekly_plan durations — informational, not "
        "authoritative; recompute from weekly_plan rather than trusting this blindly."
    )
    exam_date: date | None = None

    plan_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
