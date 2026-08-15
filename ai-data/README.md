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

## What's implemented (all 8 phases of the roadmap)

- **Phase 1 — Data Models**: `Student`/`Question`/`Assessment`/`Response`
  Pydantic models, `TopicMastery` (Pydantic + SQLAlchemy table),
  `StudentLearningProfile`, `AIMemory` (short-term/long-term/goal).
- **Phase 2 — Performance Engine**: `calculate_accuracy`,
  `calculate_topic_mastery`, `identify_weak_topics`,
  `identify_strong_topics`, `calculate_performance_trend`,
  `estimate_learning_progress` — all pure functions over the Phase 1 models,
  unit tested with realistic data.
- **Phase 3 — Student Profile**: `generate_student_profile()` composes
  Phase 1/2 output into a `StudentLearningProfile`.
- **Phase 4 — AI Context Builder**: `build_student_context()` produces the
  `StudentContext` payload agent prompts consume.
- **Phase 5 — Memory**: `InMemoryShortTermStore` (session-scoped, no DB) +
  `SQLAlchemyLongTermMemoryRepository` (concrete implementation against
  this module's own `ai_memory` table, self-contained via `models/db.py` —
  works today against a local SQLite fallback, or the shared Postgres
  instance once `AI_DATA_DATABASE_URL` is set). `MemoryService` combines
  both into the single interface the Context Builder/agents should use.
- **Phase 6 — Knowledge Base**: `Concept`/`ConceptExample` models, 3 sample
  concepts (Reading Inference, Linear Equations, Grammar), and
  `get_concepts_for_topic()` — looks up directly by the same topic strings
  the performance engine produces, so a weak topic resolves to teaching
  material with no translation layer.
- **Phase 7 — Retrieval** (opt-in, isolated in `retrieval/`):
  `EmbeddingProvider` protocol with a dependency-free
  `DeterministicEmbeddingProvider` (tests/local dev) and a
  `GoogleEmbeddingProvider` stub for production; `VectorSearchService`
  does cosine-similarity search over concept text, stored as a portable
  JSON array — no `pgvector` Postgres extension required. Nothing outside
  `retrieval/` depends on it, so it can be deleted if the MVP doesn't need
  semantic search.
- **Phase 8 — Evaluation**: all 5 scenarios from the hackathon prompt
  (weak algebra, weak reading inference, improving rapidly, inconsistent
  performance, repeated mistake) as data files, each verified against the
  real analyzer/recommendation code before being committed. `evaluator.py`
  synthesizes responses from each scenario and checks
  `identify_weak_topics()` / `generate_topic_recommendations()` produce
  the expected outcome — one parametrized test per scenario.

All 31 tests pass, including the memory service and vector search against
a real (SQLite) database, and the SQLAlchemy models verified to compile
correct DDL against the Postgres dialect specifically (native
`UUID`/`JSONB`, not just SQLite-compatible types).

## Definition of Done — status

- [x] Student learning profiles can be generated.
- [x] Assessment results can be analyzed.
- [x] Weak and strong topics can be identified.
- [x] Topic mastery can be calculated.
- [x] Performance trends can be calculated.
- [x] Relevant student context can be generated.
- [x] AI memory can retrieve relevant history.
- [x] Recommendations have explainable reasons.
- [x] The AI Agent Engineer can consume structured student context — the
      `ai-agents` package now builds `StudentContext` for every agent
      prompt via `build_context()`, and persists an `AILogRecord` per
      decision so the "explainable reasons" above have an actual audit
      trail, not just a well-worded string. See `ai-agents/README.md`.
- [x] The Backend Engineer can integrate the data layer — `app/services/
      ai_bridge.py` (backend) and `ai_agents/context.py` both do this
      today, against the boundary/session decisions in the section above.
- [x] Automated tests cover the critical logic.

## Dependencies on other roles

- **Backend Engineer**: needs to confirm the boundary above, expose a
  repository/query layer (or direct DB session) so `services/` can read
  `assessments`/`answers`/`questions`/`student_profiles` without this module
  owning those tables. Migration for `topic_mastery`, `ai_memory`, `ai_logs`
  is no longer blocking — this module runs its own local database via
  `models/db.py` (`AI_DATA_DATABASE_URL` env var, defaults to a local
  SQLite file) until the shared Postgres instance is ready; point that env
  var at it whenever it exists, or swap the `Session` at that point.
- **AI Agent Engineer**: now implemented in `ai-agents/` — consumes
  `StudentContext` (Phase 4) as the input to the Diagnostic/Planning/
  Coaching agent prompts, and `Recommendation` for the "reason" field the
  prompt strategy doc requires on every recommendation.
  `MemoryService.recall()` remains available for an agent to pull scoped
  historical context mid-prompt but isn't wired into any agent yet — a
  reasonable next step, not attempted here to avoid pulling long-term
  memory into every `/ai/*` call before there's a concrete need for it.
