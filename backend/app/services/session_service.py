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
from app.models.question import Question
from app.services.ai_bridge import suggest_mission_topic
from app.utils.errors import SessionError, ValidationAPIError

# Small, fixed practice set per mission — mirrors assessment_service's
# DIAGNOSTIC_QUESTION_COUNT approach: a hackathon MVP doesn't need
# adaptive session length yet, just a short focused set.
SESSION_QUESTION_COUNT = 3


def _pick_session_questions(db: Session, topic: str | None) -> list[Question]:
    """Prefers questions from the student's weak topic (what `mission`
    is named after); falls back to a general spread if that topic has no
    questions yet, so a session never comes back empty.
    """
    questions: list[Question] = []
    if topic:
        questions = db.query(Question).filter_by(topic=topic).limit(SESSION_QUESTION_COUNT).all()
    if len(questions) < SESSION_QUESTION_COUNT:
        seen_ids = {q.id for q in questions}
        extra = (
            db.query(Question)
            .filter(~Question.id.in_(seen_ids) if seen_ids else True)
            .limit(SESSION_QUESTION_COUNT - len(questions))
            .all()
        )
        questions.extend(extra)
    return questions


def start_session(db: Session, student_id: UUID) -> tuple[LearningSession, list[Question]]:
    topic = suggest_mission_topic(db, student_id)
    mission = f"{topic} practice" if topic else "General practice"

    session = LearningSession(student_id=student_id, mission=mission)
    db.add(session)
    db.commit()
    db.refresh(session)

    questions = _pick_session_questions(db, topic)
    return session, questions


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
