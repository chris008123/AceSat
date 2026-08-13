"""Knowledge base loader/lookup — the interface the Coaching Agent should
use to fetch an explanation for a topic (Prompt_strategy.txt §7 "Coaching
Agent Prompt Strategy": "Explain the concept" needs source material to
explain from).

Loads from `knowledge/sample_concepts.json` for now — swap `load_concepts()`
for a DB or file-directory-backed version once there's enough real content
that hand-maintaining one JSON file stops being practical (that's a Phase 7
question, not a Phase 6 one).
"""

from __future__ import annotations

import json
from pathlib import Path

from ai_data.knowledge.concepts import Concept

_DEFAULT_CONTENT_PATH = Path(__file__).parent / "sample_concepts.json"


def load_concepts(path: Path | None = None) -> list[Concept]:
    content_path = path or _DEFAULT_CONTENT_PATH
    with open(content_path) as f:
        raw = json.load(f)
    return [Concept.model_validate(item) for item in raw]


def get_concepts_for_topic(topic: str, concepts: list[Concept] | None = None) -> list[Concept]:
    """Case-insensitive match on `Concept.topic` — matches how
    `performance_analyzer.py` groups responses by `QuestionResponse.topic`,
    so a weak topic identified there can look itself up here directly.
    """
    pool = concepts if concepts is not None else load_concepts()
    return [c for c in pool if c.topic.lower() == topic.lower()]
