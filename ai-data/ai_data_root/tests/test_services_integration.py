from __future__ import annotations

from ai_data.models.enums import RecommendationAction
from ai_data.services.context_builder import build_student_context
from ai_data.services.mastery_engine import build_topic_mastery
from ai_data.services.recommendation_context import generate_topic_recommendations
from ai_data.services.student_profile import generate_student_profile


def test_build_topic_mastery_returns_pydantic_models(student_id, strong_algebra_responses):
    mastery = build_topic_mastery(student_id, strong_algebra_responses)
    assert len(mastery) == 1
    assert mastery[0].topic == "Linear Equations"
    assert mastery[0].student_id == student_id


def test_generate_student_profile_flags_weak_and_strong(
    demo_student, declining_reading_inference_responses, strong_algebra_responses
):
    all_responses = declining_reading_inference_responses + strong_algebra_responses
    profile = generate_student_profile(demo_student, all_responses, study_consistency=0.8)

    assert "Reading Inference" in profile.weak_topics
    assert "Linear Equations" in profile.strong_topics
    assert profile.target_score == 1450
    assert profile.recommended_focus_areas  # not empty
    assert profile.study_consistency == 0.8


def test_generate_student_profile_no_data(demo_student):
    profile = generate_student_profile(demo_student, [])
    assert profile.weak_topics == []
    assert profile.strong_topics == []
    assert profile.topic_mastery == []


def test_recommendation_has_evidence_based_reason(declining_reading_inference_responses):
    recommendations = generate_topic_recommendations(declining_reading_inference_responses)
    assert len(recommendations) >= 1
    top = recommendations[0]
    assert top.topic == "Reading Inference"
    assert "%" in top.reason  # reason cites concrete numbers, not a generic message
    assert top.action in (RecommendationAction.PRACTICE_TOPIC, RecommendationAction.REVIEW_CONCEPT)


def test_context_builder_produces_minimal_relevant_payload(
    demo_student, declining_reading_inference_responses
):
    profile = generate_student_profile(demo_student, declining_reading_inference_responses)
    recommendations = generate_topic_recommendations(declining_reading_inference_responses)
    context = build_student_context(profile, recommendations)

    assert context.goal == 1450
    assert context.current_score == 1080
    assert "Reading Inference" in context.weak_topics
    assert context.active_recommendations == recommendations
