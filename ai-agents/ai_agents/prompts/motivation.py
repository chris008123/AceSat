"""Motivation Agent prompt — Prompt_strategy.txt §10."""

from __future__ import annotations

from ai_agents.prompts.base import build_system_prompt

ROLE_BLOCK = """Role: Motivation Agent

Your role is to encourage the student, referencing their actual streak and
progress — never empty, generic praise.

Rules:
- Reference the specific `streak` number (and `recent_improvement` if
  given) in the message.
- Keep it to one or two sentences.
- Do not invent achievements that aren't in the data provided.

Output format (JSON only):
{
  "message": "<one or two sentence, specific encouragement>"
}"""


def build_motivation_prompt(streak: int, recent_improvement: str | None) -> tuple[str, str]:
    system = build_system_prompt(ROLE_BLOCK)
    user = (
        f"streak: {streak} days\n"
        f"recent_improvement: {recent_improvement or 'none recorded'}\n\n"
        "Write the encouragement message and return the JSON described above."
    )
    return system, user
