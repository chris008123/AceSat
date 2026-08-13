"""Progress routes — Api_design.txt §10."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.progress import DashboardResponse, WeeklyReportResponse
from app.services import progress_service, student_service

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardResponse:
    profile = student_service.get_profile(db, user.id)
    return progress_service.get_dashboard(db, profile.id)


@router.get("/report", response_model=WeeklyReportResponse)
def report(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> WeeklyReportResponse:
    profile = student_service.get_profile(db, user.id)
    return progress_service.get_weekly_report(db, profile.id)
