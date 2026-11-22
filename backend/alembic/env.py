"""Configuração de execução das migrations do Alembic."""

from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context
from app import models  # noqa: F401  (registra todas as tabelas em Base.metadata)
from app.core.config import settings
from app.core.database import Base

config = context.config

# Configura os logs pelo alembic.ini, exceto quando chamado pelos testes
# (para não sobrescrever a configuração de logs do pytest).
if config.config_file_name is not None and "connection" not in config.attributes:
    fileConfig(config.config_file_name)

# Metadados dos models: usados pelo "alembic revision --autogenerate".
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera o SQL das migrations sem conectar ao banco (alembic upgrade head --sql)."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _executar(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Conecta ao banco e aplica as migrations.

    Se quem chamou já passou uma conexão (os testes fazem isso para migrar o banco
    pdv_test), ela é usada; senão, conecta no DATABASE_URL do .env.
    """
    connection = config.attributes.get("connection")
    if connection is not None:
        _executar(connection)
        return

    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        _executar(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
