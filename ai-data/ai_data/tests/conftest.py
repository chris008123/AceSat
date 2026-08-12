from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from ai_data.models.assessment import QuestionResponse
from ai_data.models.enums import ConfidenceLevel, DifficultyLevel, Subject
from ai_data.models.student import Student


@pytest.fixture
def student_id():
    return uuid4()


@pytest.fixture
def demo_student(student_id) -> Student:
    """Mirrors the demo account in Deployment_architecture.txt §12."""
    return Student(
        student_id=student_id,
        target_score=1450,
        current_score=1080,
        exam_date=None,
        study_time_daily_minutes=45,
        confidence_level=3,
        learning_style="step-by-step",
    )


def _make_response(
    student_id,
    topic: str,
    subject: Subject,
    correct: bool,
    days_ago: int,
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
) -> QuestionResponse:
    return QuestionResponse(
        response_id=uuid4(),
        student_id=student_id,
        question_id=uuid4(),
        topic=topic,
        subject=subject,
        difficulty=difficulty,
        answer_given="A",
        correct=correct,
        confidence=ConfidenceLevel.MEDIUM,
        response_time_seconds=45,
        answered_at=datetime.utcnow() - timedelta(days=days_ago),
    )


@pytest.fixture
def declining_reading_inference_responses(student_id):
    """5 correct out of 7 early on, then a recent slump — the scenario
    from AI_Agent_architecture.txt §9 ('Student repeatedly fails geometry
    questions', adapted here to reading inference to match the hackathon
    prompt's own worked example in section 8).
    """
    responses = []
    # Older window: still below-mastery overall, but noticeably better than
    # the recent slump — keeps indices 5-9 as the "previous window" the
    # trend calculation compares against.
    older_pattern = [True, True, False, False, True, False, True, True, False, True]
    for i, correct in enumerate(older_pattern):
        responses.append(
            _make_response(student_id, "Reading Inference", Subject.READING, correct, days_ago=20 - i)
        )
    # Recent window: mostly wrong (accuracy drops toward 47%)
    recent_pattern = [False, True, False, False, True]
    for i, correct in enumerate(recent_pattern):
        responses.append(
            _make_response(student_id, "Reading Inference", Subject.READING, correct, days_ago=4 - i)
        )
    return responses


@pytest.fixture
def strong_algebra_responses(student_id):
    pattern = [True, True, True, True, False, True, True, True]
    return [
        _make_response(student_id, "Linear Equations", Subject.MATH, correct, days_ago=8 - i)
        for i, correct in enumerate(pattern)
    ]


@pytest.fixture
def sparse_geometry_responses(student_id):
    """Only 2 attempts — below MIN attempts threshold, should not be
    confidently labeled weak or strong."""
    return [
        _make_response(student_id, "Geometry", Subject.MATH, False, days_ago=2),
        _make_response(student_id, "Geometry", Subject.MATH, True, days_ago=1),
    ]
