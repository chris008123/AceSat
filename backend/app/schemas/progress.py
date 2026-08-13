"""Matches Api_design.txt §10 (Dashboard / Weekly Report)."""

from __future__ import annotations

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    current_score: int | None
    improvement: str
    weak_area: str | None
    streak: int


class WeeklyReportResponse(BaseModel):
    study_hours: float
    questions_completed: int
    recommendation: str
