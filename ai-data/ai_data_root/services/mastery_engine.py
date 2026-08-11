"""Turns `performance_analyzer` output into `TopicMastery` model instances.

Kept separate from `performance_analyzer.py` so the analyzer stays pure
number-crunching (easy to unit test) while this layer owns shaping that
into the Pydantic model the rest of the system (profile builder, context
builder, dashboard) actually consumes.
"""

from __future__ import annotations

from uuid import UUID

from ai_data.models.assessment import QuestionResponse
from ai_data.models.enums import MasteryTrend
from ai_data.models.mastery import TopicMastery
from ai_data.services.performance_analyzer import calculate_topic_mastery


def build_topic_mastery(student_id: UUID, responses: list[QuestionResponse]) -> list[TopicMastery]:
    """One `TopicMastery` per topic the student has attempted."""
    raw = calculate_topic_mastery(responses)
    mastery_list: list[TopicMastery] = []
    for topic, stats in raw.items():
        mastery_list.append(
            TopicMastery(
                student_id=student_id,
                topic=topic,
                attempts=stats["attempts"],
                correct_answers=stats["correct_answers"],
                accuracy=stats["accuracy"],
                recent_accuracy=stats["recent_accuracy"],
                difficulty_adjusted_performance=stats["difficulty_adjusted_performance"],
                mastery_score=stats["mastery_score"],
                confidence=stats["confidence"],
                last_practiced=stats["last_practiced"],
                trend=MasteryTrend(stats["trend"]),
            )
        )
    # Weakest-first ordering is the most broadly useful default — callers
    # that want a different order (e.g. alphabetical for a dashboard) can
    # re-sort.
    mastery_list.sort(key=lambda m: m.mastery_score)
    return mastery_list
