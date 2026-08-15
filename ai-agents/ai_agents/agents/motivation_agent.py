"""Motivation Agent — AI_Agent_architecture.txt §4.5 / Agents.txt.

Maintains engagement using real numbers (streaks, milestones) rather than
generic praise, per Prompt_strategy.txt §10. No dedicated `/ai/*` route
exists for this yet (Api_design.txt has none) — available for the
dashboard to call alongside `/progress/dashboard`'s `streak` field.
"""

from __future__ import annotations

from pydantic import ValidationError

from ai_agents.agents.base import BaseAgent
from ai_agents.prompts.motivation import build_motivation_prompt
from ai_agents.schemas import MotivationResult


class MotivationAgent(BaseAgent):
    name = "Motivation Agent"

    def run(self, streak: int, recent_improvement: str | None = None) -> MotivationResult:
        system, user = build_motivation_prompt(streak, recent_improvement)
        raw = self._try_llm(system, user)
        if raw is not None:
            try:
                return MotivationResult(**raw, source="llm")
            except (ValidationError, TypeError):
                pass
        return self._fallback(streak, recent_improvement)

    def _fallback(self, streak: int, recent_improvement: str | None) -> MotivationResult:
        if streak >= 7:
            message = f"Great work — {streak} days of consistent practice. That streak is real momentum."
        elif streak >= 1:
            message = f"Day {streak} of your streak — keep it going."
        else:
            message = "Ready when you are — starting today builds tomorrow's streak."

        if recent_improvement:
            message = f"{message} {recent_improvement}"

        return MotivationResult(message=message, source="deterministic")
