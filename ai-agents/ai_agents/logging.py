"""Decision logging — writes every agent call to ai-data's `ai_logs`
table (`ai_data.models.memory.AILogRecord`, Database_design.txt §5.10),
so recommendations stay explainable end-to-end: not just "the reason
string looked evidence-based" but an actual persisted record of what
input an agent saw and what it decided, per Backend_architecture.txt §14
("Logging System" — "AI decisions, Agent performance").

Self-contained the same way `ai_data.services.memory_service` /
`app/services/memory_bridge.py` are: opens its own session via
`ai_data.models.db.get_session`, pointed at whatever `DATABASE_URL` the
caller passes in (the shared Postgres instance in production, a local
SQLite fallback otherwise).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from ai_data.models.db import get_session
from ai_data.models.memory import AILogRecord


def log_decision(
    database_url: str | None,
    student_id: UUID,
    agent_name: str,
    input_data: dict[str, Any],
    output_data: dict[str, Any],
) -> None:
    with get_session(database_url) as session:
        session.add(
            AILogRecord(
                student_id=student_id,
                agent_name=agent_name,
                input_data=input_data,
                output_data=output_data,
            )
        )
