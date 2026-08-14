"""Diagnostic Agent — AI_Agent_architecture.txt §4.1 / Development_roadmap.txt
Phase 3 Priority Agent 1.

Consumes `ai_data`'s `StudentContext` and produces a `DiagnosticResult`
(Phase 1 schema), backed by a Groq chat completion call.

The actual LLM call is injected as `complete_fn` rather than hardcoded to
the `groq` SDK inline, so:
  - Tests never need a real GROQ_API_KEY or network access — they pass a
    fake `complete_fn` returning canned JSON.
  - Swapping providers later (or adding retries/streaming) doesn't change
    this class's public interface.

`_default_groq_complete` is the real implementation used when no
`complete_fn` is supplied, i.e. actual production/local usage.
"""

from __future__ import annotations

import json
import os
from typing import Callable

from pydantic import BaseModel, Field, ValidationError

from ai_data.services.context_builder import StudentContext

from ai_agents.prompts.diagnostic import DIAGNOSTIC_SYSTEM_PROMPT, build_diagnostic_user_prompt
from ai_agents.schemas import DiagnosticResult
from ai_agents.schemas.enums import InterventionUrgency

# Sensible default — fast Groq-hosted model, good enough for structured
# JSON extraction tasks like this one. Override via the GROQ_MODEL env var
# or the `model=` constructor arg without code changes.
DEFAULT_GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# The type `complete_fn` must satisfy: given the chat messages, return the
# raw text content of the model's reply.
CompleteFn = Callable[[list[dict]], str]


class DiagnosticAgentError(Exception):
    """Raised when the LLM response can't be turned into a valid
    DiagnosticResult — bad JSON, or JSON that doesn't match the expected
    shape. Deliberately not swallowed/retried silently here (Phase 2 scope
    is correctness, not resilience — retry policy is a Phase 6+ concern)."""


class _DiagnosticLLMOutput(BaseModel):
    """What the LLM itself is responsible for producing — deliberately
    narrower than `DiagnosticResult`: `student_id`, `diagnostic_id`, and
    `generated_at` are filled in by this module, never by the model, so a
    hallucinated student_id can't slip through.
    """

    weak_topics: list[str] = Field(default_factory=list)
    strong_topics: list[str] = Field(default_factory=list)
    priority_topics: list[str] = Field(default_factory=list)
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_intervention: str | None = None
    intervention_urgency: InterventionUrgency = InterventionUrgency.NONE


def _default_groq_complete(messages: list[dict], *, model: str) -> str:
    """Real Groq-backed implementation of `CompleteFn`. Imports `groq`
    lazily so importing this module (or running tests, which never take
    this path) doesn't require the package or an API key to be present.
    """
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise DiagnosticAgentError(
            "GROQ_API_KEY is not set. Set it in the environment (or backend/.env) "
            "before calling DiagnosticAgent without an explicit complete_fn."
        )

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return response.choices[0].message.content


class DiagnosticAgent:
    """Diagnostic Agent. Usage:

        agent = DiagnosticAgent()  # uses real Groq call, needs GROQ_API_KEY
        result = agent.diagnose(student_context)

    For tests, inject a fake completion function:

        agent = DiagnosticAgent(complete_fn=lambda messages: '{"weak_topics": [...], ...}')
    """

    def __init__(self, complete_fn: CompleteFn | None = None, model: str = DEFAULT_GROQ_MODEL):
        self.model = model
        self._complete_fn = complete_fn or (
            lambda messages: _default_groq_complete(messages, model=self.model)
        )

    def diagnose(self, context: StudentContext) -> DiagnosticResult:
        messages = [
            {"role": "system", "content": DIAGNOSTIC_SYSTEM_PROMPT},
            {"role": "user", "content": build_diagnostic_user_prompt(context)},
        ]

        raw = self._complete_fn(messages)

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise DiagnosticAgentError(
                f"Diagnostic Agent response was not valid JSON: {exc}\nRaw response: {raw!r}"
            ) from exc

        try:
            llm_output = _DiagnosticLLMOutput.model_validate(payload)
        except ValidationError as exc:
            raise DiagnosticAgentError(
                f"Diagnostic Agent response did not match the expected schema: {exc}"
            ) from exc

        # priority_topics must be a subset of weak_topics — the prompt asks
        # for this but doesn't guarantee it; enforce it here rather than
        # trusting the model, per the "validate all agent outputs" rule.
        weak_set = set(llm_output.weak_topics)
        priority_topics = [t for t in llm_output.priority_topics if t in weak_set]

        return DiagnosticResult(
            student_id=context.student_id,
            weak_topics=llm_output.weak_topics,
            strong_topics=llm_output.strong_topics,
            priority_topics=priority_topics,
            reasoning=llm_output.reasoning,
            confidence=llm_output.confidence,
            recommended_intervention=llm_output.recommended_intervention,
            intervention_urgency=llm_output.intervention_urgency,
        )
