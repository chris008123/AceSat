"""add questions.explanation column

Revision ID: 0002_question_explanation
Revises: 0001_initial_schema
Create Date: 2026-08-14

Frontend integration pass: `QuestionCard` shows an explanation once the
student answers, matching `ai_data.models.question.Question.explanation`.
The backend-owned `questions` table didn't have this column yet — added
here as a plain nullable `Text` column so existing rows don't need
backfilling.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_question_explanation"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col["name"] for col in inspector.get_columns("questions")}
    if "explanation" not in existing_columns:
        # On a fresh database, 0001's `metadata.create_all()` already
        # creates `questions` from the *current* model (which now
        # includes `explanation`), so this migration is a no-op there.
        # On a pre-existing database created before this column existed,
        # it actually adds the column. Guarding on existence keeps
        # `alembic upgrade head` safe to run from either starting point.
        op.add_column("questions", sa.Column("explanation", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("questions", "explanation")
