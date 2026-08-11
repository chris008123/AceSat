# AceMentor AI — `ai-data` (AI / Data Engineering module)

This package implements the **AI/Data Engineer** role for AceMentor AI: the data
and intelligence foundation the Diagnostic/Planning/Coaching agents and the
FastAPI backend consume. It does **not** contain agent orchestration
(AI Agent Engineer), REST endpoints/auth (Backend Engineer), or UI (Frontend).

## Status of the repo when this module was started

At the time this module was scaffolded, the AceMentor AI repository contained
**no application code** — only planning documents (`00_Project_Overview`,
`06_System_Architecture`, `10_Database_Design`, etc.), all marked
`Status: Planning Phase`. Nothing listed in section "Definition of Done" was
implemented yet. This module is therefore a from-scratch Phase 1–2
implementation, built to the shapes defined in `10_Database_Design.md` and
`Technology_Stack.md`.

## A boundary note worth flagging to the team

`06_System_Architecture` / `13_Backend_Architecture` put a `models/` folder
(`user.py`, `student.py`, `question.py`, `progress.py`) under the **backend**,
and describe the backend's Data Layer as "Uses SQLAlchemy Models". But
`10_Database_Design` separately defines `ai_memory`, `ai_logs`,
`study_plans`, and `progress_records` — tables that conceptually belong to
this AI/Data role per the hackathon prompt's ownership section ("Owns: Data,
Learning Profiles, Memory, Analysis, Context, Evaluation").

To avoid duplicate/conflicting ORM models for the same tables, this module
draws the line as follows — **please confirm with the Backend Engineer**:

- **Backend-owned tables** (read via a repository interface, not redefined
  here): `users`, `student_profiles`, `questions`, `assessments`, `answers`,
  `learning_sessions`.
- **AI/Data-owned tables** (defined in `ai_data/models/`):
  `topic_mastery` (new — not yet in `10_Database_Design`, proposed here
  because the design doc has no per-topic mastery/trend table, only the
  coarser `progress_records`), `ai_memory`, `ai_logs`.
- Everything AI/Data produces (profiles, mastery, context, recommendations)
  is exposed as **Pydantic models**, independent of whichever ORM the
  backend settles on for its own tables — so the AI Agent Engineer and
  Backend Engineer can consume clean interfaces regardless.

## Structure

```
ai_data/
├── models/          # Pydantic domain models + SQLAlchemy models for AI-owned tables
├── services/         # performance analysis, mastery engine, profile/context/memory/recommendations
├── knowledge/        # SAT content structure (Phase 6, not yet built)
├── retrieval/         # pgvector embeddings/search (Phase 7, not yet built)
├── evaluation/        # personalization test scenarios (Phase 8, started)
└── tests/
```

## What's implemented in this pass (Phases 1–2 of the roadmap)

- **Phase 1 — Data Models**: `Student`/`Question`/`Assessment`/`Response`
  Pydantic models, `TopicMastery` (Pydantic + SQLAlchemy table),
  `StudentLearningProfile`, `AIMemory` (short-term/long-term/goal).
- **Phase 2 — Performance Engine**: `calculate_accuracy`,
  `calculate_topic_mastery`, `identify_weak_topics`,
  `identify_strong_topics`, `calculate_performance_trend`,
  `estimate_learning_progress` — all pure functions over the Phase 1 models,
  unit tested with realistic data.

## Not yet built (next stages, in roadmap order)

- Phase 3 — Student profile generator service (`student_profile.py` stub only)
- Phase 4 — AI Context Builder (produces the `student_context` dict the AI
  Agent Engineer's prompts consume)
- Phase 5 — Short-term/long-term Memory service + retrieval
- Phase 6 — Knowledge base structure for SAT content
- Phase 7 — pgvector retrieval (optional, MVP can ship without it)
- Phase 8 — Full evaluation dataset (one scenario stubbed as a template)

## Dependencies on other roles

- **Backend Engineer**: needs to confirm the boundary above, expose a
  repository/query layer (or direct DB session) so `services/` can read
  `assessments`/`answers`/`questions`/`student_profiles` without this module
  owning those tables; needs to run the migration for `topic_mastery`,
  `ai_memory`, `ai_logs`.
- **AI Agent Engineer**: consumes `StudentContext` (Phase 4, pending) as the
  input to Diagnostic/Planning/Coaching agent prompts, and
  `RecommendationContext` (pending) for the "reason" field the prompt
  strategy doc requires on every recommendation.
