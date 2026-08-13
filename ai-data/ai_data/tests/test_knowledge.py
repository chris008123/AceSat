from __future__ import annotations

from ai_data.knowledge.loader import get_concepts_for_topic, load_concepts


def test_load_concepts_returns_parsed_models():
    concepts = load_concepts()
    assert len(concepts) >= 3
    assert all(c.explanation for c in concepts)


def test_get_concepts_for_topic_matches_case_insensitively():
    concepts = load_concepts()
    matches = get_concepts_for_topic("reading inference", concepts=concepts)
    assert len(matches) == 1
    assert matches[0].topic == "Reading Inference"


def test_get_concepts_for_topic_no_match_returns_empty():
    concepts = load_concepts()
    assert get_concepts_for_topic("Quantum Mechanics", concepts=concepts) == []


def test_weak_topic_from_analyzer_resolves_to_a_concept(declining_reading_inference_responses):
    from ai_data.services.performance_analyzer import identify_weak_topics

    weak_topics = identify_weak_topics(declining_reading_inference_responses)
    assert weak_topics  # sanity check the fixture still produces a weak topic
    matches = get_concepts_for_topic(weak_topics[0])
    assert matches, f"no concept found for weak topic {weak_topics[0]!r}"
