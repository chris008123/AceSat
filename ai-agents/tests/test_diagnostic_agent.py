from __future__ import annotations

from ai_agents.agents.diagnostic_agent import DiagnosticAgent
from ai_agents.context import build_context


def test_diagnose_identifies_declining_weak_topic(demo_student, declining_reading_inference_responses):
    context = build_context(demo_student, declining_reading_inference_responses)
    agent = DiagnosticAgent(llm_client=None)  # no client configured -> deterministic path

    result = agent.run(context, declining_reading_inference_responses)

    assert "Reading Inference" in result.weaknesses
    assert "%" in result.recommendation
    assert result.source == "deterministic"


def test_diagnose_surfaces_strong_topic(demo_student, strong_algebra_responses):
    context = build_context(demo_student, strong_algebra_responses)
    agent = DiagnosticAgent(llm_client=None)

    result = agent.run(context, strong_algebra_responses)

    assert "Linear Equations" in result.strengths


def test_diagnose_with_no_responses_falls_back_gracefully(demo_student):
    context = build_context(demo_student, [])
    agent = DiagnosticAgent(llm_client=None)

    result = agent.run(context, [])

    assert result.weaknesses == []
    assert result.strengths == []
    assert result.recommendation  # still a non-empty, honest fallback message
    assert result.source == "deterministic"


def test_diagnose_llm_path_used_when_client_available(demo_student, declining_reading_inference_responses):
    class _StubClient:
        def generate_json(self, system_prompt, user_prompt):
            return {
                "strengths": ["Vocabulary"],
                "weaknesses": ["Reading Inference"],
                "reason": "accuracy dropped to 40% over the last 5 attempts",
                "recommendation": "Add a 15-minute inference drill daily",
            }

    context = build_context(demo_student, declining_reading_inference_responses)
    agent = DiagnosticAgent(llm_client=_StubClient())

    result = agent.run(context, declining_reading_inference_responses)

    assert result.source == "llm"
    assert result.recommendation == "Add a 15-minute inference drill daily"


def test_diagnose_falls_back_when_llm_returns_malformed_json(
    demo_student, declining_reading_inference_responses
):
    class _BrokenClient:
        def generate_json(self, system_prompt, user_prompt):
            return {"not_the_expected_shape": True}

    context = build_context(demo_student, declining_reading_inference_responses)
    agent = DiagnosticAgent(llm_client=_BrokenClient())

    result = agent.run(context, declining_reading_inference_responses)

    assert result.source == "deterministic"
    assert "Reading Inference" in result.weaknesses


def test_diagnose_falls_back_when_llm_raises(demo_student, declining_reading_inference_responses):
    class _ExplodingClient:
        def generate_json(self, system_prompt, user_prompt):
            raise RuntimeError("network is down")

    context = build_context(demo_student, declining_reading_inference_responses)
    agent = DiagnosticAgent(llm_client=_ExplodingClient())

    result = agent.run(context, declining_reading_inference_responses)

    assert result.source == "deterministic"
