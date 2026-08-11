"""Question bank representation.

Read model over the backend-owned `questions` table (10_Database_Design.md
§5.4), extended with the fields the hackathon prompt's section 2 ("Question
Bank") asks for that aren't in the DB doc yet (`subtopic`, `skills_tested`,
`source`) — flag these as a possible migration addition for the Backend
Engineer rather than inventing a second table.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from ai_data.models.enums import DifficultyLevel, QuestionType, Subject


class Question(BaseModel):
    question_id: UUID
    subject: Subject
    domain: str = Field(description="e.g. 'Algebra', 'Craft and Structure'")
    topic: str = Field(description="e.g. 'Linear Equations'")
    subtopic: str | None = None
    difficulty: DifficultyLevel
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    question_text: str
    answer_options: dict[str, str] | None = None
    correct_answer: str
    explanation: str | None = None
    skills_tested: list[str] = Field(default_factory=list)
    source: str | None = None
