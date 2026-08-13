"""Alembic env — carries BOTH this backend's tables and ai-data's tables
in one migration chain, per the boundary decision in the top-level README:
one shared Postgres database, one migration history, two separately
maintained `Base` declarations.

`target_metadata` is a `MetaData` that has every table from both `Base`s
merged into it (via `app.database.metadata.get_merged_metadata()`, shared
with the initial migration so both always agree on what "the schema" is),
so `alembic revision --autogenerate` picks up model changes made in
either package.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config.settings import settings
from app.database.metadata import get_merged_metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = get_merged_metadata()

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
