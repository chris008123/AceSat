"""Alembic env — carries BOTH this backend's tables and ai-data's tables
in one migration chain, per the boundary decision in the top-level README:
one shared Postgres database, one migration history, two separately
maintained `Base` declarations.

`target_metadata` is a `MetaData` that has every table from both `Base`s
merged into it, so `alembic revision --autogenerate` picks up model
changes made in either package.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import MetaData, engine_from_config, pool

from app.config.settings import settings
from app.database.connection import Base as BackendBase

# Import every backend model module so they're registered on BackendBase
# before we read its metadata.
import app.models  # noqa: F401

try:
    from ai_data.models.base import Base as AIDataBase
    import ai_data.models.mastery  # noqa: F401
    import ai_data.models.memory  # noqa: F401

    _ai_data_available = True
except ImportError:
    # ai-data isn't installed in this environment (e.g. running backend
    # tests in isolation) — migrations will only cover backend's own
    # tables. Fine for local dev; production should always have both.
    _ai_data_available = False

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Merge both Bases' tables into one MetaData for autogenerate.
target_metadata = MetaData()
for table in BackendBase.metadata.tables.values():
    table.to_metadata(target_metadata)
if _ai_data_available:
    for table in AIDataBase.metadata.tables.values():
        if table.name not in target_metadata.tables:
            table.to_metadata(target_metadata)

config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
