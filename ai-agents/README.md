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

No agent logic, prompts, or LLM calls exist yet — that's Phase 2 onward.

### Not yet built

Phase 2 (Diagnostic Agent + Groq wiring), Phase 3 (Planning Agent), Phase 4
(Coaching Agent), Phase 5 (Analytics Agent), Phase 6 (tool layer), Phase 7
(orchestrator), Phase 8 (adaptive loop), Phase 9 (backend integration —
swapping `backend/app/services/ai_bridge.py`'s placeholder logic for real
agent calls), Phase 10 (evaluation).

## Structure

```
ai_agents/
├── schemas/          # Phase 1 — agent output contracts (this phase)
├── tests/
├── agents/            # Phase 2+ — not yet built
├── prompts/           # Phase 2+ — not yet built
└── orchestrator/       # Phase 7 — not yet built
```

## Running tests

```bash
cd ai-agents
pip install -e ".[dev]"
python -m pytest -v
```
