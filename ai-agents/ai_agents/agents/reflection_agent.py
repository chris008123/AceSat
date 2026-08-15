"""Reflection Agent — AI_Agent_architecture.txt §4.6 / Agents.txt.

Surfaces a short post-lesson question about difficulty/confidence
(Product_features.txt Feature 10). Deliberately not LLM-backed — there's
no ambiguity to resolve in "ask how a lesson felt," so this stays a
simple, fast, zero-cost deterministic agent. No dedicated route consumes
it yet; available for `/sessions/complete` or the session-summary screen
to call.
"""

from __future__ import annotations

from ai_agents.agents.base import BaseAgent
from ai_agents.schemas import ReflectionPrompt


class ReflectionAgent(BaseAgent):
    name = "Reflection Agent"

    def run(self, topic: str | None = None) -> ReflectionPrompt:
        question = f"How difficult was {topic}?" if topic else "How difficult was today's session?"
        return ReflectionPrompt(question=question)
