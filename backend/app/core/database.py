"""Conexão com o banco: engine, fábrica de sessões e classe base dos models."""

from collections.abc import Generator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Padrão de nomes para constraints e índices. Sem isso, o PostgreSQL gera nomes
# automáticos, e as migrations futuras (ex.: remover uma constraint) ficam frágeis.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Classe base de todos os models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# pool_pre_ping testa a conexão antes de usá-la, evitando erros com conexões
# que o banco encerrou por inatividade.
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """Dependência do FastAPI: abre uma sessão por requisição e sempre a fecha."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
