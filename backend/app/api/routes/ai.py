"""AI routes — Api_design.txt §8. See README + app/services/ai_bridge.py
for why these call ai-data directly rather than a real agent
orchestrator.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.ai import CoachRequest, CoachResponse, DiagnoseResponse, StudyPlanResponse
from app.services import ai_bridge, student_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DiagnoseResponse:
    profile = student_service.get_profile(db, user.id)
    return ai_bridge.diagnose(db, profile.id)


@router.post("/study-plan", response_model=StudyPlanResponse)
def study_plan(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudyPlanResponse:
    profile = student_service.get_profile(db, user.id)
    return ai_bridge.generate_study_plan(db, profile.id)


@router.post("/coach", response_model=CoachResponse)
def coach(
    payload: CoachRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CoachResponse:
    profile = student_service.get_profile(db, user.id)
    return ai_bridge.coach(db, profile.id, payload.question)
