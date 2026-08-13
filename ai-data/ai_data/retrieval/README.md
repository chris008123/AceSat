# Vector retrieval (Phase 7 — done, opt-in)

Semantic search over concept explanations (hackathon prompt section 10).
Deliberately isolated: nothing outside `retrieval/` imports from it, so a
team that decides the MVP doesn't need semantic search can delete this
folder without touching `services/` or `knowledge/`.

- `embeddings.py` — `EmbeddingProvider` protocol. `DeterministicEmbeddingProvider`
  (hash-based, no API key/network — what tests and local dev use) and
  `GoogleEmbeddingProvider` (stub for the real Gemini/Google embeddings API;
  raises `NotImplementedError` until `AI_API_KEY` is wired in).
- `vector_search.py` — `VectorSearchService.index_concepts()` /
  `.search()`. Stores embeddings as a portable JSON float array (works on
  SQLite and Postgres) and computes cosine similarity in pure Python — does
  **not** require the `pgvector` Postgres extension. If the corpus grows
  large enough that this gets slow, swap the storage for a real `pgvector`
  column later; the public interface doesn't need to change.
