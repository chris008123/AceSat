"""Knowledge base structure — hackathon prompt section 9.

Organizes SAT content by subject/domain/topic/subtopic/concept, each with
an explanation, worked examples, and links to practice questions. This is
deliberately a thin structure (no RAG, no chunking strategy) per the
prompt's own instruction: "Do not create an unnecessarily complicated RAG
system unless the project actually needs it." Phase 7 (retrieval) can sit
on top of this later without changing this shape.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ai_data.models.enums import DifficultyLevel, Subject


class ConceptExample(BaseModel):
    prompt: str = Field(description="A short worked example question or scenario")
    solution: str = Field(description="Step-by-step resolution, in plain language")


class Concept(BaseModel):
    """The unit the AI Coach actually teaches from — matches the
    "Explain / Guide / Practice / Confirm" framework in Prompt_strategy.txt
    §8. One concept usually has several practice `Question`s tagged with
    its `topic`/`subtopic` in `models/question.py`."""

    concept_id: UUID = Field(default_factory=uuid4)
    subject: Subject
    domain: str = Field(description="e.g. 'Algebra', 'Craft and Structure'")
    topic: str = Field(description="e.g. 'Linear Equations' — matches Question.topic")
    subtopic: str | None = None
    difficulty: DifficultyLevel
    explanation: str = Field(description="Clear, student-facing explanation of the concept")
    examples: list[ConceptExample] = Field(default_factory=list)
    practice_question_ids: list[UUID] = Field(
        default_factory=list, description="Question.question_id values that practice this concept"
    )
    related_concept_ids: list[UUID] = Field(
        default_factory=list, description="Prerequisite or closely related concepts, for sequencing"
    )
