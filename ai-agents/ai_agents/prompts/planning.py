"""Planning Agent prompt — Prompt_strategy.txt §6."""

from __future__ import annotations

from ai_data.services.context_builder import StudentContext

from ai_agents.prompts.base import build_system_prompt

ROLE_BLOCK = """Role: Planning Agent

Goal: Design the most effective study schedule for this student, using
their target score, exam timeline, weak areas, and available daily study
time (all in the context below).

Rules:
- Do NOT create a generic schedule. Every item must have a `reason` tied to
  something in the student's context (a weak topic, a declining trend, or —
  if the student has no weaknesses yet — reinforcing a strength).
- The total time across all items should roughly match the student's daily
  study time budget, not wildly exceed or fall short of it.
- Prioritize weak/declining topics first, then strong topics that are ready
  for harder material.
- Produce at most 4 items — a study plan a student can actually follow in
  one sitting, not an exhaustive list.

Output format (JSON only):
{
  "items": [
    {"topic": "<topic>", "duration_minutes": <int>, "reason": "<why this, why now>"}
  ]
}"""


def build_planning_prompt(context: StudentContext) -> tuple[str, str]:
    system = build_system_prompt(ROLE_BLOCK)
    user = (
        "Student context:\n"
        f"{context.model_dump_json(indent=2)}\n\n"
        "Build today's study plan and return the JSON described above."
    )
    return system, user
