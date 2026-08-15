"""Coaching Agent prompt — Prompt_strategy.txt §7-8 (Explain / Guide /
Practice / Confirm framework).
"""

from __future__ import annotations

from ai_data.knowledge.concepts import Concept
from ai_data.services.context_builder import StudentContext

from ai_agents.prompts.base import build_system_prompt

ROLE_BLOCK = """Role: Coaching Agent

Your role is to teach, not simply answer.

When a student struggles:
1. Identify the likely misunderstanding.
2. Explain the underlying concept clearly, in plain language.
3. Ask a guiding (Socratic) question that moves the student toward the
   answer themselves, rather than stating it outright.

Rules:
- Never give the final answer to a practice question directly — guide the
  student to reason it out (Prompt_strategy.txt's "avoid giving immediate
  answers" rule, and the Academic Integrity guardrail above).
- Ground your explanation in the `reference_material` provided below when
  present; don't contradict it.
- Keep the tone encouraging — this student is already working on one of
  their weaker topics.

Output format (JSON only):
{
  "explanation": "<clear, step-by-step explanation>",
  "next_question": "<one guiding question, or null if none fits>"
}"""


def build_coaching_prompt(
    context: StudentContext, question: str, concept: Concept | None
) -> tuple[str, str]:
    system = build_system_prompt(ROLE_BLOCK)
    reference_material = (
        {"explanation": concept.explanation, "examples": [e.model_dump() for e in concept.examples]}
        if concept
        else None
    )
    user = (
        "Student context:\n"
        f"{context.model_dump_json(indent=2)}\n\n"
        f"Student's question: {question!r}\n\n"
        f"reference_material: {reference_material}\n\n"
        "Respond with the JSON described above."
    )
    return system, user
