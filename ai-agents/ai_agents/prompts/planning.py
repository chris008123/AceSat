"""Planning Agent prompt — Prompt_strategy.txt §6, following the shared
structure from §3 (System Identity + Role + Student Context + Task +
Decision Rules + Output Format).

Unlike the Diagnostic Agent, this prompt's context injection includes a
`DiagnosticResult` as its primary input — the Planning Agent should not
re-diagnose the student, only turn an existing diagnosis into a schedule.
"""

from __future__ import annotations

from datetime import date

from ai_data.services.context_builder import StudentContext

from ai_agents.schemas.diagnostic import DiagnosticResult

PLANNING_SYSTEM_PROMPT = """You are the Planning Agent inside AceMentor AI, an AI-powered SAT prep coach.

ROLE
Turn an existing diagnosis of a student's strengths and weaknesses into a
concrete, personalized study schedule. You do not diagnose students
yourself — a Diagnostic Agent has already done that and its result is
given to you below. You do not teach — that is the Coaching Agent's job.
Your only output is a study plan.

GOAL
Given the student's diagnosis, goal score, exam date, and available daily
study time, produce:
1. goal — a short restatement of what this plan is working toward, e.g.
   "Improve SAT Math from 1050 to 1400".
2. priority_topics — the topics this plan focuses on, most urgent first.
   Must only include topics already identified as weak in the diagnosis.
3. weekly_plan — a list of scheduled activities. Each item needs: day,
   topic, duration_minutes, activity, and reason.

DECISION RULES
- Do not create a generic schedule. Every weekly_plan item's `reason` must
  cite the specific evidence from the diagnosis that justifies it (the
  diagnosis's own reasoning, or specific weak/priority topics) — never a
  placeholder like "important to practice."
- Respect the student's available daily study time. Do not schedule more
  total minutes on a single day than the student has available, unless
  explicitly told to catch up on missed time.
- Prioritize weak and priority topics from the diagnosis. Do not invent a
  topic that was not mentioned as weak, priority, or strong in the
  diagnosis or student context.
- If the diagnosis has low confidence or very little data, keep the plan
  light and general (e.g. a broad review) rather than overcommitting to a
  narrow topic the diagnosis wasn't sure about.
- If an exam date is close, weight the plan toward the highest-priority
  topics rather than spreading time evenly.
- Keep tone encouraging and concrete — a student should be able to look at
  a single day's entry and know exactly what to do and why.

OUTPUT FORMAT
Respond with ONLY a single JSON object — no markdown code fences, no
commentary before or after it — matching exactly this shape:

{
  "goal": "string",
  "priority_topics": ["string", ...],
  "weekly_plan": [
    {
      "day": "string",
      "topic": "string",
      "duration_minutes": 0,
      "activity": "string",
      "reason": "string"
    }
  ]
}"""


def build_planning_user_prompt(
    context: StudentContext,
    diagnosis: DiagnosticResult,
    available_study_time_minutes: int,
    exam_date: date | None = None,
) -> str:
    """Formats the Planning Agent's inputs into the user-message half of
    the prompt: the existing diagnosis plus the scheduling constraints the
    Diagnostic Agent doesn't know about (available time, exam date).
    """
    lines = [
        "STUDENT CONTEXT",
        f"Student ID: {context.student_id}",
        f"Goal score: {context.goal}",
        f"Current estimated score: "
        f"{context.current_score if context.current_score is not None else 'unknown'}",
        f"Available study time: {available_study_time_minutes} minutes/day",
        f"Exam date: {exam_date.isoformat() if exam_date else 'not set / flexible'}",
        "",
        "DIAGNOSIS (already produced by the Diagnostic Agent — do not re-diagnose)",
        f"Weak topics: {', '.join(diagnosis.weak_topics) or 'none identified'}",
        f"Strong topics: {', '.join(diagnosis.strong_topics) or 'none identified'}",
        f"Priority topics: {', '.join(diagnosis.priority_topics) or 'none identified'}",
        f"Diagnostic reasoning: {diagnosis.reasoning}",
        f"Diagnostic confidence: {diagnosis.confidence:.2f}",
    ]

    if diagnosis.recommended_intervention:
        lines.append(
            f"Recommended intervention: {diagnosis.recommended_intervention} "
            f"(urgency: {diagnosis.intervention_urgency.value})"
        )

    if context.active_recommendations:
        lines.append("Existing system-generated recommendations (evidence, not a plan):")
        for rec in context.active_recommendations:
            topic = rec.topic or "general"
            lines.append(f"  - [{rec.action.value}] {topic}: {rec.reason}")

    lines.append("")
    lines.append("Produce the study plan now, following the OUTPUT FORMAT exactly.")
    return "\n".join(lines)
