"""Phase 2 tests: Diagnostic Agent behavior against a fake `complete_fn`
returning canned JSON — no real GROQ_API_KEY or network access needed. This
proves the agent's plumbing (prompt building, response parsing, schema
validation, priority_topics enforcement) is correct independent of Groq
itself.
"""

from __future__ import annotations

import json
from uuid import uuid4

import pytest

from ai_data.services.context_builder import StudentContext

from ai_agents.agents.diagnostic_agent import DiagnosticAgent, DiagnosticAgentError
from ai_agents.schemas.enums import InterventionUrgency


def _make_context(**overrides) -> StudentContext:
    defaults = dict(
        student_id=str(uuid4()),
        goal=1400,
        current_score=1050,
        weak_topics=["Reading Inference", "Quadratic Equations"],
        strong_topics=["Vocabulary"],
        recent_performance={
            "reading": {"accuracy": 0.48, "questions_attempted": 20},
            "math": {"accuracy": 0.65, "questions_attempted": 15},
        },
        recommended_focus=["Reading Inference"],
        active_recommendations=[],
    )
    defaults.update(overrides)
    return StudentContext(**defaults)


def _fake_complete(response_dict: dict):
    """Returns a `complete_fn` that ignores the messages and always returns
    `response_dict` as JSON — standing in for a real Groq call."""

    def _complete(messages: list[dict]) -> str:
        return json.dumps(response_dict)

    return _complete


def test_diagnose_returns_valid_result_for_well_formed_response():
    context = _make_context()
    agent = DiagnosticAgent(
        complete_fn=_fake_complete(
            {
                "weak_topics": ["Reading Inference", "Quadratic Equations"],
                "strong_topics": ["Vocabulary"],
                "priority_topics": ["Reading Inference"],
                "reasoning": "Reading accuracy is 48% over 20 questions, well below the "
                "60% mastery threshold, and is the system's top recommended focus area.",
                "confidence": 0.82,
                "recommended_intervention": "Assign inference-strategy practice before the next assessment.",
                "intervention_urgency": "moderate",
            }
        )
    )

    result = agent.diagnose(context)

    assert str(result.student_id) == context.student_id
    assert result.weak_topics == ["Reading Inference", "Quadratic Equations"]
    assert result.priority_topics == ["Reading Inference"]
    assert result.confidence == 0.82
    assert result.intervention_urgency == InterventionUrgency.MODERATE


def test_diagnose_filters_priority_topics_not_in_weak_topics():
    # The model claims "Grammar" is a priority even though it never listed
    # it as weak — the agent must not trust that blindly.
    context = _make_context()
    agent = DiagnosticAgent(
        complete_fn=_fake_complete(
            {
                "weak_topics": ["Reading Inference"],
                "strong_topics": [],
                "priority_topics": ["Reading Inference", "Grammar"],
                "reasoning": "Reading inference accuracy is low.",
                "confidence": 0.6,
            }
        )
    )

    result = agent.diagnose(context)

    assert result.priority_topics == ["Reading Inference"]
    assert "Grammar" not in result.priority_topics


def test_diagnose_handles_sparse_data_with_low_confidence():
    context = _make_context(weak_topics=[], strong_topics=[], recent_performance={})
    agent = DiagnosticAgent(
        complete_fn=_fake_complete(
            {
                "weak_topics": [],
                "strong_topics": [],
                "priority_topics": [],
                "reasoning": "Not enough practice history yet to identify a clear weakness.",
                "confidence": 0.1,
                "recommended_intervention": None,
                "intervention_urgency": "none",
            }
        )
    )

    result = agent.diagnose(context)

    assert result.confidence == 0.1
    assert result.weak_topics == []
    assert result.intervention_urgency == InterventionUrgency.NONE


def test_diagnose_raises_on_invalid_json():
    context = _make_context()
    agent = DiagnosticAgent(complete_fn=lambda messages: "not valid json {{{")

    with pytest.raises(DiagnosticAgentError, match="not valid JSON"):
        agent.diagnose(context)


def test_diagnose_raises_on_schema_mismatch():
    context = _make_context()
    # Missing required "reasoning" field, and confidence out of range.
    agent = DiagnosticAgent(complete_fn=_fake_complete({"confidence": 5.0}))

    with pytest.raises(DiagnosticAgentError, match="did not match the expected schema"):
        agent.diagnose(context)


def test_diagnose_without_complete_fn_requires_groq_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    context = _make_context()
    agent = DiagnosticAgent()  # no complete_fn -> falls back to real Groq path

    with pytest.raises(DiagnosticAgentError, match="GROQ_API_KEY is not set"):
        agent.diagnose(context)
