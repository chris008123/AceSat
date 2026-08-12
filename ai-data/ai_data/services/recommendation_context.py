"""Recommendation data — hackathon prompt section 8.

Produces `Recommendation` objects with a concrete, numeric `reason` — this
is the piece the Prompt_strategy.txt doc leans on heavily ("Every
recommendation must have a reason"). The AI Agent Engineer's Planning Agent
decides *when* to call this and how to phrase it to the student; this
module only decides *what* the evidence supports.
"""

from __future__ import annotations

from ai_data.models.assessment import QuestionResponse
from ai_data.models.enums import MasteryTrend, RecommendationAction
from ai_data.models.recommendation import Recommendation
from ai_data.services.performance_analyzer import calculate_topic_mastery


def generate_topic_recommendations(
    responses: list[QuestionResponse],
    max_recommendations: int = 3,
) -> list[Recommendation]:
    """One recommendation per topic that needs attention, ordered by
    priority (weak + declining topics first).
    """
    mastery = calculate_topic_mastery(responses)
    recommendations: list[Recommendation] = []

    for topic, stats in mastery.items():
        trend = MasteryTrend(stats["trend"])
        accuracy = stats["accuracy"]
        recent_accuracy = stats["recent_accuracy"]

        if trend == MasteryTrend.DECLINING:
            reason = (
                f"Accuracy on {topic} dropped from {accuracy:.0%} overall to "
                f"{recent_accuracy:.0%} over the last {min(stats['attempts'], 5)} attempts."
            )
            recommendations.append(
                Recommendation(
                    action=RecommendationAction.PRACTICE_TOPIC,
                    topic=topic,
                    reason=reason,
                    supporting_evidence=stats,
                    priority=1,
                )
            )
        elif trend == MasteryTrend.WEAK:
            reason = f"{topic} accuracy is {accuracy:.0%} across {stats['attempts']} attempts, below the 60% mastery threshold."
            recommendations.append(
                Recommendation(
                    action=RecommendationAction.REVIEW_CONCEPT,
                    topic=topic,
                    reason=reason,
                    supporting_evidence=stats,
                    priority=2,
                )
            )
        elif trend == MasteryTrend.IMPROVING and accuracy >= 0.85:
            reason = f"{topic} accuracy reached {accuracy:.0%} and is improving — ready for harder questions."
            recommendations.append(
                Recommendation(
                    action=RecommendationAction.INCREASE_DIFFICULTY,
                    topic=topic,
                    reason=reason,
                    supporting_evidence=stats,
                    priority=3,
                )
            )

    recommendations.sort(key=lambda r: r.priority)
    return recommendations[:max_recommendations]
