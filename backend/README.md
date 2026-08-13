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

**Phase 2 (Core Backend) — done.**
- Auth: `POST /auth/register`, `POST /auth/login` — JWT + bcrypt password
  hashing (`app/services/security.py`, `app/services/auth_service.py`).
  Uses `bcrypt` directly rather than through `passlib`, which has a known
  incompatibility with `bcrypt>=4.1`.
- Student profile: `POST`/`GET`/`PUT /students/profile`
  (`app/services/student_service.py`).
- Assessment engine: `Assessment`/`Answer` models
  (`app/models/assessment.py`), `POST /assessment/start` (now picks a
  **subject-balanced** spread of questions rather than the first N rows —
  an uneven question bank could otherwise starve entire subjects out of
  the diagnostic entirely), `POST /assessment/answer`,
  `POST /assessment/complete` with real scoring
  (`app/services/assessment_service.py`).
- Standard `{"success": false, "error": {...}}` error format as an actual
  FastAPI exception handler (`app/utils/errors.py`), not just documented.
- `get_current_user` bearer-token dependency (`app/api/dependencies.py`)
  used by every protected route.

**Phase 3 (AI Integration, via the ai-data bridge) — done.**
- `app/services/ai_bridge.py` translates this backend's `Answer`/
  `Question` rows into `ai-data`'s `QuestionResponse` models and calls
  straight into `ai-data`'s `identify_weak_topics`,
  `identify_strong_topics`, `generate_topic_recommendations`, and
  `ai_data.knowledge` — the stand-in described above.
- `POST /ai/diagnose`, `POST /ai/study-plan` (persists to the new
  `StudyPlan`/`study_plans` table), `POST /ai/coach` (a deterministic
  stand-in — pulls the student's weakest topic's stored explanation, not
  an LLM-backed coach).

Verified end-to-end via `TestClient`: register → login → create profile →
run a full assessment → get a real, evidence-based diagnosis → get a
persisted study plan. **20/20 tests pass** (`app/tests/`), covering auth,
student profile, the assessment flow (including the subject-balancing
fix), and the AI bridge — respecting ai-data's evidence thresholds (a
diagnosis only fires once there's actually enough data).

**Not yet built:**
- `learning_sessions`, `progress_records` tables and the
  `GET /progress/dashboard`, `GET /progress/report` endpoints
  (`Api_design.txt` §10).
- Memory API endpoints (`POST /memory/update`, `GET /memory/student/{id}`
  per `Api_design.txt` §11) — should be thin wrappers around ai-data's
  `MemoryService`, not new logic.
- Background tasks (progress analysis, daily plan generation —
  `Backend_architecture.txt` §11).
- An actual `alembic revision --autogenerate` generated and applied
  against a real Postgres instance — the merge logic in `alembic/env.py`
  is verified to produce the right merged metadata, but no migration has
  been run against real Postgres yet (only SQLite, for local dev/tests).
- Rate limiting, and any validation beyond Pydantic's defaults.

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
