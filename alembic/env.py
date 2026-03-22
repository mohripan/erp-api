from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.db.base import Base  # noqa: F401 — imports Base + all models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is the metadata Alembic compares against your actual DB
# to figure out what migrations need to be generated.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Generates SQL scripts without a live DB connection.
    Useful for reviewing what will run before actually running it.
    """
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Connects to the DB and runs migrations directly.
    This is what `alembic upgrade head` uses.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
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