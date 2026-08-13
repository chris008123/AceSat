"""Assessment routes — Api_design.txt §7."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.assessment import (
    AssessmentQuestion,
    CompleteAssessmentResponse,
    StartAssessmentResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services import assessment_service, student_service

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.post("/start", response_model=StartAssessmentResponse)
def start(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StartAssessmentResponse:
    profile = student_service.get_profile(db, user.id)
    assessment, questions = assessment_service.start_assessment(db, profile.id)
    return StartAssessmentResponse(
        assessment_id=str(assessment.id),
        questions=[
            AssessmentQuestion(id=str(q.id), subject=q.subject, difficulty=q.difficulty) for q in questions
        ],
    )


@router.post("/answer", response_model=SubmitAnswerResponse)
def answer(
    payload: SubmitAnswerRequest,
    assessment_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmitAnswerResponse:
    profile = student_service.get_profile(db, user.id)
    saved_answer, correct_answer = assessment_service.submit_answer(
        db,
        assessment_id=assessment_id,
        student_id=profile.id,
        question_id=payload.question_id,
        answer_given=payload.answer,
        confidence=payload.confidence,
        time_taken=payload.time_taken,
    )
    return SubmitAnswerResponse(correct=saved_answer.correct, correct_answer=correct_answer)


@router.post("/complete", response_model=CompleteAssessmentResponse)
def complete(
    assessment_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompleteAssessmentResponse:
    profile = student_service.get_profile(db, user.id)
    assessment = assessment_service.complete_assessment(db, assessment_id, profile.id)
    return CompleteAssessmentResponse(score=assessment.score)
