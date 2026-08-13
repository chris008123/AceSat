"""FastAPI entrypoint — Backend_architecture.txt §4 (`main.py` at the
`app/` root).

Phase 1 only: app instance, CORS, a health check, and DB table creation
for local dev. Route modules (`api/routes/*.py`) get wired in during
Phase 2 once auth/student/assessment endpoints exist — importing an empty
router now would just be noise.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ai_router, assessment_router, auth_router, students_router
from app.config.settings import settings
from app.database.connection import init_db
from app.utils.errors import APIError, api_error_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment == "development":
        # Local dev convenience only — real deployments use the Alembic
        # migration chain in `alembic/`, which also carries ai-data's
        # tables (see alembic/env.py).
        init_db()
    yield


app = FastAPI(title="AceMentor AI Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(APIError, api_error_handler)

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(assessment_router)
app.include_router(ai_router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "environment": settings.environment}

