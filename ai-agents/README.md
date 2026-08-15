# AceMentor AI — `ai-agents` (AI Agent Engineering module)

This package implements the **AI Agent Engineer** role for AceMentor AI
(`Team_assignments.txt` §6, `Project_modules.txt` §6, `Agents.txt`): the
actual multi-agent orchestration that turns `ai-data`'s structured student
context into decisions — diagnoses, study plans, coaching responses,
progress narratives, motivation, and reflection prompts.

## Why this package exists

`ai-data/README.md` and `backend/README.md` both flag the same gap:

> "Agent orchestration — a placeholder, not the real thing... Until that
> role is staffed, the `ai` route calls directly into `ai-data`'s services
> ... as a stand-in, clearly marked as simplified."

This package is that role, staffed. `backend/app/services/ai_bridge.py`
now delegates to `ai_agents.orchestrator.AgentOrchestrator` instead of
calling `ai-data` directly — the API contract in `Api_design.txt` doesn't
change, per that same README's promise ("swapping in real agent
orchestration later shouldn't require frontend changes").

## Relationship to `ai-data` and `backend`

```
backend (FastAPI, owns DB access)
   │  fetches Student + QuestionResponse rows from Postgres
   ▼
ai-agents (this package, DB-agnostic except decision logging)
   │  calls ai-data's Phase 1-4 services to build StudentContext
   │  runs the six agents (LLM-first, deterministic-fallback)
   ▼
ai-data (StudentContext, Recommendation, knowledge base, performance analysis)
```

`ai-agents` depends on `ai-data`; neither `ai-data` nor `backend` depend on
`ai-agents` at import time (`backend` imports it lazily inside
`ai_bridge.py`, matching how it already imports `ai-data`).

## The six agents (`Agents.txt`)

| Agent | File | Wired into a route? |
|---|---|---|
| Diagnostic | `agents/diagnostic_agent.py` | `POST /ai/diagnose` |
| Planning | `agents/planning_agent.py` | `POST /ai/study-plan`, and `sessions.mission` via `suggest_mission_topic` |
| Coaching | `agents/coaching_agent.py` | `POST /ai/coach` |
| Analytics | `agents/analytics_agent.py` | available to `progress_service.py`; no dedicated route in `Api_design.txt` |
| Motivation | `agents/motivation_agent.py` | not yet — no `Api_design.txt` route exists for it |
| Reflection | `agents/reflection_agent.py` | not yet — same |

The first three are what `Api_design.txt` §8 actually exposes, so those
are what `ai_bridge.py` calls today. Analytics/Motivation/Reflection are
fully implemented and tested but sit unconsumed until a route or the
frontend needs them — same "interfaces ready, consumption pending" state
`ai-data/README.md` describes for its own outputs.

## Design decision: LLM-first, deterministic-fallback, always

Every agent's `run()` method:

1. Builds a prompt from `prompts/<agent>.py` (Prompt_strategy.txt's
   `System Identity + Role + Context + Task + Rules + Output Format`
   structure) and a `StudentContext` built via `context.py`.
2. Tries a real Gemini call (`llm/client.py`) if `AI_API_KEY` /
   `GOOGLE_API_KEY` is configured — Technology_Stack.txt's stack pick,
   Gemini 2.5 Flash, structured JSON output.
3. On **any** failure — no key configured, package not installed, network
   error, malformed JSON, schema validation failure — silently falls back
   to a deterministic path built on `ai-data`'s already-tested analysis
   functions (`performance_analyzer`, `recommendation_context`,
   `knowledge.loader`).

This isn't a shortcut; it's the actual requirement. Demo_scripts.txt §13
("Backup Demo Plan") and the reality of hackathon judging (no guaranteed
network/API key at demo time) mean an LLM outage must never be visible to
the student — every result is a real, structured, evidence-based answer
either way, just with a `source: "llm" | "deterministic"` field marking
which path produced it (useful for debugging, not part of any
`Api_design.txt` response contract).

**Practical consequence for anyone running this without an API key**: the
product still works completely. Set `AI_API_KEY` (or `GOOGLE_API_KEY`) and
install the `llm` extra (`pip install -e .[llm]`) to turn on real model
calls; everything functions identically, just with LLM-generated
reasoning instead of rule-based reasoning, without any code changes.

## Why not PydanticAI, despite `Technology_Stack.txt` naming it

`Technology_Stack.txt`'s AI stack lists `PydanticAI` as the intended
multi-agent framework. This package doesn't depend on it — pulling in a
framework that can't be installed/verified in every environment would
make the whole package unimportable if it's missing, worse than the LLM
feature it would add. `llm/client.py`'s `generate_json(system_prompt,
user_prompt) -> dict` is deliberately the same shape `Agent.run` would
have; swapping in PydanticAI later is a one-file change in `llm/client.py`
and the `_try_llm` call sites, not a rewrite of the six agents or the
orchestrator.

## Decision logging (`ai_logs`)

Every orchestrator call (`diagnose`, `plan`, `coach`, `analyze`) writes an
`AILogRecord` — agent name, input context, output decision — to `ai-data`'s
`ai_logs` table when a `database_url` is supplied, mirroring
`Backend_architecture.txt` §14's "Logging System" (records API requests,
errors, **AI decisions**, agent performance) and closing the
`ai-data/README.md` Definition-of-Done item "Recommendations have
explainable reasons" with an actual persisted audit trail, not just a
well-worded `reason` string. Logging failures are swallowed — this is
diagnostic, never load-bearing; a broken/missing `ai_logs` table must not
take down a diagnosis, plan, or coaching response.

## Structure

```
ai_agents/
├── config.py          # AI_API_KEY / GOOGLE_API_KEY from env
├── context.py          # builds StudentContext from Student + QuestionResponse
├── errors.py           # NoTeachingMaterialError
├── logging.py          # writes AILogRecord to ai-data's ai_logs table
├── orchestrator.py      # AgentOrchestrator — the integration point
├── schemas.py           # structured outputs every agent returns
├── llm/
│   └── client.py        # Gemini wrapper; None/LLMUnavailable on any failure
├── prompts/              # one module per agent, Prompt_strategy.txt-shaped
│   ├── base.py
│   ├── diagnostic.py
│   ├── planning.py
│   ├── coaching.py
│   ├── analytics.py
│   └── motivation.py
└── agents/                # one class per agent
    ├── base.py             # shared _try_llm / fallback pattern
    ├── diagnostic_agent.py
    ├── planning_agent.py
    ├── coaching_agent.py
    ├── analytics_agent.py
    ├── motivation_agent.py
    └── reflection_agent.py
```

## Running locally

```bash
pip install -e ../ai-data
pip install -e .[dev]        # add [llm] too if you have an AI_API_KEY to test against
pytest tests -q
```

Tests run entirely on the deterministic fallback path (no `AI_API_KEY` set
in the test environment), so they're fast, free, and don't need network
access — the same property `backend/app/tests` relies on, since
`backend`'s own tests never set an API key either and therefore always
exercise `ai-agents`' deterministic path today.

## Backend integration

`backend/app/services/ai_bridge.py`'s three public functions
(`diagnose`, `generate_study_plan`, `coach`) and
`suggest_mission_topic` keep their original signatures — they still take
a SQLAlchemy `Session` and build `ai_data.models.assessment.
QuestionResponse` rows from the backend's own `Answer`/`Question` tables
(that boundary-crossing code doesn't move). What changed is what happens
next: instead of calling `ai_data.services.*` directly, they build an
`AgentOrchestrator` (`AgentOrchestrator.from_env(database_url=...)`) and
call its `diagnose`/`plan`/`coach` methods, then translate the
`ai_agents.schemas.*` result into the existing `app/schemas/ai.py`
response shapes. See that file for the exact translation.

## Dependencies on other roles

- **AI/Data Engineer (`ai-data`)**: this package is a pure consumer of
  `StudentContext`, `Recommendation`, the knowledge base, and the
  performance-analysis functions — no changes requested there.
- **Backend Engineer**: `ai_bridge.py` is the only integration point;
  route handlers and `app/schemas/ai.py` are unchanged.
- **Frontend**: no changes required — `Api_design.txt`'s `/ai/*` response
  shapes are identical to before.
