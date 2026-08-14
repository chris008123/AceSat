"""Phase 3 tests: Planning Agent behavior against a fake `complete_fn`
returning canned JSON — no real GROQ_API_KEY or network access needed.
"""

from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

import pytest

from ai_data.services.context_builder import StudentContext

from ai_agents.agents.planning_agent import PlanningAgent, PlanningAgentError
from ai_agents.schemas.diagnostic import DiagnosticResult


def _make_context(**overrides) -> StudentContext:
    defaults = dict(
        student_id=str(uuid4()),
        goal=1400,
        current_score=1050,
        weak_topics=["Reading Inference", "Quadratic Equations"],
        strong_topics=["Vocabulary"],
        recent_performance={"reading": {"accuracy": 0.48, "questions_attempted": 20}},
        recommended_focus=["Reading Inference"],
        active_recommendations=[],
    )
    defaults.update(overrides)
    return StudentContext(**defaults)


def _make_diagnosis(**overrides) -> DiagnosticResult:
    defaults = dict(
        student_id=uuid4(),
        weak_topics=["Reading Inference", "Quadratic Equations"],
        strong_topics=["Vocabulary"],
        priority_topics=["Reading Inference"],
        reasoning="Reading accuracy is 48% over 20 questions, below the 60% mastery threshold.",
        confidence=0.82,
    )
    defaults.update(overrides)
    return DiagnosticResult(**defaults)


def _fake_complete(response_dict: dict):
    def _complete(messages: list[dict]) -> str:
        return json.dumps(response_dict)

    return _complete


def test_plan_returns_valid_result_for_well_formed_response():
    context = _make_context()
    diagnosis = _make_diagnosis()
    agent = PlanningAgent(
        complete_fn=_fake_complete(
            {
                "goal": "Improve SAT Reading from 1050 to 1400",
                "priority_topics": ["Reading Inference"],
                "weekly_plan": [
                    {
                        "day": "Monday",
                        "topic": "Reading Inference",
                        "duration_minutes": 20,
                        "activity": "Practice",
                        "reason": "Accuracy is 48%, below the 60% mastery threshold.",
                    },
                    {
                        "day": "Tuesday",
                        "topic": "Reading Inference",
                        "duration_minutes": 15,
                        "activity": "Review lesson",
                        "reason": "Reinforce inference strategy after Monday's practice.",
                    },
                ],
            }
        )
    )

    plan = agent.plan(context, diagnosis, available_study_time_minutes=30, exam_date=date(2026, 10, 4))

    assert str(plan.student_id) == context.student_id
    assert plan.priority_topics == ["Reading Inference"]
    assert len(plan.weekly_plan) == 2
    assert plan.total_weekly_minutes == 35  # recomputed, not trusted from the model
    assert plan.exam_date == date(2026, 10, 4)


def test_plan_filters_priority_topics_not_in_diagnosis():
    # The model claims "Grammar" is a priority even though the diagnosis
    # never flagged it as weak or priority — must not be trusted blindly.
    context = _make_context()
    diagnosis = _make_diagnosis()
    agent = PlanningAgent(
        complete_fn=_fake_complete(
            {
                "goal": "Improve SAT Reading",
                "priority_topics": ["Reading Inference", "Grammar"],
                "weekly_plan": [
                    {
                        "day": "Monday",
                        "topic": "Reading Inference",
                        "duration_minutes": 20,
                        "activity": "Practice",
                        "reason": "Accuracy is 48%, below the 60% mastery threshold.",
                    }
                ],
            }
        )
    )

    plan = agent.plan(context, diagnosis, available_study_time_minutes=30)

    assert plan.priority_topics == ["Reading Inference"]
    assert "Grammar" not in plan.priority_topics


def test_plan_total_weekly_minutes_always_recomputed_not_trusted():
    context = _make_context()
    diagnosis = _make_diagnosis()
    agent = PlanningAgent(
        complete_fn=_fake_complete(
            {
                "goal": "Improve SAT Reading",
                "priority_topics": [],
                "weekly_plan": [
                    {
                        "day": "Monday",
                        "topic": "Reading Inference",
                        "duration_minutes": 20,
                        "activity": "Practice",
                        "reason": "Accuracy is 48%, below the 60% mastery threshold.",
                    }
                ],
                # Model lying about the total — should be ignored entirely,
                # this key isn't even part of _PlanningLLMOutput.
                "total_weekly_minutes": 9999,
            }
        )
    )

    plan = agent.plan(context, diagnosis, available_study_time_minutes=30)

    assert plan.total_weekly_minutes == 20


def test_plan_can_be_empty_when_diagnosis_has_no_weak_topics():
    context = _make_context(weak_topics=[], strong_topics=["Reading Inference"])
    diagnosis = _make_diagnosis(
        weak_topics=[], strong_topics=["Reading Inference"], priority_topics=[],
        reasoning="No weak topics identified — student is performing well across the board.",
        confidence=0.7,
    )
    agent = PlanningAgent(
        complete_fn=_fake_complete(
            {"goal": "Maintain performance", "priority_topics": [], "weekly_plan": []}
        )
    )

    plan = agent.plan(context, diagnosis, available_study_time_minutes=30)

    assert plan.weekly_plan == []
    assert plan.total_weekly_minutes == 0


def test_plan_raises_on_invalid_json():
    context = _make_context()
    diagnosis = _make_diagnosis()
    agent = PlanningAgent(complete_fn=lambda messages: "not valid json {{{")

    with pytest.raises(PlanningAgentError, match="not valid JSON"):
        agent.plan(context, diagnosis, available_study_time_minutes=30)


def test_plan_raises_on_schema_mismatch():
    context = _make_context()
    diagnosis = _make_diagnosis()
    # Missing required "goal" field.
    agent = PlanningAgent(complete_fn=_fake_complete({"priority_topics": [], "weekly_plan": []}))

    with pytest.raises(PlanningAgentError, match="did not match the expected schema"):
        agent.plan(context, diagnosis, available_study_time_minutes=30)


def test_plan_raises_on_invalid_study_plan_item_in_response():
    # weekly_plan item missing the required "reason" field — StudyPlanItem
    # validation should surface as a PlanningAgentError, same path as any
    # other schema mismatch.
    context = _make_context()
    diagnosis = _make_diagnosis()
    agent = PlanningAgent(
        complete_fn=_fake_complete(
            {
                "goal": "Improve SAT Reading",
                "priority_topics": [],
                "weekly_plan": [
                    {"day": "Monday", "topic": "Reading Inference", "duration_minutes": 20, "activity": "Practice"}
                ],
            }
        )
    )

    with pytest.raises(PlanningAgentError, match="did not match the expected schema"):
        agent.plan(context, diagnosis, available_study_time_minutes=30)


def test_plan_without_complete_fn_requires_groq_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    context = _make_context()
    diagnosis = _make_diagnosis()
    agent = PlanningAgent()  # no complete_fn -> falls back to real Groq path

    with pytest.raises(PlanningAgentError, match="GROQ_API_KEY is not set"):
        agent.plan(context, diagnosis, available_study_time_minutes=30)
