"""Assessment service — Backend_architecture.txt §10 "Assessment Service:
Questions, Answers, Scoring."
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

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


def start_assessment(db: Session, student_id: UUID, assessment_type: str = "diagnostic") -> tuple[Assessment, list[Question]]:
    """Picks a subject-balanced spread of questions rather than the first
    N rows — with an uneven question bank (e.g. many more reading
    questions seeded than math), a naive `.limit(N)` can silently starve
    entire subjects out of every diagnostic, which defeats the point of a
    diagnostic test. Distributes `DIAGNOSTIC_QUESTION_COUNT` as evenly as
    possible across whatever subjects currently have questions.
    """
    subjects = [row[0] for row in db.query(Question.subject).distinct().all()]
    if not subjects:
        raise ValidationAPIError(
            "No questions available — seed the question bank before starting an assessment"
        )

    per_subject = max(1, DIAGNOSTIC_QUESTION_COUNT // len(subjects))
    questions: list[Question] = []
    for subject in subjects:
        questions.extend(db.query(Question).filter_by(subject=subject).limit(per_subject).all())

    # Top up with more from any subject if rounding left us short (e.g. 10
    # questions / 3 subjects = 3 each = 9, not 10).
    if len(questions) < DIAGNOSTIC_QUESTION_COUNT:
        seen_ids = {q.id for q in questions}
        extra = (
            db.query(Question)
            .filter(~Question.id.in_(seen_ids) if seen_ids else True)
            .limit(DIAGNOSTIC_QUESTION_COUNT - len(questions))
            .all()
        )
        questions.extend(extra)

    assessment = Assessment(student_id=student_id, assessment_type=assessment_type)
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
