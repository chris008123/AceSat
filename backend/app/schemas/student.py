"""Matches Api_design.txt §6 (Get/Update Student Profile)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class StudentProfileResponse(BaseModel):
    target_score: int
    current_score: int | None
    exam_date: date | None
    study_time: int
    confidence_level: int | None
    learning_style: str | None

    model_config = {"from_attributes": True}


class StudentProfileUpdateRequest(BaseModel):
    target_score: int | None = None
    current_score: int | None = None
    exam_date: date | None = None
    study_time: int | None = None
    confidence_level: int | None = None
    learning_style: str | None = None
