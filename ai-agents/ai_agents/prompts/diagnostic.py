"""Diagnostic Agent prompt — Prompt_strategy.txt §5."""

from __future__ import annotations

from ai_data.services.context_builder import StudentContext

from ai_agents.prompts.base import build_system_prompt

ROLE_BLOCK = """Role: Diagnostic Agent

Goal: Analyze the student's performance data below and identify their
learning gaps and strengths.

Task: Determine
1. Strong topics (accuracy consistently high).
2. Weak topics (accuracy below mastery threshold, or declining).
3. The most likely cause of the primary weakness.
4. One concrete, specific recommendation.

Rules:
- Base every claim only on the numbers provided in the student context —
  never invent a topic or statistic that isn't there.
- `reason` must cite a concrete number (e.g. "accuracy is 47% across 8
  attempts"), never a vague statement like "needs improvement."
- If `weak_topics` in the context is empty, say so honestly rather than
  inventing a weakness.

Output format (JSON only):
{
  "strengths": ["<topic>", ...],
  "weaknesses": ["<topic>", ...],
  "reason": "<concrete, evidence-based explanation>",
  "recommendation": "<one specific next action>"
}"""


def build_diagnostic_prompt(context: StudentContext) -> tuple[str, str]:
    system = build_system_prompt(ROLE_BLOCK)
    user = (
        "Student context:\n"
        f"{context.model_dump_json(indent=2)}\n\n"
        "Analyze this student's performance and return the JSON described above."
    )
    return system, user
