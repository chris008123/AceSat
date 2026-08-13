"""Learning session service — Backend_architecture.txt §12's post-lesson
flow (Learning Service -> Database Update -> Analytics Agent -> Planning
Agent -> New Recommendation), simplified: on completion this also writes
a coarse `ProgressRecord` snapshot so the dashboard has something to show
without recomputing from `answers` on every request.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.learning_session import LearningSession
from app.models.progress import ProgressRecord
from app.services.ai_bridge import suggest_mission_topic
from app.utils.errors import SessionError, ValidationAPIError


def start_session(db: Session, student_id: UUID) -> LearningSession:
    topic = suggest_mission_topic(db, student_id)
    mission = f"{topic} practice" if topic else "General practice"

    session = LearningSession(student_id=student_id, mission=mission)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def complete_session(
    db: Session,
    session_id: UUID | str,
    student_id: UUID,
    accuracy: float,
    duration: int,
) -> LearningSession:
    session_id = session_id if isinstance(session_id, UUID) else UUID(str(session_id))
    session = db.query(LearningSession).filter_by(id=session_id, student_id=student_id).first()
    if session is None:
        raise SessionError("Learning session not found")
    if not (0 <= accuracy <= 100):
        raise ValidationAPIError("accuracy must be between 0 and 100")

    session.accuracy = accuracy
    session.duration = duration
    session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)

    # Coarse "overall" progress snapshot — Database_design.txt's
    # progress_records is per-subject, but a session here isn't tagged
    # with a subject (Api_design.txt §9's request body only has
    # accuracy/duration), so this records an overall-subject snapshot
    # rather than inventing a subject the API doesn't provide.
    db.add(
        ProgressRecord(
            student_id=student_id,
            subject="overall",
            score=accuracy,
            mastery_level=accuracy / 100,
        )
    )
    db.commit()

    return session
