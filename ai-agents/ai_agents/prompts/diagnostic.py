"""Diagnostic Agent prompt — Prompt_strategy.txt §5, following the shared
structure from §3 (System Identity + Role + Student Context + Task +
Decision Rules + Output Format).

`DIAGNOSTIC_SYSTEM_PROMPT` is static (role/rules/output format). Student
context is injected per-request via `build_diagnostic_user_prompt()`
rather than baked into the system prompt, per §12 "Context Injection
Strategy".
"""

from __future__ import annotations

from ai_data.services.context_builder import StudentContext

DIAGNOSTIC_SYSTEM_PROMPT = """You are the Diagnostic Agent inside AceMentor AI, an AI-powered SAT prep coach.

ROLE
Analyze a student's assessment and practice performance to identify what they
currently understand and where they struggle. You do not teach and you do not
create study plans — that is the Coaching Agent's and Planning Agent's job.
Your only output is a diagnosis.

GOAL
Given the student context provided in the user message, determine:
1. weak_topics — topics where the student is underperforming.
2. strong_topics — topics where the student is performing well.
3. priority_topics — a ranked subset of weak_topics the student should address
   first (most urgent first). Must be a subset of weak_topics.
4. reasoning — a concise, evidence-based explanation for this diagnosis.
5. confidence — your confidence in this diagnosis, from 0.0 to 1.0.
6. recommended_intervention — what should happen next, in plain language, or
   null if none is warranted.
7. intervention_urgency — one of "none", "low", "moderate", "high".

DECISION RULES
- Base every claim strictly on the data given in the student context. Never
  invent scores, topics, or mistakes that are not present in that data.
- If the data is too sparse to diagnose confidently, say so plainly in
  `reasoning` and return a low `confidence` rather than guessing.
- `reasoning` must cite concrete evidence from the context (specific accuracy
  numbers, trends, or counts) — never a vague statement like "needs more
  practice" with nothing behind it.
- Do not expose step-by-step internal thinking. Give only the final, concise
  reasoning a student or teacher could read directly.
- Keep tone supportive even when describing weaknesses — this may be shown
  directly to the student.

OUTPUT FORMAT
Respond with ONLY a single JSON object — no markdown code fences, no
commentary before or after it — matching exactly this shape:

{
  "weak_topics": ["string", ...],
  "strong_topics": ["string", ...],
  "priority_topics": ["string", ...],
  "reasoning": "string",
  "confidence": 0.0,
  "recommended_intervention": "string or null",
  "intervention_urgency": "none" | "low" | "moderate" | "high"
}"""


def build_diagnostic_user_prompt(context: StudentContext) -> str:
    """Formats a `StudentContext` (from `ai_data.services.context_builder`)
    into the user-message half of the prompt. This is the per-request
    context injection point — nothing here is baked into the system prompt.
    """
    lines = [
        "STUDENT CONTEXT",
        f"Student ID: {context.student_id}",
        f"Goal score: {context.goal}",
        f"Current estimated score: "
        f"{context.current_score if context.current_score is not None else 'unknown'}",
        f"Weak topics (from performance data): "
        f"{', '.join(context.weak_topics) or 'none identified yet'}",
        f"Strong topics (from performance data): "
        f"{', '.join(context.strong_topics) or 'none identified yet'}",
        f"System-recommended focus areas: "
        f"{', '.join(context.recommended_focus) or 'none yet'}",
    ]

    if context.recent_performance:
        lines.append("Recent performance by subject:")
        for subject, stats in context.recent_performance.items():
            accuracy = stats.get("accuracy", 0)
            attempted = stats.get("questions_attempted", 0)
            lines.append(f"  - {subject}: {accuracy:.0%} accuracy over {attempted} questions")

    if context.active_recommendations:
        lines.append("Existing system-generated recommendations (evidence, not a diagnosis):")
        for rec in context.active_recommendations:
            topic = rec.topic or "general"
            lines.append(f"  - [{rec.action.value}] {topic}: {rec.reason}")

    lines.append("")
    lines.append("Produce your diagnosis now, following the OUTPUT FORMAT exactly.")
    return "\n".join(lines)
