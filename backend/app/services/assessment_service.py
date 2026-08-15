"""Assessment service — Backend_architecture.txt §10 "Assessment Service:
Questions, Answers, Scoring."
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from sqlalchemy import func

from sqlalchemy.orm import Session

from app.models.assessment import Answer, Assessment
from app.models.question import Question
from app.models.student import StudentProfile
from app.utils.errors import NotFoundError, SessionError, ValidationAPIError

# Small, fixed-size diagnostic per Project_modules.txt §5 ("Diagnostic
# test... SAT-style questions") — a hackathon MVP doesn't need adaptive
# question selection yet, just a representative spread across subjects.
DIAGNOSTIC_QUESTION_COUNT = 10


def _as_uuid(value: str | UUID) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value))


def start_assessment(
    db: Session,
    student_id: UUID,
    assessment_type: str = "diagnostic",
) -> tuple[Assessment, list[Question]]:
    """Create a diagnostic assessment using a randomized,
    subject-balanced selection from the full question bank.
    """

    subjects = [
        row[0]
        for row in db.query(Question.subject).distinct().all()
    ]

    if not subjects:
        raise ValidationAPIError(
            "No questions available — seed the question bank before starting an assessment"
        )

    # Divide the diagnostic as evenly as possible across subjects.
    subject_count = len(subjects)
    base_count = DIAGNOSTIC_QUESTION_COUNT // subject_count
    remainder = DIAGNOSTIC_QUESTION_COUNT % subject_count

    questions: list[Question] = []

    for index, subject in enumerate(subjects):
        count = base_count + (1 if index < remainder else 0)

        if count <= 0:
            continue

        subject_questions = (
            db.query(Question)
            .filter(Question.subject == subject)
            .order_by(func.random())
            .limit(count)
            .all()
        )

        questions.extend(subject_questions)

    # Safety fallback/top-up if some subjects don't have enough questions.
    if len(questions) < DIAGNOSTIC_QUESTION_COUNT:
        seen_ids = {q.id for q in questions}

        query = db.query(Question)

        if seen_ids:
            query = query.filter(~Question.id.in_(seen_ids))

        extra = (
            query
            .order_by(func.random())
            .limit(
                DIAGNOSTIC_QUESTION_COUNT - len(questions)
            )
            .all()
        )

        questions.extend(extra)

    # Final shuffle so subjects aren't always grouped together.
    import random
    random.shuffle(questions)

    assessment = Assessment(
        student_id=student_id,
        assessment_type=assessment_type,
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return assessment, questions


def submit_answer(
    db: Session,
    assessment_id: UUID | str,
    student_id: UUID,
    question_id: UUID | str,
    answer_given: str,
    confidence: int,
    time_taken: int,
) -> tuple[Answer, str]:
    assessment_id = _as_uuid(assessment_id)
    question_id = _as_uuid(question_id)

    assessment = db.query(Assessment).filter_by(id=assessment_id, student_id=student_id).first()
    if assessment is None:
        raise SessionError("Assessment not found")

    question = db.query(Question).filter_by(id=question_id).first()
    if question is None:
        raise NotFoundError("Question not found")

    correct = answer_given.strip().upper() == question.correct_answer.strip().upper()

    answer = Answer(
        assessment_id=assessment_id,
        student_id=student_id,
        question_id=question_id,
        answer_given=answer_given,
        correct=correct,
        confidence=confidence,
        response_time=time_taken,
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer, question.correct_answer


def complete_assessment(db: Session, assessment_id: UUID | str, student_id: UUID) -> Assessment:
    assessment_id = _as_uuid(assessment_id)
    assessment = db.query(Assessment).filter_by(id=assessment_id, student_id=student_id).first()
    if assessment is None:
        raise SessionError("Assessment not found")

    answers = db.query(Answer).filter_by(assessment_id=assessment_id).all()
    if not answers:
        raise ValidationAPIError("Cannot complete an assessment with no submitted answers")

    correct_count = sum(1 for a in answers if a.correct)
    score = round((correct_count / len(answers)) * 100)

    assessment.score = score
    assessment.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(assessment)

    # Keep the student's current_score estimate roughly in sync — a real
    # SAT scaled-score conversion is out of scope for the MVP, this is a
    # simple proportional placeholder the Planning/Analytics side can
    # refine later.
    profile = db.query(StudentProfile).filter_by(id=student_id).first()
    if profile is not None:
        profile.current_score = min(1600, round(400 + (score / 100) * 1200))
        db.commit()

    return assessment
