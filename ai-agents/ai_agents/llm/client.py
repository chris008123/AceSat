"""Thin wrapper around Google Gemini (Technology_Stack.txt: "Google Gemini
2.5 Flash" + "Structured JSON outputs"). Deliberately NOT built on
PydanticAI despite Technology_Stack.txt naming it as the intended
multi-agent framework — pulling in a framework dependency that can't be
installed/verified in this environment would make the whole package
unimportable if it's missing, which is worse than the feature it would
add. The interface below (`generate_json`) is exactly what PydanticAI's
`Agent.run` would be swapped in for later: agents call one method and get
a `dict`, so migrating is a one-file change, not a rewrite.

Every failure mode — package not installed, no key, network error,
malformed response — collapses to `LLMUnavailable`. Callers (see
`agents/base.py`) always treat that as "use the deterministic fallback,"
never as a reason to error out to the student.
"""

from __future__ import annotations

import json
from typing import Any

try:  # pragma: no cover - exercised only when the package is installed
    import google.generativeai as genai
except ImportError:  # pragma: no cover - the expected path in this environment
    genai = None

from ai_agents.config import AgentConfig, load_config


class LLMUnavailable(RuntimeError):
    """Raised for every LLM-path failure. Never propagates past
    `agents/base.py`'s `_try_llm` — it's an internal control-flow signal,
    not something a route handler should ever see.
    """


class GeminiClient:
    def __init__(self, api_key: str | None, model_name: str) -> None:
        if genai is None:
            raise LLMUnavailable("google-generativeai is not installed")
        if not api_key:
            raise LLMUnavailable("no AI_API_KEY/GOOGLE_API_KEY configured")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Sends the two-part prompt (role/system instructions + task
        payload — matches the `System Identity + Role Definition + ...`
        structure in Prompt_strategy.txt §3) and parses the response as
        JSON. Any exception anywhere in this path — API error, timeout,
        non-JSON response — becomes `LLMUnavailable` so callers only ever
        need to catch one thing.
        """
        try:
            response = self._model.generate_content(
                [system_prompt, user_prompt],
                generation_config={"response_mime_type": "application/json"},
            )
            return json.loads(response.text)
        except Exception as exc:  # noqa: BLE001 - intentionally broad, see docstring
            raise LLMUnavailable(str(exc)) from exc


def build_llm_client(config: AgentConfig | None = None) -> GeminiClient | None:
    """Returns `None` (not a raised exception) when the LLM path isn't
    available for any reason — the one place that decision gets made, so
    every agent and the orchestrator can just check "do I have a client"
    without knowing why one might be missing.
    """
    config = config or load_config()
    if not config.enabled:
        return None
    try:
        return GeminiClient(api_key=config.api_key, model_name=config.model_name)
    except LLMUnavailable:
        return None
