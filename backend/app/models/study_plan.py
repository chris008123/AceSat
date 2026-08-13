"""`study_plans` table — Database_design.txt §5.6.

Persists whatever `/ai/study-plan` produces (see `app/services/ai_bridge.py`),
so a plan doesn't need to be regenerated from scratch on every dashboard
load.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base

_JSONType = JSON().with_variant(JSONB, "postgresql")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("student_profiles.id"), index=True)
    plan_date: Mapped[date] = mapped_column(Date, default=date.today)
    activity: Mapped[list] = mapped_column(_JSONType)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
