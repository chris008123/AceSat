"""Vector search — hackathon prompt section 10.

Stores embeddings as a portable JSON float array (works on SQLite for
local dev and Postgres in production) and computes cosine similarity in
pure Python. This intentionally does NOT require the `pgvector` Postgres
extension to be enabled — the prompt says to keep retrieval modular enough
to disable for the MVP, so this whole subsystem is opt-in: nothing else in
`ai_data` imports from `retrieval/`, and a team that doesn't need semantic
search can delete this folder without touching anything else.

If/when the corpus grows large enough that Python-side cosine similarity
is too slow, swap `VectorSearchService`'s storage for a real `pgvector`
column — `EmbeddingProvider` and the public methods below don't need to
change, only the internals of `index_concepts`/`search`.
"""

from __future__ import annotations

import math
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import JSON, DateTime, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, Session, mapped_column

from ai_data.knowledge.concepts import Concept
from ai_data.models.base import Base
from ai_data.retrieval.embeddings import EmbeddingProvider

_JSONType = JSON().with_variant(JSONB, "postgresql")


class ConceptEmbeddingRecord(Base):
    """AI/Data-owned table, same portability approach as
    `models/mastery.py` / `models/memory.py` — no cross-module FK object
    until the Bases merge (see README boundary note)."""

    __tablename__ = "concept_embeddings"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    concept_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    topic: Mapped[str] = mapped_column(String, index=True)
    source_text: Mapped[str] = mapped_column(String)
    embedding: Mapped[list] = mapped_column(_JSONType)
    model_name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SearchResult(BaseModel):
    concept_id: UUID
    topic: str
    source_text: str
    score: float


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (norm_a * norm_b)


def _concept_source_text(concept: Concept) -> str:
    """What actually gets embedded — explanation plus example prompts, so
    a query phrased like a student's question can match against worked
    examples too, not just the formal explanation text."""
    parts = [concept.explanation] + [ex.prompt for ex in concept.examples]
    return " ".join(parts)


class VectorSearchService:
    def __init__(self, session: Session, provider: EmbeddingProvider):
        self._session = session
        self._provider = provider

    def index_concepts(self, concepts: list[Concept]) -> None:
        for concept in concepts:
            source_text = _concept_source_text(concept)
            embedding = self._provider.embed(source_text)
            record = ConceptEmbeddingRecord(
                concept_id=concept.concept_id,
                topic=concept.topic,
                source_text=source_text,
                embedding=embedding,
                model_name=type(self._provider).__name__,
            )
            self._session.merge(record)

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        query_embedding = self._provider.embed(query)
        records = self._session.query(ConceptEmbeddingRecord).all()
        scored = [
            SearchResult(
                concept_id=r.concept_id,
                topic=r.topic,
                source_text=r.source_text,
                score=_cosine_similarity(query_embedding, r.embedding),
            )
            for r in records
        ]
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]
