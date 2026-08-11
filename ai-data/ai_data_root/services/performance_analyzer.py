"""Performance analysis — hackathon prompt section 5.

Pure functions over `QuestionResponse` lists. No DB or API calls in here on
purpose: keeps this layer trivially unit-testable and reusable from the
Diagnostic Agent, Analytics Agent, or a batch job, per the "modular and
testable" instruction.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from ai_data.models.assessment import QuestionResponse
from ai_data.models.enums import MasteryTrend

# Below this many attempts on a topic, trend/mastery numbers are considered
# too noisy to act on with confidence. Tunable, not a magic constant hidden
# elsewhere — surfaced here so the Diagnostic Agent's prompt can reference it.
MIN_ATTEMPTS_FOR_CONFIDENT_TREND = 5
RECENT_WINDOW_SIZE = 5


def calculate_accuracy(responses: list[QuestionResponse]) -> float:
    """Fraction correct, 0.0 if no responses (not NaN — callers can treat
    an empty list as 'no data yet' distinctly if they check length)."""
    if not responses:
        return 0.0
    return sum(1 for r in responses if r.correct) / len(responses)


def _group_by_topic(responses: list[QuestionResponse]) -> dict[str, list[QuestionResponse]]:
    grouped: dict[str, list[QuestionResponse]] = defaultdict(list)
    for r in responses:
        grouped[r.topic].append(r)
    return grouped


def calculate_topic_mastery(
    responses: list[QuestionResponse],
) -> dict[str, dict[str, float | int | str | datetime | None]]:
    """Per-topic mastery summary. Returns raw numbers (used by
    `mastery_engine.py` to build `TopicMastery` objects) rather than the
    Pydantic model directly, so this stays a small composable function.
    """
    results: dict[str, dict] = {}
    for topic, topic_responses in _group_by_topic(responses).items():
        sorted_responses = sorted(topic_responses, key=lambda r: r.answered_at)
        attempts = len(sorted_responses)
        correct = sum(1 for r in sorted_responses if r.correct)
        accuracy = correct / attempts if attempts else 0.0

        recent = sorted_responses[-RECENT_WINDOW_SIZE:]
        recent_accuracy = calculate_accuracy(recent)

        # Weight each response by difficulty so getting hard questions right
        # counts for more than getting easy ones right.
        difficulty_weighted_correct = sum(r.difficulty.value for r in sorted_responses if r.correct)
        difficulty_weighted_total = sum(r.difficulty.value for r in sorted_responses)
        difficulty_adjusted = (
            difficulty_weighted_correct / difficulty_weighted_total if difficulty_weighted_total else 0.0
        )

        results[topic] = {
            "attempts": attempts,
            "correct_answers": correct,
            "accuracy": round(accuracy, 4),
            "recent_accuracy": round(recent_accuracy, 4),
            "difficulty_adjusted_performance": round(difficulty_adjusted, 4),
            "mastery_score": round((accuracy + difficulty_adjusted) / 2, 4),
            "confidence": round(min(attempts / MIN_ATTEMPTS_FOR_CONFIDENT_TREND, 1.0), 4),
            "last_practiced": sorted_responses[-1].answered_at,
            "trend": calculate_performance_trend(sorted_responses).value,
        }
    return results


def identify_weak_topics(
    responses: list[QuestionResponse],
    threshold: float = 0.6,
    min_attempts: int = 3,
) -> list[str]:
    """Topics with accuracy below `threshold`. Topics with fewer than
    `min_attempts` are excluded — not enough evidence yet, so we shouldn't
    label a topic "weak" off one unlucky question.
    """
    mastery = calculate_topic_mastery(responses)
    weak = [
        topic
        for topic, stats in mastery.items()
        if stats["attempts"] >= min_attempts and stats["accuracy"] < threshold
    ]
    # Weakest first — most useful ordering for a Diagnostic Agent picking
    # what to surface first.
    weak.sort(key=lambda t: mastery[t]["accuracy"])
    return weak


def identify_strong_topics(
    responses: list[QuestionResponse],
    threshold: float = 0.8,
    min_attempts: int = 3,
) -> list[str]:
    mastery = calculate_topic_mastery(responses)
    strong = [
        topic
        for topic, stats in mastery.items()
        if stats["attempts"] >= min_attempts and stats["accuracy"] >= threshold
    ]
    strong.sort(key=lambda t: mastery[t]["accuracy"], reverse=True)
    return strong


def calculate_performance_trend(
    responses: list[QuestionResponse],
    window_size: int = RECENT_WINDOW_SIZE,
) -> MasteryTrend:
    """Compares accuracy in the most recent window against the window
    before it. Requires enough history in both windows to call a trend —
    otherwise returns INSUFFICIENT_DATA rather than guessing.
    """
    sorted_responses = sorted(responses, key=lambda r: r.answered_at)
    if len(sorted_responses) < window_size * 2:
        return MasteryTrend.INSUFFICIENT_DATA

    recent_window = sorted_responses[-window_size:]
    previous_window = sorted_responses[-window_size * 2 : -window_size]

    recent_accuracy = calculate_accuracy(recent_window)
    previous_accuracy = calculate_accuracy(previous_window)
    delta = recent_accuracy - previous_accuracy

    if recent_accuracy < 0.5 and delta <= 0:
        return MasteryTrend.WEAK
    if delta >= 0.1:
        return MasteryTrend.IMPROVING
    if delta <= -0.1:
        return MasteryTrend.DECLINING
    return MasteryTrend.STABLE


def estimate_learning_progress(
    responses: list[QuestionResponse],
    window_size: int = RECENT_WINDOW_SIZE,
) -> dict[str, float | int]:
    """Overall (not per-topic) progress summary — the numbers behind a
    weekly-review-style report (Agent_workflows.txt §9)."""
    sorted_responses = sorted(responses, key=lambda r: r.answered_at)
    if not sorted_responses:
        return {
            "total_questions": 0,
            "overall_accuracy": 0.0,
            "earliest_accuracy": 0.0,
            "latest_accuracy": 0.0,
            "accuracy_change": 0.0,
        }

    earliest_window = sorted_responses[:window_size]
    latest_window = sorted_responses[-window_size:]

    earliest_accuracy = calculate_accuracy(earliest_window)
    latest_accuracy = calculate_accuracy(latest_window)

    return {
        "total_questions": len(sorted_responses),
        "overall_accuracy": round(calculate_accuracy(sorted_responses), 4),
        "earliest_accuracy": round(earliest_accuracy, 4),
        "latest_accuracy": round(latest_accuracy, 4),
        "accuracy_change": round(latest_accuracy - earliest_accuracy, 4),
    }
