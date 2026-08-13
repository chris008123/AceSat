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
  `assessments`, `answers`, `learning_sessions`, `study_plans`,
  `progress_records`.
- **ai-data owns**: `topic_mastery`, `ai_memory`, `ai_logs`,
  `concept_embeddings`.
- **Both live in one Postgres database**, under **one Alembic migration
  chain** managed here (`app/database/metadata.py` merges both packages'
  table metadata into one `MetaData`, shared by both `alembic/env.py` and
  the initial migration — verified via a real Alembic CLI run to produce
  all 12 tables).

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

**Phase 4 (Sessions, Progress, Memory) — done.**
- `LearningSession`/`ProgressRecord` models (`app/models/learning_session.py`,
  `app/models/progress.py`).
- `POST /sessions/start` (mission text pulled from the student's current
  weakest topic via `ai_bridge.suggest_mission_topic`), `POST /sessions/complete`
  (`app/services/session_service.py`) — also writes a coarse `ProgressRecord`
  snapshot on completion.
- `GET /progress/dashboard`, `GET /progress/report`
  (`app/services/progress_service.py`) — degrade gracefully (no 4xx) when
  there isn't enough history for a diagnosis yet.
- `POST /memory/update`, `GET /memory/student/{id}`
  (`app/services/memory_bridge.py`) — a thin wrapper around ai-data's
  `MemoryService`/`SQLAlchemyLongTermMemoryRepository`, pointed at this
  backend's own `DATABASE_URL` since both packages share one database.
  `GET /memory/student/{id}` is scoped to the authenticated student's own
  id — there's no admin role wired up yet to allow broader access.

Verified end-to-end via `TestClient`: register → login → create profile →
run a full assessment → get a real, evidence-based diagnosis → get a
persisted study plan → start/complete a learning session → see it reflected
on the dashboard. **32/32 tests pass** (`app/tests/`).

**Not yet built:**
- Background tasks (progress analysis, daily plan generation —
  `Backend_architecture.txt` §11).
- Notifications (`POST /notifications/create` per `Api_design.txt` §12 —
  marked Low priority in the roadmap's own priority matrix).
- Rate limiting, and any validation beyond Pydantic's defaults.
- `learning_sessions` currently only records an "overall" progress
  snapshot per session, not per-subject — `Api_design.txt` §9's session
  completion request doesn't include a subject, so there's nothing to tag
  it with yet; revisit if per-subject dashboard trends become a real need.

## Database — Supabase setup

Supabase is just hosted Postgres, so the existing Alembic chain applies
as-is. Two things had to be added to actually make that true rather than
just documented: a real Postgres driver (`psycopg2-binary` — SQLAlchemy
alone can't connect to Postgres without one, and it was missing from
`pyproject.toml` before now), and an actual initial migration file
(`alembic/versions/0001_initial_schema.py` — `alembic/env.py` always had
the merge logic, but nothing had ever been generated from it).

The migration mechanics (`upgrade`, `current`, `downgrade`) are verified
against a real Alembic CLI run — confirmed it creates all 12 tables
(8 backend-owned + 4 ai-data-owned, including `concept_embeddings`, which
was missing from the metadata merge until this pass) and tears them back
down cleanly. That verification used a local SQLite target, since this
environment doesn't have network access to an actual Supabase host —
the steps below are what to run against the real one.

**Steps:**

1. In your Supabase project dashboard, go to Project Settings → Database
   and copy the connection string (direct connection is simplest for a
   hackathon; use the pooler if you expect many concurrent short-lived
   connections — see `.env.example` for both formats and the SSL note).
2. Set `DATABASE_URL` in your `.env` (or real environment) to that string,
   and set `ENVIRONMENT=production` — `development` mode calls
   `init_db()`/`create_all()` directly on startup, which you don't want
   once Alembic is managing the schema.
3. Run the migration:
   ```bash
   alembic upgrade head
   ```
4. Verify in the Supabase Table Editor that all 12 tables exist:
   `users`, `student_profiles`, `questions`, `assessments`, `answers`,
   `study_plans`, `learning_sessions`, `progress_records`, `topic_mastery`,
   `ai_memory`, `ai_logs`, `concept_embeddings`.
5. Any future schema change: edit the SQLAlchemy models (in either this
   package or `ai-data`), then run
   `alembic revision --autogenerate -m "description"` — it diffs against
   whatever's actually in Supabase, using the same merged metadata via
   `app/database/metadata.py`.

Note: `ai-data`'s own `models/db.py` has its own SQLite-fallback engine
for standalone use — in production, `app/services/ai_bridge.py` and
`memory_bridge.py` both pass this backend's `settings.database_url`
explicitly into ai-data's session calls, so everything actually lands in
the same Supabase database rather than ai-data's local fallback file.

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
