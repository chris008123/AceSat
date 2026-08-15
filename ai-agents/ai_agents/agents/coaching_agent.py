"""Coaching Agent — AI_Agent_architecture.txt §4.3 / Agents.txt.

Acts as the student's personal instructor: explains, guides, never just
hands over answers (Prompt_strategy.txt §7-8).
"""

from __future__ import annotations

from pydantic import ValidationError

from ai_data.knowledge.concepts import Concept
from ai_data.knowledge.loader import get_concepts_for_topic
from ai_data.models.assessment import QuestionResponse
from ai_data.services.context_builder import StudentContext

from ai_agents.agents.base import BaseAgent
from ai_agents.errors import NoTeachingMaterialError
from ai_agents.prompts.coaching import build_coaching_prompt
from ai_agents.schemas import CoachResult

_NO_HISTORY_MESSAGE = (
    "I don't have enough practice history yet to tailor this — try a few "
    "more questions first, or ask about a specific topic."
)


class CoachingAgent(BaseAgent):
    name = "Coaching Agent"

    def run(
        self, context: StudentContext, responses: list[QuestionResponse], question: str
    ) -> CoachResult:
        if not context.weak_topics:
            return CoachResult(explanation=_NO_HISTORY_MESSAGE, next_question=None, source="deterministic")

        topic = context.weak_topics[0]
        concepts = get_concepts_for_topic(topic)
        concept = concepts[0] if concepts else None

        system, user = build_coaching_prompt(context, question, concept)
        raw = self._try_llm(system, user)
        if raw is not None:
            try:
                return CoachResult(**raw, source="llm")
            except (ValidationError, TypeError):
                pass

        return self._fallback(topic, concept)

    def _fallback(self, topic: str, concept: Concept | None) -> CoachResult:
        if concept is None:
            raise NoTeachingMaterialError(topic)
        next_question = concept.examples[0].prompt if concept.examples else None
        return CoachResult(explanation=concept.explanation, next_question=next_question, source="deterministic")
