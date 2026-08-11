"""AI Context Builder — hackathon prompt section 7.

This is the single interface the AI Agent Engineer's prompts should call
into. It deliberately returns a small, task-relevant slice of the
student's data — not their entire history — per both the prompt's section 7
instruction and the memory-selectivity instruction in section 6.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ai_data.models.recommendation import Recommendation
from ai_data.models.student import StudentLearningProfile


class StudentContext(BaseModel):
    """Matches the shape shown in Prompt_strategy.txt §12 (context
    injection) and the hackathon prompt's `student_context` example."""

    student_id: str
    goal: int
    current_score: int | None
    weak_topics: list[str]
    strong_topics: list[str]
    recent_performance: dict = Field(default_factory=dict)
    recommended_focus: list[str]
    active_recommendations: list[Recommendation] = Field(default_factory=list)


def build_student_context(
    profile: StudentLearningProfile,
    recommendations: list[Recommendation] | None = None,
) -> StudentContext:
    """Build the context object handed to an agent prompt for a given task.

    Only pulls from the already-computed `StudentLearningProfile` — this
    function does no analysis itself, it shapes what's already known into
    the minimal payload a prompt needs.
    """
    recent_performance = {
        snapshot.subject.value: {
            "accuracy": snapshot.accuracy,
            "questions_attempted": snapshot.questions_attempted,
        }
        for snapshot in profile.recent_performance
    }

    return StudentContext(
        student_id=str(profile.student_id),
        goal=profile.target_score,
        current_score=profile.current_estimated_score,
        weak_topics=profile.weak_topics,
        strong_topics=profile.strong_topics,
        recent_performance=recent_performance,
        recommended_focus=profile.recommended_focus_areas,
        active_recommendations=recommendations or [],
    )
