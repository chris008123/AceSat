"""Merges this backend's table metadata with ai-data's, per the boundary
decision in the project README: one shared Postgres database, one
migration chain, two separately maintained `Base` declarations.

Pulled out of `alembic/env.py` into its own module so the initial
migration (`alembic/versions/..._initial_schema.py`) can reuse the exact
same merge logic rather than duplicating it — the migration and `env.py`
must always agree on what "the schema" is.
"""

from __future__ import annotations

from sqlalchemy import MetaData

from app.database.connection import Base as BackendBase

# Import every backend model module so they're registered on BackendBase
# before we read its metadata.
import app.models  # noqa: F401


def get_merged_metadata() -> MetaData:
    merged = MetaData()
    for table in BackendBase.metadata.tables.values():
        table.to_metadata(merged)

    try:
        from ai_data.models.base import Base as AIDataBase
        import ai_data.models.mastery  # noqa: F401
        import ai_data.models.memory  # noqa: F401
        import ai_data.retrieval.vector_search  # noqa: F401 — registers concept_embeddings

        for table in AIDataBase.metadata.tables.values():
            if table.name not in merged.tables:
                table.to_metadata(merged)
    except ImportError:
        # ai-data isn't installed in this environment — migration/schema
        # will only cover backend's own tables. Fine for isolated backend
        # testing; production should always have both installed (see
        # pyproject.toml's local dependency on ai-data).
        pass

    return merged
