"""Exceptions the orchestration layer can raise. Deliberately small — most
failure modes (LLM down, bad JSON, missing key) are handled *inside* an
agent by falling back to its deterministic path (see `agents/base.py`),
not by raising. What's left here are cases where there's genuinely
nothing to fall back to.
"""

from __future__ import annotations


class NoTeachingMaterialError(Exception):
    """Raised by the Coaching Agent when a weak topic has no matching
    entry in ai-data's knowledge base (`ai_data.knowledge.loader`) and the
    LLM path also isn't available — there's no explanation to give. The
    backend maps this to a 404, same as the original ai_bridge behavior.
    """

    def __init__(self, topic: str):
        self.topic = topic
        super().__init__(f"No teaching material found for {topic!r} yet")
