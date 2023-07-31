from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from config import settings, starless_logger
from database.model import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

target_metadata = Base.metadata
db_uri = f'postgresql://{settings.postgres_db_user}:{settings.postgres_db_password}'
db_uri += f'@{settings.postgres_db_host}:{settings.postgres_db_port}/{settings.postgres_db_name}'

config.set_main_option('sqlalchemy.url', db_uri)
config.set_main_option('prepend_sys_path', settings.base_dir)
config.set_main_option('script_location', 'database/alembic')


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=db_uri,
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
