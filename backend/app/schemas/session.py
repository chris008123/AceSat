"""Matches Api_design.txt §9 (Start/Complete Session)."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.assessment import AssessmentQuestion


class StartSessionResponse(BaseModel):
    session_id: str
    mission: str
    # Added for frontend integration: Api_design.txt §9 only specifies
    # `mission`, but `/session` needs actual practice questions to render
    # (BACKEND_INTEGRATION.md §3) — there was no endpoint that supplied
    # them. Reuses the same question shape `/assessment/start` returns.
    questions: list[AssessmentQuestion] = []


class CompleteSessionRequest(BaseModel):
    accuracy: float
    duration: int


class CompleteSessionResponse(BaseModel):
    status: str = "completed"
    accuracy: float
    duration: int
