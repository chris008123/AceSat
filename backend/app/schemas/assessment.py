"""Matches Api_design.txt §7 (Start/Submit Answer/Complete Assessment)."""

from __future__ import annotations

from pydantic import BaseModel


class QuestionOptionOut(BaseModel):
    letter: str
    text: str


class AssessmentQuestion(BaseModel):
    id: str
    subject: str
    topic: str
    difficulty: int
    # Extended for frontend integration (BACKEND_INTEGRATION.md §4): the
    # frontend's `Question` type needs the actual prompt/options/answer
    # key/explanation to render `QuestionCard`, not just subject/
    # difficulty metadata. `QuestionCard` grades client-side the instant
    # a student picks an answer, so `correct_answer`/`explanation` are
    # included up front rather than withheld until a server round trip —
    # a deliberate simplification flagged here, not a security boundary
    # this MVP relies on. `POST /assessment/answer` is still called to
    # persist the real answer for scoring/diagnosis.
    question_text: str
    options: list[QuestionOptionOut]
    correct_answer: str
    explanation: str | None = None


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
