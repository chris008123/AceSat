"""Phase 1 tests: the four agent contracts validate correctly, both for
realistic valid data and for the constraints that matter (confidence
bounds, required fields). No agent logic exists yet — this only proves
the schemas themselves are sound.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from ai_agents.schemas import (
    AnalyticsResult,
    AnalyticsStatus,
    CoachingResponse,
    CoachingResponseType,
    DiagnosticResult,
    InterventionUrgency,
    StudyPlan,
    StudyPlanItem,
    TopicTrend,
)


# ---------------------------------------------------------------------------
# DiagnosticResult
# ---------------------------------------------------------------------------


def test_diagnostic_result_valid():
    result = DiagnosticResult(
        student_id=uuid4(),
        weak_topics=["Reading Inference", "Quadratic Equations"],
        strong_topics=["Vocabulary"],
        priority_topics=["Quadratic Equations"],
        reasoning="Accuracy on quadratic equations dropped from 72% to 48% over the last 3 attempts.",
        confidence=0.85,
        recommended_intervention="Assign a foundational lesson on factoring before more practice.",
        intervention_urgency=InterventionUrgency.MODERATE,
    )
    assert result.confidence == 0.85
    assert "Quadratic Equations" in result.priority_topics
    assert result.intervention_urgency == InterventionUrgency.MODERATE


def test_diagnostic_result_defaults():
    # weak/strong/priority topics and intervention fields are all optional —
    # a diagnosis with no clear weaknesses yet is still a valid diagnosis.
    result = DiagnosticResult(
        student_id=uuid4(),
        reasoning="Not enough data yet to identify a clear weak area.",
        confidence=0.2,
    )
    assert result.weak_topics == []
    assert result.intervention_urgency == InterventionUrgency.NONE
    assert result.recommended_intervention is None


@pytest.mark.parametrize("bad_confidence", [-0.1, 1.1, 2.0])
def test_diagnostic_result_confidence_out_of_range(bad_confidence):
    with pytest.raises(ValidationError):
        DiagnosticResult(student_id=uuid4(), reasoning="x", confidence=bad_confidence)


def test_diagnostic_result_requires_reasoning():
    with pytest.raises(ValidationError):
        DiagnosticResult(student_id=uuid4(), confidence=0.5)  # missing reasoning


# ---------------------------------------------------------------------------
# StudyPlan
# ---------------------------------------------------------------------------


def test_study_plan_valid():
    plan = StudyPlan(
        student_id=uuid4(),
        goal="Improve SAT Math from 1050 to 1400",
        priority_topics=["Quadratic Equations", "Linear Equations"],
        weekly_plan=[
            StudyPlanItem(
                day="Monday",
                topic="Linear Equations",
                duration_minutes=30,
                activity="Practice",
                reason="Accuracy is 55%, below the 60% mastery threshold.",
            ),
            StudyPlanItem(
                day="Tuesday",
                topic="Quadratic Equations",
                duration_minutes=20,
                activity="Review lesson",
                reason="Accuracy dropped from 72% to 48% over the last 3 attempts.",
            ),
        ],
        total_weekly_minutes=50,
    )
    assert len(plan.weekly_plan) == 2
    assert plan.weekly_plan[0].reason  # every item must carry a reason


def test_study_plan_item_requires_reason():
    with pytest.raises(ValidationError):
        StudyPlanItem(day="Monday", topic="Algebra", duration_minutes=30, activity="Practice")


def test_study_plan_item_duration_must_be_positive_and_bounded():
    with pytest.raises(ValidationError):
        StudyPlanItem(day="Monday", topic="Algebra", duration_minutes=0, activity="Practice", reason="x")
    with pytest.raises(ValidationError):
        StudyPlanItem(day="Monday", topic="Algebra", duration_minutes=999, activity="Practice", reason="x")


def test_study_plan_can_be_empty_when_no_data_yet():
    plan = StudyPlan(student_id=uuid4(), goal="Improve SAT Math")
    assert plan.weekly_plan == []
    assert plan.priority_topics == []


# ---------------------------------------------------------------------------
# CoachingResponse
# ---------------------------------------------------------------------------


def test_coaching_response_hint_does_not_give_direct_answer():
    response = CoachingResponse(
        student_id=uuid4(),
        concept="Reading Inference",
        response_type=CoachingResponseType.HINT,
        message="Look at the second paragraph — what claim is the author making there?",
        follow_up_question="What evidence supports that claim?",
    )
    assert response.gives_direct_answer is False
    assert response.response_type == CoachingResponseType.HINT


def test_coaching_response_explanation_can_give_direct_answer():
    response = CoachingResponse(
        student_id=uuid4(),
        concept="Quadratic Equations",
        response_type=CoachingResponseType.EXPLANATION,
        message="The answer is C, because factoring (x-2)(x+3) gives roots at 2 and -3.",
        gives_direct_answer=True,
    )
    assert response.gives_direct_answer is True


def test_coaching_response_requires_message_and_concept():
    with pytest.raises(ValidationError):
        CoachingResponse(student_id=uuid4(), response_type=CoachingResponseType.HINT)


# ---------------------------------------------------------------------------
# AnalyticsResult
# ---------------------------------------------------------------------------


def test_analytics_result_valid():
    result = AnalyticsResult(
        student_id=uuid4(),
        overall_status=AnalyticsStatus.IMPROVING,
        topic_trends=[
            TopicTrend(
                topic="Reading Inference",
                status=AnalyticsStatus.IMPROVING,
                detail="Accuracy improved from 55% to 72% over 2 weeks.",
            ),
            TopicTrend(
                topic="Grammar",
                status=AnalyticsStatus.STABLE,
                detail="Accuracy holding steady around 80%.",
            ),
        ],
        summary="Overall accuracy rose from 68% to 76% (+8%) this week.",
        reasoning="Reading inference accuracy shows a consistent upward trend across "
        "the last 3 sessions with no regressions.",
        confidence=0.9,
        recommended_next_action="Increase reading practice difficulty.",
    )
    assert result.overall_status == AnalyticsStatus.IMPROVING
    assert len(result.topic_trends) == 2


def test_analytics_result_confidence_bounds():
    with pytest.raises(ValidationError):
        AnalyticsResult(
            student_id=uuid4(),
            overall_status=AnalyticsStatus.STABLE,
            summary="x",
            reasoning="x",
            confidence=1.5,
        )


def test_analytics_result_defaults_no_topic_trends():
    result = AnalyticsResult(
        student_id=uuid4(),
        overall_status=AnalyticsStatus.NEEDS_INTERVENTION,
        summary="Accuracy dropped sharply this week.",
        reasoning="Overall accuracy fell from 70% to 40% across the last 10 questions.",
        confidence=0.75,
    )
    assert result.topic_trends == []
    assert result.recommended_next_action is None
