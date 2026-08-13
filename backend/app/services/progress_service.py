"""Progress service — Api_design.txt §10 (Dashboard / Weekly Report).

Reads from `ProgressRecord` (written by `session_service.complete_session`)
for the numbers a dashboard needs cheaply, and calls into the `ai_bridge`
for the qualitative "weak_area"/"recommendation" text — avoids
recomputing full topic-mastery analysis just to render a dashboard number.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.learning_session import LearningSession
from app.models.progress import ProgressRecord
from app.models.student import StudentProfile
from app.schemas.progress import DashboardResponse, WeeklyReportResponse
from app.services import ai_bridge
from app.utils.errors import APIError

_REPORT_WINDOW_DAYS = 7


def _current_streak(db: Session, student_id: UUID) -> int:
    """Consecutive calendar days (counting back from today) with at least
    one completed learning session — matches Api_design.txt §10's
    `"streak": 7` (a day-streak, not a session count).
    """
    completed_dates = {
        row.completed_at.date()
        for row in db.query(LearningSession)
        .filter(LearningSession.student_id == student_id, LearningSession.completed_at.isnot(None))
        .all()
    }
    if not completed_dates:
        return 0

    streak = 0
    day = datetime.utcnow().date()
    while day in completed_dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def get_dashboard(db: Session, student_id: UUID) -> DashboardResponse:
    profile = db.query(StudentProfile).filter_by(id=student_id).first()

    records = (
        db.query(ProgressRecord)
        .filter_by(student_id=student_id)
        .order_by(ProgressRecord.recorded_at)
        .all()
    )
    if records:
        change = records[-1].score - records[0].score
        improvement = f"{'+' if change >= 0 else ''}{round(change)}"
    else:
        improvement = "+0"

    try:
        diagnosis = ai_bridge.diagnose(db, student_id)
        weak_area = diagnosis.weaknesses[0] if diagnosis.weaknesses else None
    except APIError:
        # Not enough answer history yet for a diagnosis — a dashboard
        # should degrade gracefully to "no weak area yet", not 4xx.
        weak_area = None

    return DashboardResponse(
        current_score=profile.current_score if profile else None,
        improvement=improvement,
        weak_area=weak_area,
        streak=_current_streak(db, student_id),
    )


def get_weekly_report(db: Session, student_id: UUID) -> WeeklyReportResponse:
    since = datetime.utcnow() - timedelta(days=_REPORT_WINDOW_DAYS)

    sessions = (
        db.query(LearningSession)
        .filter(
            LearningSession.student_id == student_id,
            LearningSession.completed_at.isnot(None),
            LearningSession.completed_at >= since,
        )
        .all()
    )
    study_hours = round(sum(s.duration or 0 for s in sessions) / 60, 2)
    questions_completed = sum(s.questions_completed or 0 for s in sessions)

    try:
        diagnosis = ai_bridge.diagnose(db, student_id)
        recommendation = diagnosis.recommendation
    except APIError:
        recommendation = "Keep practicing consistently — not enough data yet for a specific recommendation."

    return WeeklyReportResponse(
        study_hours=study_hours,
        questions_completed=questions_completed,
        recommendation=recommendation,
    )
