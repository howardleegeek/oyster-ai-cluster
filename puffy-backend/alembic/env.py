import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ensure the project root is on sys.path so that 'app' package is importable.
# alembic.ini already sets prepend_sys_path = . which handles this when run
# from the project root, but we add it explicitly as a safety net.
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

# Import the declarative Base and all model modules so that their tables are
# registered on Base.metadata before Alembic inspects it.
from app.models.base import Base  # noqa: E402
import app.models.user  # noqa: E402, F401
import app.models.order  # noqa: E402, F401
import app.models.product  # noqa: E402, F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to the project's Base.metadata so that autogenerate
# can detect model changes.
target_metadata = Base.metadata


def get_database_url() -> str:
    """Build the database URL from application settings.

    Falls back to the value in alembic.ini if the app settings cannot be
    loaded (e.g. missing .env file during CI).
    """
    try:
        from app.config import get_settings
        settings = get_settings()
        return (
            f"mysql://{settings.db_user}:{settings.db_passwd}"
            f"@{settings.db_host}/{settings.db_name}"
        )
    except Exception:
        # If settings are unavailable, let Alembic use whatever is in the ini
        return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Override the sqlalchemy.url from alembic.ini with the one derived from
    # application settings so that we always connect to the right database.
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
