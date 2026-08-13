from __future__ import annotations

import pytest

from ai_data.knowledge.loader import load_concepts
from ai_data.models.db import get_session, init_db
from ai_data.retrieval.embeddings import DeterministicEmbeddingProvider
from ai_data.retrieval.vector_search import VectorSearchService


@pytest.fixture
def retrieval_db(tmp_path):
    db_url = f"sqlite:///{tmp_path}/test_retrieval.db"
    init_db(db_url)
    return db_url


def test_index_and_search_returns_best_match(retrieval_db):
    concepts = load_concepts()
    provider = DeterministicEmbeddingProvider(dimensions=64)

    with get_session(retrieval_db) as session:
        service = VectorSearchService(session, provider)
        service.index_concepts(concepts)

    with get_session(retrieval_db) as session:
        service = VectorSearchService(session, provider)
        # Query built from the Reading Inference concept's own explanation
        # text — the closest match by construction, since the deterministic
        # provider is just a hashed bag-of-words over the query terms.
        reading_concept = next(c for c in concepts if c.topic == "Reading Inference")
        results = service.search(reading_concept.explanation, top_k=1)

    assert len(results) == 1
    assert results[0].topic == "Reading Inference"


def test_search_returns_top_k_ordered_by_score(retrieval_db):
    concepts = load_concepts()
    provider = DeterministicEmbeddingProvider(dimensions=64)

    with get_session(retrieval_db) as session:
        service = VectorSearchService(session, provider)
        service.index_concepts(concepts)

    with get_session(retrieval_db) as session:
        service = VectorSearchService(session, provider)
        results = service.search("solve for x algebra equation", top_k=2)

    assert len(results) == 2
    assert results[0].score >= results[1].score
