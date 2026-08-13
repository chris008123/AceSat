"""Matches Api_design.txt §7 (Start/Submit Answer/Complete Assessment)."""

from __future__ import annotations

from pydantic import BaseModel


class AssessmentQuestion(BaseModel):
    id: str
    subject: str
    difficulty: int


class StartAssessmentResponse(BaseModel):
    assessment_id: str
    questions: list[AssessmentQuestion]


class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer: str
    confidence: int
    time_taken: int


class SubmitAnswerResponse(BaseModel):
    correct: bool
    correct_answer: str


class CompleteAssessmentResponse(BaseModel):
    status: str = "completed"
    message: str = "Generating your learning profile"
    score: float
