"""Student learning profile generator — hackathon prompt section 1, Phase 3
of the development order.

Composes `performance_analyzer` + `mastery_engine` output into a
`StudentLearningProfile`. Takes plain data in (not a DB session) so it can
be called from a FastAPI request handler, a background task, or a unit
test identically — the Backend Engineer decides how `student` and
`responses` get fetched.
"""

from __future__ import annotations

from ai_data.models.assessment import QuestionResponse
from ai_data.models.enums import Subject
from ai_data.models.student import RecentPerformanceSnapshot, Student, StudentLearningProfile
from ai_data.services.mastery_engine import build_topic_mastery
from ai_data.services.performance_analyzer import (
    calculate_accuracy,
    identify_strong_topics,
    identify_weak_topics,
)

# How many weak topics to surface as "recommended focus" — matches the
# Planning Agent examples in Agent_workflows.txt, which generally focus on
# 2-3 topics per day, not the student's entire weak-topic list at once.
DEFAULT_FOCUS_AREA_COUNT = 3


def generate_student_profile(
    student: Student,
    responses: list[QuestionResponse],
    study_consistency: float | None = None,
) -> StudentLearningProfile:
    """Build a `StudentLearningProfile` from a student's full response
    history. `study_consistency` is passed in rather than computed here
    because it depends on `learning_sessions` (backend-owned table, not a
    `QuestionResponse` concern) — the Backend Engineer supplies it.
    """
    topic_mastery = build_topic_mastery(student.student_id, responses)
    weak_topics = identify_weak_topics(responses)
    strong_topics = identify_strong_topics(responses)

    recent_performance = [
        RecentPerformanceSnapshot(
            subject=subject,
            accuracy=calculate_accuracy(
                [r for r in responses if r.subject == subject][-20:]
            ),
            questions_attempted=len([r for r in responses if r.subject == subject][-20:]),
        )
        for subject in Subject
        if any(r.subject == subject for r in responses)
    ]

    return StudentLearningProfile(
        student_id=student.student_id,
        target_score=student.target_score,
        current_estimated_score=student.current_score,
        available_study_time_minutes=student.study_time_daily_minutes,
        exam_date=student.exam_date,
        strong_topics=strong_topics,
        weak_topics=weak_topics,
        topic_mastery=topic_mastery,
        recent_performance=recent_performance,
        confidence=student.confidence_level,
        study_consistency=study_consistency,
        recommended_focus_areas=weak_topics[:DEFAULT_FOCUS_AREA_COUNT],
    )
