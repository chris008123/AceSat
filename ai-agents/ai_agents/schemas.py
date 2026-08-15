"""Structured agent outputs — Prompt_strategy.txt §16 ("Structured AI
Outputs"): every agent returns one of these instead of free text, so the
backend can render/persist a response without parsing prose, and so a
result can be logged to `ai_logs` (Database_design.txt §5.10) as clean
JSON.

Every result carries a `source` field ("llm" or "deterministic") — not
part of any Api_design.txt contract, the backend response schemas don't
expose it — but it matters for debugging/demoing which path actually
produced a given answer (Prompt_strategy.txt §17's "Prompt Improvement
Loop" needs to know that to be useful).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Source = Literal["llm", "deterministic"]


class DiagnosticResult(BaseModel):
    """Diagnostic Agent output — AI_Agent_architecture.txt §4.1."""

    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    reason: str = Field(description="Concrete, evidence-based explanation of the main gap.")
    recommendation: str
    source: Source = "deterministic"


class StudyPlanItemResult(BaseModel):
    topic: str
    duration_minutes: int = Field(gt=0)
    reason: str


class StudyPlanResult(BaseModel):
    """Planning Agent output — AI_Agent_architecture.txt §4.2."""

    items: list[StudyPlanItemResult] = Field(default_factory=list)
    source: Source = "deterministic"


class CoachResult(BaseModel):
    """Coaching Agent output — AI_Agent_architecture.txt §4.3. Follows the
    Explain/Guide/Practice/Confirm framework (Prompt_strategy.txt §8):
    `explanation` teaches, `next_question` guides rather than hands over
    the answer.
    """

    explanation: str
    next_question: str | None = None
    source: Source = "deterministic"


class AnalyticsResult(BaseModel):
    """Analytics Agent output — AI_Agent_architecture.txt §4.4."""

    summary: str
    trend: Literal["improving", "declining", "steady", "insufficient_data"]
    accuracy_change: float
    source: Source = "deterministic"


class MotivationResult(BaseModel):
    """Motivation Agent output — AI_Agent_architecture.txt §4.5. Must
    reference something real about the student (streak, improvement),
    never generic praise, per Prompt_strategy.txt §10.
    """

    message: str
    source: Source = "deterministic"


class ReflectionPrompt(BaseModel):
    """Reflection Agent output — AI_Agent_architecture.txt §4.6. A single
    question to surface to the student after a lesson; not LLM-generated
    (no ambiguity to resolve here), kept structured for the frontend
    (Product_features.txt Feature 10 shows a fixed 3-option UI).
    """

    question: str
    options: list[str] = Field(default_factory=lambda: ["Easy", "Medium", "Hard"])
