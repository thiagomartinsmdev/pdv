"""Regras de cadastro de categorias."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import Conflito, NaoEncontrado
from app.models import Categoria
from app.schemas.categoria import CategoriaAtualizar, CategoriaCriar


def listar(db: Session, incluir_inativas: bool = False) -> list[Categoria]:
    """Na ordem das abas do caixa: campo "ordem" e, no empate, nome."""
    consulta = select(Categoria).order_by(Categoria.ordem, Categoria.nome)
    if not incluir_inativas:
        consulta = consulta.where(Categoria.ativo.is_(True))
    return list(db.scalars(consulta))


def buscar(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise NaoEncontrado(f"Categoria {categoria_id} não encontrada.")
    return categoria


def _garantir_nome_livre(db: Session, nome: str, ignorar_id: int | None = None) -> None:
    # Sem diferenciar maiúsculas: "Bebidas" e "bebidas" seriam a mesma aba no caixa.
    existente = db.scalar(select(Categoria).where(func.lower(Categoria.nome) == nome.lower()))
    if existente is not None and existente.id != ignorar_id:
        raise Conflito(f"Já existe a categoria '{existente.nome}'.")


def criar(db: Session, dados: CategoriaCriar) -> Categoria:
    _garantir_nome_livre(db, dados.nome)
    categoria = Categoria(**dados.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def atualizar(db: Session, categoria_id: int, dados: CategoriaAtualizar) -> Categoria:
    categoria = buscar(db, categoria_id)
    alteracoes = dados.model_dump(exclude_unset=True)
    if "nome" in alteracoes:
        _garantir_nome_livre(db, alteracoes["nome"], ignorar_id=categoria.id)
    for campo, valor in alteracoes.items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


def desativar(db: Session, categoria_id: int) -> None:
    """Exclusão lógica: a aba some do caixa, mas os produtos continuam ligados a ela
    (e aparecem na aba "Todos")."""
    categoria = buscar(db, categoria_id)
    categoria.ativo = False
    db.commit()
