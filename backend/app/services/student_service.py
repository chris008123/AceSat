"""Student profile service — Backend_architecture.txt §10 "Student
Service: Profiles, Preferences, Goals."
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.student import StudentProfile
from app.utils.errors import NotFoundError


def get_profile(db: Session, user_id: UUID) -> StudentProfile:
    profile = db.query(StudentProfile).filter_by(user_id=user_id).first()
    if profile is None:
        raise NotFoundError("Student profile not found — create one first")
    return profile


def create_profile(
    db: Session,
    user_id: UUID,
    target_score: int,
    study_time_daily: int,
    current_score: int | None = None,
    exam_date=None,
    confidence_level: int | None = None,
    learning_style: str | None = None,
) -> StudentProfile:
    profile = StudentProfile(
        user_id=user_id,
        target_score=target_score,
        current_score=current_score,
        exam_date=exam_date,
        study_time_daily=study_time_daily,
        confidence_level=confidence_level,
        learning_style=learning_style,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, user_id: UUID, **fields) -> StudentProfile:
    profile = get_profile(db, user_id)
    for key, value in fields.items():
        if value is not None and hasattr(profile, key):
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile
