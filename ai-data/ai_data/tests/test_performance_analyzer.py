from __future__ import annotations

from ai_data.models.enums import MasteryTrend
from ai_data.services.performance_analyzer import (
    calculate_accuracy,
    calculate_performance_trend,
    calculate_topic_mastery,
    estimate_learning_progress,
    identify_strong_topics,
    identify_weak_topics,
)


def test_calculate_accuracy_empty_list_returns_zero():
    assert calculate_accuracy([]) == 0.0


def test_calculate_accuracy_basic(strong_algebra_responses):
    accuracy = calculate_accuracy(strong_algebra_responses)
    assert accuracy == 7 / 8


def test_declining_topic_detected_as_declining(declining_reading_inference_responses):
    trend = calculate_performance_trend(declining_reading_inference_responses)
    assert trend in (MasteryTrend.DECLINING, MasteryTrend.WEAK)


def test_weak_topic_identified(declining_reading_inference_responses):
    weak = identify_weak_topics(declining_reading_inference_responses)
    assert "Reading Inference" in weak


def test_strong_topic_identified(strong_algebra_responses):
    strong = identify_strong_topics(strong_algebra_responses)
    assert "Linear Equations" in strong


def test_sparse_topic_excluded_from_weak_and_strong(sparse_geometry_responses):
    weak = identify_weak_topics(sparse_geometry_responses)
    strong = identify_strong_topics(sparse_geometry_responses)
    assert "Geometry" not in weak
    assert "Geometry" not in strong


def test_topic_mastery_shape(strong_algebra_responses):
    mastery = calculate_topic_mastery(strong_algebra_responses)
    assert "Linear Equations" in mastery
    stats = mastery["Linear Equations"]
    assert stats["attempts"] == 8
    assert stats["correct_answers"] == 7
    assert 0.0 <= stats["mastery_score"] <= 1.0
    assert 0.0 <= stats["confidence"] <= 1.0


def test_estimate_learning_progress_no_data():
    progress = estimate_learning_progress([])
    assert progress["total_questions"] == 0
    assert progress["overall_accuracy"] == 0.0


def test_estimate_learning_progress_with_data(declining_reading_inference_responses):
    progress = estimate_learning_progress(declining_reading_inference_responses)
    assert progress["total_questions"] == 15
    assert progress["accuracy_change"] < 0  # slump should show as negative change
