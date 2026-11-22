"""Infraestrutura dos testes.

- Usa um banco PostgreSQL separado (pdv_test). Não usamos SQLite porque as regras
  testadas dependem do PostgreSQL: SELECT ... FOR UPDATE, índice único parcial e
  CHECK constraints.
- O esquema é criado rodando as migrations do Alembic, então os testes também
  garantem que as migrations estão corretas.
- Depois de cada teste, todas as tabelas são esvaziadas (TRUNCATE): cada teste
  começa com o banco vazio e não depende da ordem de execução.
"""

import os
from collections.abc import Callable, Generator
from decimal import Decimal
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import criar_token_acesso, gerar_hash_senha
from app.main import app
from app.models import PerfilUsuario, Produto, SessaoCaixa, Usuario

BACKEND_DIR = Path(__file__).resolve().parents[1]

# Banco de testes: TEST_DATABASE_URL, ou o mesmo servidor do .env com o banco "pdv_test".
URL_TESTE = make_url(
    os.environ.get("TEST_DATABASE_URL") or make_url(settings.database_url).set(database="pdv_test")
)
if not URL_TESTE.database or not URL_TESTE.database.endswith("_test"):
    # Trava de segurança: os testes apagam os dados do banco usado.
    raise RuntimeError(
        f"O banco de testes deve terminar em '_test' (recebido: {URL_TESTE.database})."
    )

# bcrypt é lento de propósito; gerar o hash uma vez só deixa os testes bem mais rápidos.
SENHA_PADRAO = "senha123"
HASH_PADRAO = gerar_hash_senha(SENHA_PADRAO)


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    engine = create_engine(URL_TESTE)
    with engine.begin() as conexao:
        # Recomeça do zero e aplica as migrations.
        Base.metadata.drop_all(conexao)
        conexao.execute(text("DROP TABLE IF EXISTS alembic_version"))
        config = Config(str(BACKEND_DIR / "alembic.ini"))
        config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
        config.attributes["connection"] = conexao
        command.upgrade(config, "head")
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def fabrica_sessao(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def db(engine: Engine, fabrica_sessao: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Sessão para o teste preparar dados e conferir resultados."""
    sessao = fabrica_sessao()
    yield sessao
    sessao.close()
    tabelas = ", ".join(tabela.name for tabela in Base.metadata.sorted_tables)
    with engine.begin() as conexao:
        conexao.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))


@pytest.fixture
def client(db: Session, fabrica_sessao: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    """Cliente HTTP da API apontando para o banco de testes."""

    def get_db_teste() -> Generator[Session, None, None]:
        sessao = fabrica_sessao()
        try:
            yield sessao
        finally:
            sessao.close()

    app.dependency_overrides[get_db] = get_db_teste
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Dados de exemplo
# ---------------------------------------------------------------------------


@pytest.fixture
def criar_usuario(db: Session) -> Callable[..., Usuario]:
    def _criar(
        email: str = "operador@teste.com", perfil: PerfilUsuario = PerfilUsuario.OPERADOR
    ) -> Usuario:
        usuario = Usuario(
            nome=email.split("@")[0].title(), email=email, senha_hash=HASH_PADRAO, perfil=perfil
        )
        db.add(usuario)
        db.commit()
        return usuario

    return _criar


@pytest.fixture
def admin(criar_usuario: Callable[..., Usuario]) -> Usuario:
    return criar_usuario("admin@teste.com", PerfilUsuario.ADMIN)


@pytest.fixture
def operador(criar_usuario: Callable[..., Usuario]) -> Usuario:
    return criar_usuario("operador@teste.com", PerfilUsuario.OPERADOR)


def cabecalho(usuario: Usuario) -> dict[str, str]:
    """Cabeçalho de autenticação para o usuário (sem passar pelo endpoint de login)."""
    return {"Authorization": f"Bearer {criar_token_acesso(usuario.id)}"}


@pytest.fixture
def auth_admin(admin: Usuario) -> dict[str, str]:
    return cabecalho(admin)


@pytest.fixture
def auth_operador(operador: Usuario) -> dict[str, str]:
    return cabecalho(operador)


@pytest.fixture
def criar_produto(db: Session) -> Callable[..., Produto]:
    contador = iter(range(1, 10_000))

    def _criar(nome: str = "Produto", preco: str = "10.00", estoque: int = 10) -> Produto:
        produto = Produto(
            nome=nome,
            codigo_barras=f"789{next(contador):010d}",
            preco=Decimal(preco),
            quantidade_estoque=estoque,
        )
        db.add(produto)
        db.commit()
        return produto

    return _criar


@pytest.fixture
def abrir_caixa(db: Session) -> Callable[..., SessaoCaixa]:
    def _abrir(usuario: Usuario, valor_abertura: str = "100.00") -> SessaoCaixa:
        sessao = SessaoCaixa(usuario_id=usuario.id, valor_abertura=Decimal(valor_abertura))
        db.add(sessao)
        db.commit()
        return sessao

    return _abrir


@pytest.fixture
def caixa_operador(operador: Usuario, abrir_caixa: Callable[..., SessaoCaixa]) -> SessaoCaixa:
    return abrir_caixa(operador)
