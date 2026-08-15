"""Analytics Agent — AI_Agent_architecture.txt §4.4 / Agents.txt.

Turns raw response history into a narrative progress summary (the numbers
behind Agent_workflows.txt §9's weekly review). Available for the backend
to enrich `/progress/report`'s `recommendation` field beyond the plain
numbers `progress_service.py` already computes from `learning_sessions`.
"""

from __future__ import annotations

from pydantic import ValidationError

from ai_data.models.assessment import QuestionResponse
from ai_data.services.performance_analyzer import estimate_learning_progress

from ai_agents.agents.base import BaseAgent
from ai_agents.prompts.analytics import build_analytics_prompt
from ai_agents.schemas import AnalyticsResult

_TREND_LABELS = {
    "improving": "improving",
    "declining": "declining",
    "steady": "holding steady",
}


class AnalyticsAgent(BaseAgent):
    name = "Analytics Agent"

    def run(self, responses: list[QuestionResponse]) -> AnalyticsResult:
        progress = estimate_learning_progress(responses)

        system, user = build_analytics_prompt(progress)
        raw = self._try_llm(system, user)
        if raw is not None:
            try:
                return AnalyticsResult(**raw, source="llm")
            except (ValidationError, TypeError):
                pass

        return self._fallback(progress)

    def _fallback(self, progress: dict) -> AnalyticsResult:
        if progress["total_questions"] == 0:
            return AnalyticsResult(
                summary="Not enough activity yet to show a trend — complete a few questions first.",
                trend="insufficient_data",
                accuracy_change=0.0,
                source="deterministic",
            )

        change = progress["accuracy_change"]
        trend = "improving" if change >= 0.1 else "declining" if change <= -0.1 else "steady"
        summary = (
            f"Across {progress['total_questions']} questions, accuracy moved from "
            f"{progress['earliest_accuracy']:.0%} to {progress['latest_accuracy']:.0%} "
            f"({_TREND_LABELS[trend]})."
        )
        return AnalyticsResult(summary=summary, trend=trend, accuracy_change=change, source="deterministic")
