"""Shared agent behavior: try the LLM path, silently fall back to a
deterministic one on any failure.

This is the core design decision of the whole package. AI_Agent_
architecture.txt asks for agents that reason over student data and make
decisions; Demo_scripts.txt §13 ("Backup Demo Plan") and the hackathon
reality of "no guaranteed network/API key at demo time" both push toward
never letting an LLM outage be visible to the student. Every concrete
agent below therefore has two code paths that produce the *same* Pydantic
result type — one backed by a real model call, one backed by the
already-tested, already-deterministic ai-data services (performance
analyzer, recommendation engine, knowledge base). The LLM path is
strictly an enhancement; the product works completely without it.
"""

from __future__ import annotations

from typing import Any

from ai_agents.llm.client import GeminiClient


class BaseAgent:
    name: str = "Agent"

    def __init__(self, llm_client: GeminiClient | None = None) -> None:
        self.llm_client = llm_client

    def _try_llm(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        """Returns the parsed JSON dict on success, `None` on absolutely
        any failure (no client configured, network error, bad JSON,
        content policy refusal, etc.) — callers always have a fallback
        ready and should never need to distinguish *why* the LLM path
        didn't work.
        """
        if self.llm_client is None:
            return None
        try:
            return self.llm_client.generate_json(system_prompt, user_prompt)
        except Exception:  # noqa: BLE001 - see docstring; any failure means "fall back"
            return None
