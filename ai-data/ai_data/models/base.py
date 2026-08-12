"""SQLAlchemy declarative base for the tables this module owns
(`topic_mastery`, `ai_memory`, `ai_logs` — see README boundary note).

Deliberately separate from any Base the Backend Engineer defines for their
own tables (`users`, `student_profiles`, `questions`, `assessments`,
`answers`, `learning_sessions`) so the two can be wired into one Alembic
migration chain without this module importing backend code, or vice versa.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
