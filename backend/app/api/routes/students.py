"""Student profile routes — Api_design.txt §6.

`POST /students/profile` (create) isn't in Api_design.txt explicitly —
only GET/PUT are — but PUT alone can't work for a student who has no
profile row yet (registration only creates a `User`, per §5). Added a
create endpoint so the onboarding flow in Development_roadmap.txt Phase 2
("Student Profile: Goal setup, SAT target, Study preferences") actually
has somewhere to write to; PUT stays update-only as documented.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.student import StudentProfileResponse, StudentProfileUpdateRequest
from app.services import student_service

router = APIRouter(prefix="/students", tags=["students"])


def _to_response(profile) -> StudentProfileResponse:
    return StudentProfileResponse(
        target_score=profile.target_score,
        current_score=profile.current_score,
        exam_date=profile.exam_date,
        study_time=profile.study_time_daily,
        confidence_level=profile.confidence_level,
        learning_style=profile.learning_style,
    )


@router.post("/profile", response_model=StudentProfileResponse)
def create_profile(
    payload: StudentProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudentProfileResponse:
    profile = student_service.create_profile(
        db,
        user_id=user.id,
        target_score=payload.target_score or 1200,
        study_time_daily=payload.study_time or 30,
        current_score=payload.current_score,
        exam_date=payload.exam_date,
        confidence_level=payload.confidence_level,
        learning_style=payload.learning_style,
    )
    return _to_response(profile)


@router.get("/profile", response_model=StudentProfileResponse)
def get_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudentProfileResponse:
    profile = student_service.get_profile(db, user.id)
    return _to_response(profile)


@router.put("/profile", response_model=StudentProfileResponse)
def update_profile(
    payload: StudentProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudentProfileResponse:
    profile = student_service.update_profile(
        db,
        user.id,
        target_score=payload.target_score,
        current_score=payload.current_score,
        exam_date=payload.exam_date,
        study_time_daily=payload.study_time,
        confidence_level=payload.confidence_level,
        learning_style=payload.learning_style,
    )
    return _to_response(profile)
