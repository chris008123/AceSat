from __future__ import annotations

import pytest

from ai_agents.agents.coaching_agent import CoachingAgent
from ai_agents.context import build_context
from ai_agents.errors import NoTeachingMaterialError


def test_coach_returns_teaching_material_for_weak_topic(demo_student, declining_reading_inference_responses):
    context = build_context(demo_student, declining_reading_inference_responses)
    agent = CoachingAgent(llm_client=None)

    result = agent.run(context, declining_reading_inference_responses, "I don't get this")

    assert result.explanation
    assert result.source == "deterministic"


def test_coach_with_no_history_gives_fallback_and_no_next_question(demo_student):
    context = build_context(demo_student, [])
    agent = CoachingAgent(llm_client=None)

    result = agent.run(context, [], "help")

    assert result.next_question is None
    assert result.explanation


def test_coach_raises_when_weak_topic_has_no_teaching_material(demo_student, student_id):
    from datetime import datetime, timedelta

    from ai_data.models.assessment import QuestionResponse
    from ai_data.models.enums import ConfidenceLevel, DifficultyLevel, Subject

    # "Geometry" isn't in ai-data's sample knowledge base — a weak topic
    # with no matching concept, per ai-data's own note that
    # get_concepts_for_topic() only covers Reading Inference / Linear
    # Equations / Grammar today.
    responses = [
        QuestionResponse(
            response_id=student_id,
            student_id=student_id,
            question_id=student_id,
            topic="Geometry",
            subject=Subject.MATH,
            difficulty=DifficultyLevel.INTERMEDIATE,
            answer_given="A",
            correct=False,
            confidence=ConfidenceLevel.LOW,
            response_time_seconds=30,
            answered_at=datetime.utcnow() - timedelta(days=i),
        )
        for i in range(5)
    ]
    context = build_context(demo_student, responses)
    agent = CoachingAgent(llm_client=None)

    with pytest.raises(NoTeachingMaterialError):
        agent.run(context, responses, "help with geometry")


def test_coach_llm_path_used_when_client_available(demo_student, declining_reading_inference_responses):
    class _StubClient:
        def generate_json(self, system_prompt, user_prompt):
            return {
                "explanation": "Let's look at what the passage directly states.",
                "next_question": "Which sentence supports that idea?",
            }

    context = build_context(demo_student, declining_reading_inference_responses)
    agent = CoachingAgent(llm_client=_StubClient())

    result = agent.run(context, declining_reading_inference_responses, "I don't get this")

    assert result.source == "llm"
    assert result.next_question == "Which sentence supports that idea?"
