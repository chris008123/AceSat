"""Context assembly — the one place agents get the `StudentContext`
(ai-data Phase 4, `ai_data.services.context_builder`) they reason over.

This is intentionally a thin composition of ai-data's own Phase 2/3/4
services (`generate_student_profile`, `generate_topic_recommendations`,
`build_student_context`) — no new analysis happens here, per the ai-data
README's own instruction that this is "the single interface the AI Agent
Engineer's prompts should call into."
"""

from __future__ import annotations

from ai_data.models.assessment import QuestionResponse
from ai_data.models.student import Student
from ai_data.services.context_builder import StudentContext, build_student_context
from ai_data.services.recommendation_context import generate_topic_recommendations
from ai_data.services.student_profile import generate_student_profile


def build_context(
    student: Student,
    responses: list[QuestionResponse],
    study_consistency: float | None = None,
) -> StudentContext:
    profile = generate_student_profile(student, responses, study_consistency=study_consistency)
    recommendations = generate_topic_recommendations(responses) if responses else []
    return build_student_context(profile, recommendations)
