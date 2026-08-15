"""Diagnostic Agent — AI_Agent_architecture.txt §4.1 / Agents.txt.

Understands the student's current academic state: strengths, weaknesses,
and the reasoning behind them.
"""

from __future__ import annotations

from pydantic import ValidationError

from ai_data.models.assessment import QuestionResponse
from ai_data.services.context_builder import StudentContext
from ai_data.services.recommendation_context import generate_topic_recommendations

from ai_agents.agents.base import BaseAgent
from ai_agents.prompts.diagnostic import build_diagnostic_prompt
from ai_agents.schemas import DiagnosticResult

_FALLBACK_RECOMMENDATION = "Keep practicing across all topics evenly."
_FALLBACK_REASON = "Not enough evidence yet to point to a specific gap — keep practicing."


class DiagnosticAgent(BaseAgent):
    name = "Diagnostic Agent"

    def run(self, context: StudentContext, responses: list[QuestionResponse]) -> DiagnosticResult:
        system, user = build_diagnostic_prompt(context)
        raw = self._try_llm(system, user)
        if raw is not None:
            try:
                return DiagnosticResult(**raw, source="llm")
            except (ValidationError, TypeError):
                pass  # malformed LLM output — fall through to the deterministic path
        return self._fallback(context, responses)

    def _fallback(
        self, context: StudentContext, responses: list[QuestionResponse]
    ) -> DiagnosticResult:
        """Rule-based diagnosis: identical evidence-based reasoning ai-data
        already implements in `performance_analyzer`/`recommendation_context`
        (both unit-tested there), just shaped into `DiagnosticResult`.
        """
        top_recommendation = generate_topic_recommendations(responses, max_recommendations=1)
        recommendation = top_recommendation[0].reason if top_recommendation else _FALLBACK_RECOMMENDATION
        reason = top_recommendation[0].reason if top_recommendation else _FALLBACK_REASON

        return DiagnosticResult(
            strengths=context.strong_topics,
            weaknesses=context.weak_topics,
            reason=reason,
            recommendation=recommendation,
            source="deterministic",
        )
