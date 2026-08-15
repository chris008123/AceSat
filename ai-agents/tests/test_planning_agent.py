from __future__ import annotations

from ai_agents.agents.planning_agent import PlanningAgent
from ai_agents.context import build_context


def test_plan_prioritizes_weak_topic(demo_student, declining_reading_inference_responses):
    context = build_context(demo_student, declining_reading_inference_responses)
    agent = PlanningAgent(llm_client=None)

    result = agent.run(context, declining_reading_inference_responses)

    assert result.items
    assert result.items[0].topic == "Reading Inference"
    assert result.items[0].duration_minutes > 0
    assert result.items[0].reason
    assert result.source == "deterministic"


def test_plan_with_no_data_returns_empty_plan(demo_student):
    context = build_context(demo_student, [])
    agent = PlanningAgent(llm_client=None)

    result = agent.run(context, [])

    assert result.items == []


def test_suggest_mission_topic_reflects_weak_topic(demo_student, declining_reading_inference_responses):
    agent = PlanningAgent(llm_client=None)
    assert agent.suggest_mission_topic(declining_reading_inference_responses) == "Reading Inference"


def test_suggest_mission_topic_with_no_history_returns_none():
    agent = PlanningAgent(llm_client=None)
    assert agent.suggest_mission_topic([]) is None


def test_plan_llm_path_used_when_client_available(demo_student, declining_reading_inference_responses):
    class _StubClient:
        def generate_json(self, system_prompt, user_prompt):
            return {
                "items": [
                    {"topic": "Reading Inference", "duration_minutes": 20, "reason": "weakest topic"},
                ]
            }

    context = build_context(demo_student, declining_reading_inference_responses)
    agent = PlanningAgent(llm_client=_StubClient())

    result = agent.run(context, declining_reading_inference_responses)

    assert result.source == "llm"
    assert result.items[0].duration_minutes == 20
