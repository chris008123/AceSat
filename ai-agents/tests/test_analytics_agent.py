from __future__ import annotations

from ai_agents.agents.analytics_agent import AnalyticsAgent


def test_analytics_reports_insufficient_data_with_no_history():
    agent = AnalyticsAgent(llm_client=None)
    result = agent.run([])

    assert result.trend == "insufficient_data"
    assert result.accuracy_change == 0.0
    assert result.summary


def test_analytics_summarizes_mixed_history(mixed_responses):
    agent = AnalyticsAgent(llm_client=None)
    result = agent.run(mixed_responses)

    assert result.trend in {"improving", "declining", "steady"}
    assert str(len(mixed_responses)) in result.summary


def test_analytics_llm_path_used_when_client_available(mixed_responses):
    class _StubClient:
        def generate_json(self, system_prompt, user_prompt):
            return {
                "summary": "Accuracy is trending upward across recent sessions.",
                "trend": "improving",
                "accuracy_change": 0.12,
            }

    agent = AnalyticsAgent(llm_client=_StubClient())
    result = agent.run(mixed_responses)

    assert result.source == "llm"
    assert result.trend == "improving"
