"""Shared enums for agent output schemas.

Kept separate from `ai_data.models.enums` on purpose — these describe
*agent decisions/output shapes* (Coaching response type, Analytics status),
not the underlying student/performance data ai-data owns. Where an ai-data
enum already means the same thing (e.g. `Subject`), agents should reuse it
directly rather than duplicating it here.
"""

from __future__ import annotations

from enum import Enum


class InterventionUrgency(str, Enum):
    """Diagnostic Agent's `recommended_intervention` urgency — hackathon
    prompt's Diagnostic Agent output field of the same name, given a small
    closed vocabulary so the Planning Agent/orchestrator can branch on it
    instead of parsing free text."""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CoachingResponseType(str, Enum):
    """What kind of turn the Coaching Agent is making — matches the
    Explain / Guide / Practice / Confirm framework in
    Prompt_strategy.txt §8."""

    EXPLANATION = "explanation"
    HINT = "hint"
    GUIDING_QUESTION = "guiding_question"
    FEEDBACK = "feedback"
    ENCOURAGEMENT = "encouragement"


class AnalyticsStatus(str, Enum):
    """Matches the hackathon prompt's Analytics Agent output vocabulary
    (section 4 / 4.4): Improving, Declining, Stable, Needs intervention,
    Ready for harder questions, Needs reinforcement."""

    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    NEEDS_INTERVENTION = "needs_intervention"
    READY_FOR_HARDER_QUESTIONS = "ready_for_harder_questions"
    NEEDS_REINFORCEMENT = "needs_reinforcement"
