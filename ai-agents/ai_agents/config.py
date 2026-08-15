"""Agent configuration — reads the same `AI_API_KEY` env var
Deployment_architecture.txt §5 already documents for the backend, plus
`GROQ_API_KEY` as the name Groq's own SDK looks for by default (so this
also works if someone sets up credentials the "normal" Groq way instead
of AceMentor's own var name).

No API key configured is a normal, supported state — every agent has a
deterministic fallback (see `agents/base.py`), so `enabled=False` here
just means "skip the LLM call, don't even try," not "the feature is
broken." That's what keeps local dev, CI, and the hackathon demo's backup
plan (Demo_scripts.txt §13) working without any credentials at all.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Groq-hosted Llama 3.3 70B — fast inference, strong JSON-mode support,
# generous free tier. Swapped in from Gemini 2.5 Flash
# (Technology_Stack.txt's original AI stack pick) for lower latency and
# no-cost development; see ai-agents/README.md's "Why Groq" note.
DEFAULT_MODEL_NAME = "llama-3.3-70b-versatile"


@dataclass(frozen=True)
class AgentConfig:
    api_key: str | None = None
    model_name: str = DEFAULT_MODEL_NAME
    enabled: bool = False


def load_config() -> AgentConfig:
    api_key = os.environ.get("AI_API_KEY") or os.environ.get("GROQ_API_KEY") or None
    model_name = os.environ.get("AI_MODEL_NAME", DEFAULT_MODEL_NAME)
    return AgentConfig(api_key=api_key, model_name=model_name, enabled=api_key is not None)
