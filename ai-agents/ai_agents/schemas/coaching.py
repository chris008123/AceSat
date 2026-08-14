"""Coaching Agent output contract — AI_Agent_architecture.txt §4.3 /
Prompt_strategy.txt §7-8 (Explain / Guide / Practice / Confirm framework).

The Coaching Agent teaches rather than answers directly — `response_type`
lets the orchestrator/frontend distinguish "here's an explanation" from
"here's a hint, keep trying" without parsing `message` text.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ai_agents.schemas.enums import CoachingResponseType


class CoachingResponse(BaseModel):
    student_id: UUID
    concept: str = Field(description="The topic/concept this turn is about, e.g. "
                          "'Quadratic Equations' — matches Question.topic.")

    response_type: CoachingResponseType = Field(
        description="What kind of turn this is — an explanation, a hint, a guiding "
        "question, feedback on an attempt, or encouragement."
    )
    message: str = Field(description="The actual student-facing text.")

    follow_up_question: str | None = Field(
        default=None,
        description="A question to pose back to the student, per the 'ask useful "
        "follow-up questions' responsibility — e.g. a worked-example prompt. "
        "Omitted when response_type is pure feedback/encouragement with no next step.",
    )
    gives_direct_answer: bool = Field(
        default=False,
        description="True only when directly answering is appropriate (e.g. after "
        "repeated guided attempts). Prompt_strategy.txt §7: 'Avoid giving immediate "
        "answers unless appropriate' — this flag makes that choice explicit and "
        "auditable rather than implicit in free text.",
    )

    coaching_response_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
