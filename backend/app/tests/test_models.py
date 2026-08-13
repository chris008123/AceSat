from __future__ import annotations

from datetime import date
from uuid import uuid4

from app.models.question import Question
from app.models.student import StudentProfile
from app.models.user import User, UserRole


def test_create_user(db_session):
    user = User(email="sarah@email.com", password_hash="hashed", role=UserRole.STUDENT)
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter_by(email="sarah@email.com").first()
    assert fetched is not None
    assert fetched.role == UserRole.STUDENT


def test_student_profile_links_to_user(db_session):
    user = User(email="sarah@email.com", password_hash="hashed")
    db_session.add(user)
    db_session.commit()

    profile = StudentProfile(
        user_id=user.id,
        target_score=1450,
        current_score=1080,
        exam_date=date(2026, 11, 1),
        study_time_daily=45,
        confidence_level=3,
        learning_style="step-by-step",
    )
    db_session.add(profile)
    db_session.commit()

    fetched_user = db_session.query(User).filter_by(id=user.id).first()
    assert fetched_user.student_profile is not None
    assert fetched_user.student_profile.target_score == 1450


def test_create_question(db_session):
    question = Question(
        subject="math",
        topic="Linear Equations",
        difficulty=2,
        question_text="Solve for x: 2x + 4 = 10",
        answer_options={"A": "2", "B": "3", "C": "4", "D": "5"},
        correct_answer="B",
    )
    db_session.add(question)
    db_session.commit()

    fetched = db_session.query(Question).filter_by(id=question.id).first()
    assert fetched.topic == "Linear Equations"
    assert fetched.answer_options["B"] == "3"
