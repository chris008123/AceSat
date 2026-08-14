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
   → Connection pooling → Session mode, and copy that connection string
   — **use the pooler, not the direct connection**. Supabase's direct
   hostname (`db.[ref].supabase.co`) is IPv6-only unless you've paid for
   the IPv4 add-on, and fails to resolve entirely
   (`could not translate host name`) on networks that don't route IPv6
   properly. The pooler hostname is IPv4-compatible and sidesteps this.
   See `.env.example` for the exact format — note the username changes to
   `postgres.[PROJECT-REF]`, not just `postgres`.
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

**On Windows**, run these as separate commands (not pasted as one block —
PowerShell can silently swallow later lines into a `>>` continuation if a
multi-line paste looks unterminated), and if `uvicorn` isn't found after
installing, PATH may not include your Python user-site `Scripts` folder —
use `python -m uvicorn app.main:app --reload` instead, which always works
regardless of PATH.

## Testing

```bash
pytest app/tests -q
```

## Troubleshooting

- **`pip install -e .` fails with "Multiple top-level packages discovered
  in a flat-layout"** — fixed as of this pass (`pyproject.toml` now has
  `[tool.setuptools.packages.find]` scoping the install to `app/` only,
  since `alembic/` sits alongside it and confused auto-discovery). If
  you still hit this, you're on an older copy of `pyproject.toml`.
- **`ModuleNotFoundError: No module named 'psycopg2'`** — means
  `psycopg2-binary` didn't get installed, usually because `pip install -e .`
  failed on the error above before it got that far. Fix the packaging
  error first, then reinstall.
- **`pip install -e .` fails on the `ai-data` line specifically** (a
  "non-local file URIs are not supported" error) — fixed as of this pass;
  `ai-data` is no longer declared as a dependency *inside*
  `pyproject.toml` (pip requires an absolute `file://` URI there, and a
  relative one silently doesn't work on any platform). Install it
  separately instead: `pip install -e ../ai-data`, then
  `pip install -e .[dev]` for this package — same two commands as always,
  just no longer redundant with a broken third mechanism.
- **`uvicorn` command not found after installing** — usually a PATH
  issue with pip's user-site install (common on Windows). Use
  `python -m uvicorn app.main:app --reload` instead — always works
  regardless of PATH.
- **`psycopg2.OperationalError: could not translate host name
  "db.[ref].supabase.co" to address: Unknown server error`** — not a bug
  in this project. Supabase's direct connection hostname is IPv6-only
  unless you've paid for the IPv4 add-on; if your network doesn't route
  IPv6 properly, that specific hostname just won't resolve. Switch to the
  connection pooler string (Project Settings → Database → Connection
  pooling → Session mode) — it's IPv4-compatible. Remember the username
  changes to `postgres.[PROJECT-REF]` for the pooler, not just `postgres`.
- **`ValueError: invalid interpolation syntax` when running `alembic
  upgrade head`** — fixed as of this pass. Alembic's config is built on
  Python's `configparser`, which treats `%` as a special character; a
  Supabase password containing a URL-encoded character (commonly `%40`
  for `@`) breaks it unless escaped. `alembic/env.py` now escapes every
  `%` as `%%` before handing the URL to `set_main_option` — if you still
  see this, you're on an older copy of `env.py`.
- **`alembic upgrade head` says `Context impl SQLiteImpl` even though
  you set `DATABASE_URL` to your Supabase string** — means the app is
  still falling back to the SQLite default, so your `.env` isn't being
  picked up. Check: (1) you're running the command from inside `backend/`
  (where `.env` lives, same directory as `pyproject.toml`), (2) the file
  is actually named `.env`, not `.env.example` or `.env.txt`, (3) there's
  no leftover `DATABASE_URL` environment variable already set in your
  shell overriding the file (env vars take precedence over `.env`). You
  should see `Context impl PostgresqlImpl` once it's actually reading
  your Supabase connection string.
