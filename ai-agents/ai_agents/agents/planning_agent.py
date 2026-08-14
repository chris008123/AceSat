"""Planning Agent — AI_Agent_architecture.txt §4.2 / Development_roadmap.txt
Phase 3 Priority Agent 2.

Consumes `ai_data`'s `StudentContext` plus a `DiagnosticResult` (from
`DiagnosticAgent.diagnose()`) and produces a `StudyPlan` (Phase 1 schema),
backed by a Groq chat completion call.

Same testing approach as `diagnostic_agent.py`: the LLM call is injected as
`complete_fn` so tests never need a real GROQ_API_KEY or network access.
"""

from __future__ import annotations

import json
import os
from datetime import date
from typing import Callable

from pydantic import BaseModel, Field, ValidationError

from ai_data.services.context_builder import StudentContext

from ai_agents.prompts.planning import PLANNING_SYSTEM_PROMPT, build_planning_user_prompt
from ai_agents.schemas.diagnostic import DiagnosticResult
from ai_agents.schemas.planning import StudyPlan, StudyPlanItem

DEFAULT_GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

CompleteFn = Callable[[list[dict]], str]


class PlanningAgentError(Exception):
    """Raised when the LLM response can't be turned into a valid StudyPlan
    — bad JSON, or JSON that doesn't match the expected shape."""


class _PlanningLLMOutput(BaseModel):
    """What the LLM is responsible for producing — deliberately narrower
    than `StudyPlan`: `student_id`, `plan_id`, `generated_at`,
    `total_weekly_minutes`, and `exam_date` are all filled in by this
    module, never trusted from the model (total_weekly_minutes especially
    — recomputed from weekly_plan rather than trusting the model's math).
    """

    goal: str
    priority_topics: list[str] = Field(default_factory=list)
    weekly_plan: list[StudyPlanItem] = Field(default_factory=list)


def _default_groq_complete(messages: list[dict], *, model: str) -> str:
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise PlanningAgentError(
            "GROQ_API_KEY is not set. Set it in the environment (or backend/.env) "
            "before calling PlanningAgent without an explicit complete_fn."
        )

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return response.choices[0].message.content


class PlanningAgent:
    """Planning Agent. Usage:

        agent = PlanningAgent()  # uses real Groq call, needs GROQ_API_KEY
        plan = agent.plan(student_context, diagnosis, available_study_time_minutes=45)

    For tests, inject a fake completion function:

        agent = PlanningAgent(complete_fn=lambda messages: '{"goal": ..., ...}')
    """

    def __init__(self, complete_fn: CompleteFn | None = None, model: str = DEFAULT_GROQ_MODEL):
        self.model = model
        self._complete_fn = complete_fn or (
            lambda messages: _default_groq_complete(messages, model=self.model)
        )

    def plan(
        self,
        context: StudentContext,
        diagnosis: DiagnosticResult,
        available_study_time_minutes: int,
        exam_date: date | None = None,
    ) -> StudyPlan:
        messages = [
            {"role": "system", "content": PLANNING_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_planning_user_prompt(
                    context, diagnosis, available_study_time_minutes, exam_date
                ),
            },
        ]

        raw = self._complete_fn(messages)

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise PlanningAgentError(
                f"Planning Agent response was not valid JSON: {exc}\nRaw response: {raw!r}"
            ) from exc

        try:
            llm_output = _PlanningLLMOutput.model_validate(payload)
        except ValidationError as exc:
            raise PlanningAgentError(
                f"Planning Agent response did not match the expected schema: {exc}"
            ) from exc

        # priority_topics must only include topics the diagnosis actually
        # flagged as weak or priority — the prompt asks for this but
        # doesn't guarantee it; enforce it here rather than trusting the
        # model, same pattern as DiagnosticAgent's own guard.
        known_topics = set(diagnosis.weak_topics) | set(diagnosis.priority_topics)
        priority_topics = [t for t in llm_output.priority_topics if t in known_topics]

        total_weekly_minutes = sum(item.duration_minutes for item in llm_output.weekly_plan)

        return StudyPlan(
            student_id=context.student_id,
            goal=llm_output.goal,
            priority_topics=priority_topics,
            weekly_plan=llm_output.weekly_plan,
            total_weekly_minutes=total_weekly_minutes,
            exam_date=exam_date,
        )
