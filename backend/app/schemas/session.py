"""Matches Api_design.txt §9 (Start/Complete Session)."""

from __future__ import annotations

from pydantic import BaseModel


class StartSessionResponse(BaseModel):
    session_id: str
    mission: str


class CompleteSessionRequest(BaseModel):
    accuracy: float
    duration: int


class CompleteSessionResponse(BaseModel):
    status: str = "completed"
    accuracy: float
    duration: int
