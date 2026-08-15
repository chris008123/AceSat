from __future__ import annotations

from ai_agents.agents.motivation_agent import MotivationAgent
from ai_agents.agents.reflection_agent import ReflectionAgent


def test_motivation_references_streak_number():
    agent = MotivationAgent(llm_client=None)
    result = agent.run(streak=7)

    assert "7" in result.message


def test_motivation_with_zero_streak_encourages_starting():
    agent = MotivationAgent(llm_client=None)
    result = agent.run(streak=0)

    assert result.message


def test_motivation_llm_path_used_when_client_available():
    class _StubClient:
        def generate_json(self, system_prompt, user_prompt):
            return {"message": "Ten days straight — that consistency is exactly what moves your score."}

    agent = MotivationAgent(llm_client=_StubClient())
    result = agent.run(streak=10)

    assert result.source == "llm"


def test_reflection_prompt_references_topic():
    agent = ReflectionAgent(llm_client=None)
    result = agent.run(topic="Reading Inference")

    assert "Reading Inference" in result.question
    assert result.options


def test_reflection_prompt_generic_without_topic():
    agent = ReflectionAgent(llm_client=None)
    result = agent.run()

    assert result.question
