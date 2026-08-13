# Evaluation (Phase 8 — done)

Hackathon prompt section 11 asks for scenarios covering: weak algebra,
weak reading inference, improving rapidly, inconsistent performance, and
repeated mistakes. All 5 are in `datasets/` as JSON, each with a
`topics` block of per-topic `correct_sequence` (chronological
right/wrong) and an `expected_weakness` / `expected_recommendation_action`
pair — verified against the real `performance_analyzer` /
`recommendation_context` code before being committed, not hand-guessed.

`evaluator.py` turns each scenario into synthetic `QuestionResponse`s,
runs them through `identify_weak_topics()` and
`generate_topic_recommendations()`, and checks the result matches. This is
what `tests/test_evaluation.py` runs — one parametrized test per scenario.

Once the AI Agent Engineer's agents exist, point them at these same
datasets to check *their* behavior personalizes correctly too — the
scenario format doesn't need to change for that.
