"""Recommendation data structures — hackathon prompt section 8.

This module produces the *data* (what to recommend + why), not the
decision of which agent acts on it — that orchestration belongs to the AI
Agent Engineer.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ai_data.models.enums import RecommendationAction


class Recommendation(BaseModel):
    action: RecommendationAction
    topic: str | None = None
    reason: str = Field(description="Must be a concrete, evidence-based explanation — "
                         "e.g. 'accuracy dropped from 68% to 47% over the last 3 attempts', "
                         "never a generic placeholder.")
    supporting_evidence: dict = Field(
        default_factory=dict,
        description="Raw numbers backing `reason`, e.g. {'previous_accuracy': 0.68, "
        "'current_accuracy': 0.47, 'attempts_considered': 3}",
    )
    priority: int = Field(default=3, ge=1, le=5, description="1 = highest priority")
    recommendation_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
