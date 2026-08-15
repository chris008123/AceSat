# Knowledge base (Phase 6 — done)

Structured SAT content per hackathon prompt section 9: subject / domain /
topic / subtopic, each `Concept` carrying an explanation, worked examples,
and links to practice questions.

- `concepts.py` — the `Concept` / `ConceptExample` Pydantic models.
- `sample_concepts.json` — 3 representative entries (Reading Inference,
  Linear Equations, Grammar) so the shape is settled and demoable. Not
  meant to be the real content set — replace/extend once real SAT content
  exists.
- `loader.py` — `load_concepts()` / `get_concepts_for_topic()`, the
  interface the Coaching Agent should call. `get_concepts_for_topic()`
  matches directly against the same `topic` strings
  `performance_analyzer.identify_weak_topics()` returns, so a weak topic
  can be looked up here with no translation layer.

Deliberately no RAG/chunking/embedding here — that's Phase 7, and only if
the MVP demo actually needs semantic search.
