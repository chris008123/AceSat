# AceMentor AI — `ai-agents` (AI Agent Engineer module)

This package implements the **AI Agent Engineer** role: Diagnostic, Planning,
Coaching, and Analytics agents, plus (in a later phase) the orchestrator that
connects them. It consumes `ai-data`'s `StudentContext` / `MemoryService` /
knowledge base as inputs (see `ai-data/README.md` for that boundary) and
produces the structured outputs defined in `ai_agents.schemas`.

## LLM provider

Agent reasoning will be powered by **Groq** (fast Llama/OpenAI-OSS-family
inference), not Gemini as the original planning docs assumed. This only
affects Phase 2+ (the actual model-calling code) — Phase 1's schemas are
provider-agnostic and don't change either way. `GROQ_API_KEY` will be the
env var added when that phase lands, replacing the unused `AI_API_KEY`
placeholder currently in the backend's settings.

## Status

### Phase 1 — Agent Contracts (done)

Pydantic schemas for all four agent outputs, matching the shapes defined in
`AI_Agent_architecture.txt` §4 and the hackathon master prompt's Phase 1:

- `DiagnosticResult` — weak/strong/priority topics, evidence-based
  `reasoning`, `confidence`, optional `recommended_intervention` +
  `intervention_urgency`.
- `StudyPlan` (+ `StudyPlanItem`) — goal, priority topics, a day-by-day plan
  where **every item requires a `reason`** (Prompt_strategy.txt §6: "Do not
  create generic schedules").
- `CoachingResponse` — `response_type` (explanation / hint / guiding
  question / feedback / encouragement), `message`, optional
  `follow_up_question`, and an explicit `gives_direct_answer` flag so
  "avoid giving immediate answers unless appropriate" (Prompt_strategy.txt
  §7) is an auditable field, not implicit in free text.
- `AnalyticsResult` (+ `TopicTrend`) — `overall_status` from the hackathon
  prompt's fixed vocabulary (improving / declining / stable / needs
  intervention / ready for harder questions / needs reinforcement),
  per-topic trends, `summary`, `reasoning`, `confidence`.

16 tests in `ai_agents/tests/test_schemas.py` cover valid construction,
required-field enforcement, and numeric bounds (confidence 0-1, duration
1-240 minutes) for all four schemas.

### Phase 2 — Diagnostic Agent (done)

`ai_agents.agents.DiagnosticAgent` — consumes `ai_data`'s `StudentContext`
and produces a validated `DiagnosticResult`, backed by a Groq chat
completion call (`llama-3.3-70b-versatile` by default, override via
`GROQ_MODEL` env var or the `model=` constructor arg).

- Prompt lives in `ai_agents/prompts/diagnostic.py`, structured per
  Prompt_strategy.txt §3 (Role / Goal / Decision Rules / Output Format),
  with student context injected per-request rather than baked into the
  system prompt.
- The LLM's raw JSON reply is parsed into an internal `_DiagnosticLLMOutput`
  model first (a narrower schema than `DiagnosticResult` — the model never
  supplies `student_id`, that's filled in from the real context, so a
  hallucinated ID can't slip through).
- `priority_topics` is filtered server-side to only topics also present in
  `weak_topics`, regardless of what the model returned — outputs aren't
  trusted blindly.
- Bad JSON or a schema mismatch raises `DiagnosticAgentError` with the raw
  response attached, rather than silently returning something wrong.

**LLM calls are injectable** (`complete_fn` constructor arg) specifically so
tests never need a real `GROQ_API_KEY` or network access — they pass a fake
function returning canned JSON. 6 tests in
`ai_agents/tests/test_diagnostic_agent.py` cover: valid diagnosis, the
priority_topics filtering behavior, sparse-data/low-confidence handling,
invalid JSON, schema mismatches, and the missing-API-key error path.

**To actually call Groq**, set `GROQ_API_KEY` in your environment (or
`backend/.env`) and construct `DiagnosticAgent()` with no `complete_fn` —
this hasn't been exercised against the real API in development (no network
access to `api.groq.com` in this environment), so test it against a real
key before relying on it.

### Not yet built

Phase 3 (Planning Agent), Phase 4 (Coaching Agent), Phase 5 (Analytics
Agent), Phase 6 (tool layer), Phase 7 (orchestrator), Phase 8 (adaptive
loop), Phase 9 (backend integration — swapping
`backend/app/services/ai_bridge.py`'s placeholder logic for real agent
calls), Phase 10 (evaluation).

## Structure

```
ai_agents/
├── schemas/           # Phase 1 — agent output contracts
├── prompts/            # Phase 2+ — dedicated prompt files, one per agent
├── agents/              # Phase 2+ — agent implementations
│   └── diagnostic_agent.py
└── tests/
```

## Running tests

```bash
cd ai-agents
pip install -e ".[dev]"
pip install -e ../ai-data   # DiagnosticAgent's StudentContext type comes from here
python -m pytest -v
```

## Environment variables (Phase 2+)

```env
GROQ_API_KEY=your-key-here
GROQ_MODEL=llama-3.3-70b-versatile   # optional, this is the default
```
