"""Garantias sobre as migrations e o script de seed."""

import contextlib
import io

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import func, select

from app.core.database import Base
from app.models import Categoria, Produto, Usuario
from scripts.seed import CATEGORIAS, PRODUTOS, executar_seed


def test_migrations_estao_em_dia_com_os_models(engine):
    """O banco criado pelas migrations precisa ser igual ao descrito nos models.

    Se alguém alterar um model e esquecer (ou errar) a migration, este teste falha
    e mostra a diferença.
    """
    with engine.connect() as conexao:
        diferencas = compare_metadata(MigrationContext.configure(conexao), Base.metadata)

    assert diferencas == []


def test_seed_cria_categorias_e_associa_os_produtos(db):
    with contextlib.redirect_stdout(io.StringIO()):
        executar_seed(db)

    categorias = {c.nome: c for c in db.scalars(select(Categoria))}
    produtos = list(db.scalars(select(Produto)))
    assert sorted(categorias) == sorted(CATEGORIAS)
    assert len(produtos) == len(PRODUTOS) == 20
    assert all(p.categoria_id is not None for p in produtos)
    assert all(p.imagem_url is None for p in produtos)  # as fotos são cadastradas pelo admin
    # A ordem das abas segue a lista do seed.
    ordem = sorted(categorias.values(), key=lambda c: c.ordem)
    assert [c.nome for c in ordem] == CATEGORIAS


def test_seed_pode_rodar_de_novo_sem_duplicar_nem_sobrescrever(db):
    with contextlib.redirect_stdout(io.StringIO()):
        executar_seed(db)
        # O admin troca a categoria de um produto...
        pao = db.scalar(select(Produto).where(Produto.codigo_barras == "7891000000014"))
        doces = db.scalar(select(Categoria).where(Categoria.nome == "Doces"))
        pao.categoria_id = doces.id
        db.commit()
        # ...e o seed roda de novo.
        executar_seed(db)

    assert db.scalar(select(func.count(Categoria.id))) == 6
    assert db.scalar(select(func.count(Produto.id))) == 20
    assert db.scalar(select(func.count(Usuario.id))) == 2
    db.refresh(pao)
    assert pao.categoria_id == doces.id
