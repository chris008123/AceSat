# AceMentor AI — `backend`

FastAPI backend for AceMentor AI, per `Backend_architecture.txt`,
`Database_design.txt`, and `Api_design.txt`.

## Relationship to `ai-data`

This package **depends on** `ai-data` (installed as a local editable
dependency — see `pyproject.toml`); `ai-data` never imports from here.
Both packages assume they sit as sibling directories in one monorepo
(matches `Deployment_architecture.txt` §7's repo layout:
`backend/`, `ai-agents/`, etc. as top-level folders).

**Table ownership** (see `ai-data/README.md` for the full boundary note):
- **This backend owns**: `users`, `student_profiles`, `questions`,
  `assessments`, `answers`, `learning_sessions`, `study_plans`.
- **ai-data owns**: `topic_mastery`, `ai_memory`, `ai_logs`,
  `concept_embeddings`.
- **Both live in one Postgres database**, under **one Alembic migration
  chain** managed here (`alembic/env.py` merges both packages' table
  metadata — verified to include all 6 core tables in one `MetaData`).

## Agent orchestration — a placeholder, not the real thing

`Team_assignments.txt`'s 6-role split makes agent orchestration the **AI
Agent Engineer's** job, not Backend's — even though
`Backend_architecture.txt`'s folder structure sketches an `agents/`
folder here, and `Api_design.txt` has `/ai/diagnose`, `/ai/study-plan`,
`/ai/coach` endpoints. Until that role is staffed, the `ai` route (Phase
2+) will call directly into `ai-data`'s services
(`generate_student_profile`, `identify_weak_topics`,
`generate_topic_recommendations`) as a stand-in, clearly marked as
simplified. The API contract in `Api_design.txt` stays the same either
way, so swapping in real agent orchestration later shouldn't require
frontend changes.

## Status

**Phase 1 (Foundation) — done.**
- FastAPI app (`app/main.py`) with a `/health` endpoint.
- Settings from env vars (`app/config/settings.py`) — see `.env.example`.
- DB connection/session (`app/database/connection.py`).
- Phase 1's three tables per `Development_roadmap.txt`: `User`,
  `StudentProfile`, `Question` (`app/models/`).
- Alembic scaffolding wired to merge this backend's + ai-data's metadata.
- 4/4 tests passing (health check + model creation/relationships).

**Not yet built** (`Development_roadmap.txt` Phase 2 — Core Backend):
- Auth (registration, login, JWT) — `app/api/routes/auth.py`,
  `app/services/auth_service.py`.
- Student profile CRUD — `app/api/routes/students.py`.
- Assessment engine (`assessments`/`answers` tables, question retrieval,
  scoring) — `app/api/routes/assessment.py`.
- `study_plans`, `learning_sessions` tables.
- The `ai` route bridging into `ai-data` (see above).

## Running locally

```bash
pip install -e ../ai-data
pip install -e .[dev]
cp .env.example .env   # defaults to a local SQLite file if DATABASE_URL unset
uvicorn app.main:app --reload
```

## Testing

```bash
pytest app/tests -q
```
