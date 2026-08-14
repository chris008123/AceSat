"""Diagnostic Agent output contract — AI_Agent_architecture.txt §4.1 /
hackathon prompt's Diagnostic Agent section.

Input to the agent that produces this is `ai_data.services.context_builder.
StudentContext` (built from a `StudentLearningProfile`) plus optionally
`ai_data`'s `Recommendation` list — this module only defines the *output*
shape, per Phase 1 scope.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ai_agents.schemas.enums import InterventionUrgency


class DiagnosticResult(BaseModel):
    """Structured output of the Diagnostic Agent.

    Every field maps directly to the hackathon prompt's Diagnostic Agent
    output list: Weak Topics, Strong Topics, Priority Topics, Reasoning,
    Confidence, Recommended Intervention.
    """

    student_id: UUID

    weak_topics: list[str] = Field(
        default_factory=list, description="Topics where the student is underperforming."
    )
    strong_topics: list[str] = Field(
        default_factory=list, description="Topics where the student is performing well."
    )
    priority_topics: list[str] = Field(
        default_factory=list,
        description="Ranked subset of weak_topics the student should address first — "
        "must be a subset of weak_topics, most urgent first.",
    )

    reasoning: str = Field(
        description="Concise, evidence-based explanation for the diagnosis — e.g. "
        "'accuracy on quadratic equations dropped from 72% to 48% over the last 3 "
        "attempts'. Never a generic placeholder (Prompt_strategy.txt §17 guardrail)."
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Agent's confidence in this diagnosis, 0-1."
    )

    recommended_intervention: str | None = Field(
        default=None,
        description="What should happen next in plain language, e.g. 'assign a "
        "foundational lesson on factoring before more practice questions'.",
    )
    intervention_urgency: InterventionUrgency = InterventionUrgency.NONE

    diagnostic_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
