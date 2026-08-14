"""Analytics Agent output contract — AI_Agent_architecture.txt §4.4 /
hackathon prompt's Analytics Agent section.

Input is student performance history (via `ai_data`'s performance engine /
`StudentContext`) — output-only shape here, per Phase 1 scope.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ai_agents.schemas.enums import AnalyticsStatus


class TopicTrend(BaseModel):
    topic: str
    status: AnalyticsStatus
    detail: str = Field(description="e.g. 'accuracy improved from 55% to 72% over 2 weeks'.")


class AnalyticsResult(BaseModel):
    student_id: UUID

    overall_status: AnalyticsStatus = Field(
        description="Single top-line read on the student's trajectory right now."
    )
    topic_trends: list[TopicTrend] = Field(default_factory=list)

    summary: str = Field(
        description="Concise, human-readable progress summary — e.g. the hackathon "
        "prompt's weekly report example ('Accuracy: 68% -> 76%, Improvement: +8%')."
    )
    reasoning: str = Field(
        description="Why overall_status was chosen — evidence-based, not a placeholder."
    )
    confidence: float = Field(ge=0.0, le=1.0)

    recommended_next_action: str | None = Field(
        default=None,
        description="Actionable takeaway for the Planning Agent, e.g. 'increase reading "
        "practice' or 'ready to raise difficulty on algebra questions'.",
    )

    analytics_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
