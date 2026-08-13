"""Learning session routes — Api_design.txt §9."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.session import CompleteSessionRequest, CompleteSessionResponse, StartSessionResponse
from app.services import session_service, student_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=StartSessionResponse)
def start(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StartSessionResponse:
    profile = student_service.get_profile(db, user.id)
    session = session_service.start_session(db, profile.id)
    return StartSessionResponse(session_id=str(session.id), mission=session.mission)


@router.post("/complete", response_model=CompleteSessionResponse)
def complete(
    payload: CompleteSessionRequest,
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompleteSessionResponse:
    profile = student_service.get_profile(db, user.id)
    session = session_service.complete_session(
        db, session_id, profile.id, payload.accuracy, payload.duration
    )
    return CompleteSessionResponse(accuracy=session.accuracy, duration=session.duration)
