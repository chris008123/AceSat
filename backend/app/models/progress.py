"""`progress_records` table — Database_design.txt §5.8.

Per-subject snapshots over time, distinct from ai-data's `topic_mastery`
(per-topic, recomputed on demand). This table is what
`GET /progress/dashboard` and `GET /progress/report` (Api_design.txt §10)
read from — cheap to query for a dashboard without recomputing analysis
from the full `answers`/`learning_sessions` history on every page load.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("student_profiles.id"), index=True)
    subject: Mapped[str] = mapped_column(String, index=True)
    score: Mapped[float] = mapped_column(Float)
    mastery_level: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
