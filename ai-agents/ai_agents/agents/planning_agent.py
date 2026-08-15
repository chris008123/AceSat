"""Planning Agent — AI_Agent_architecture.txt §4.2 / Agents.txt.

Turns diagnostic evidence into a concrete, time-boxed study plan, and
(via `suggest_mission_topic`) decides what a single learning session
should focus on (Api_design.txt §9's `mission` field).
"""

from __future__ import annotations

from pydantic import ValidationError

from ai_data.models.assessment import QuestionResponse
from ai_data.services.context_builder import StudentContext
from ai_data.services.performance_analyzer import identify_weak_topics
from ai_data.services.recommendation_context import generate_topic_recommendations

from ai_agents.agents.base import BaseAgent
from ai_agents.prompts.planning import build_planning_prompt
from ai_agents.schemas import StudyPlanItemResult, StudyPlanResult

# Higher-priority (lower `priority` number) recommendations get more
# minutes — same allocation the original ai_bridge.generate_study_plan
# used, kept here so the deterministic path's output doesn't change.
_MINUTES_BY_PRIORITY = {1: 20, 2: 15, 3: 10, 4: 5, 5: 5}
_DEFAULT_TOPIC_LABEL = "General Review"


class PlanningAgent(BaseAgent):
    name = "Planning Agent"

    def run(self, context: StudentContext, responses: list[QuestionResponse]) -> StudyPlanResult:
        system, user = build_planning_prompt(context)
        raw = self._try_llm(system, user)
        if raw is not None:
            try:
                items = [StudyPlanItemResult(**item) for item in raw["items"]]
                return StudyPlanResult(items=items, source="llm")
            except (ValidationError, KeyError, TypeError):
                pass
        return self._fallback(responses)

    def _fallback(self, responses: list[QuestionResponse]) -> StudyPlanResult:
        recommendations = generate_topic_recommendations(responses)
        items = [
            StudyPlanItemResult(
                topic=rec.topic or _DEFAULT_TOPIC_LABEL,
                duration_minutes=_MINUTES_BY_PRIORITY.get(rec.priority, 10),
                reason=rec.reason,
            )
            for rec in recommendations
        ]
        return StudyPlanResult(items=items, source="deterministic")

    def suggest_mission_topic(self, responses: list[QuestionResponse]) -> str | None:
        """The Planning Agent's answer to "what should today's session be
        about" — the weakest topic with enough evidence to trust, or
        `None` if there isn't one yet (caller falls back to a generic
        mission, per the original `ai_bridge.suggest_mission_topic`
        behavior).
        """
        if not responses:
            return None
        weak_topics = identify_weak_topics(responses)
        return weak_topics[0] if weak_topics else None
