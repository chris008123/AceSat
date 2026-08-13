"""Matches Api_design.txt §8 (Generate Diagnosis / Study Plan / Coach).

These are the *backend's* API contract shapes — kept intentionally
separate from ai-data's own Pydantic models (`ai_data.models.student.
StudentLearningProfile`, `ai_data.models.recommendation.Recommendation`,
etc.). `app/services/ai_bridge.py` is the only place that translates
between the two, so this API contract doesn't change even if ai-data's
internal shapes do.
"""

from __future__ import annotations

from pydantic import BaseModel


class DiagnoseResponse(BaseModel):
    weaknesses: list[str]
    strengths: list[str]
    recommendation: str


class StudyPlanItem(BaseModel):
    topic: str
    time: str
    reason: str


class StudyPlanResponse(BaseModel):
    plan: list[StudyPlanItem]


class CoachRequest(BaseModel):
    question: str


class CoachResponse(BaseModel):
    explanation: str
    next_question: str | None = None
