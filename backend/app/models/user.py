"""`users` table — Database_design.txt §5.1.

Authentication only (email, password hash, role). Academic data lives on
`StudentProfile`, not here — keeps this table small and matches the
prompt's general "avoid unnecessary sensitive personal information"
principle from the AI/Data side, applied here too: no name/DOB/etc. beyond
what auth actually needs. Add a `name` field only if the Frontend
Engineer's dashboard actually needs to display one.
"""

from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Uuid

from app.database.connection import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.STUDENT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student_profile: Mapped["StudentProfile | None"] = relationship(
        back_populates="user", uselist=False
    )
