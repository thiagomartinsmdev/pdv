"""Regras de cadastro e consulta de produtos."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import Conflito, NaoEncontrado
from app.models import Produto
from app.schemas.produto import ProdutoAtualizar, ProdutoCriar


def listar(db: Session, busca: str | None = None, incluir_inativos: bool = False) -> list[Produto]:
    """Lista produtos ordenados por nome, com busca opcional por nome ou código de barras."""
    consulta = select(Produto).order_by(Produto.nome)
    if not incluir_inativos:
        consulta = consulta.where(Produto.ativo.is_(True))
    if busca:
        # autoescape: um "%" digitado na busca é tratado como texto, e não como curinga.
        consulta = consulta.where(
            or_(Produto.nome.icontains(busca, autoescape=True), Produto.codigo_barras == busca)
        )
    return list(db.scalars(consulta))


def buscar(db: Session, produto_id: int, travar: bool = False) -> Produto:
    """Busca por id. Com travar=True, bloqueia a linha (SELECT ... FOR UPDATE) até o commit."""
    consulta = select(Produto).where(Produto.id == produto_id)
    if travar:
        consulta = consulta.with_for_update()
    produto = db.scalar(consulta)
    if produto is None:
        raise NaoEncontrado(f"Produto {produto_id} não encontrado.")
    return produto


def buscar_por_codigo(db: Session, codigo_barras: str) -> Produto:
    """Usado pelo leitor de código de barras no caixa: só encontra produtos ativos."""
    produto = db.scalar(
        select(Produto).where(Produto.codigo_barras == codigo_barras, Produto.ativo.is_(True))
    )
    if produto is None:
        raise NaoEncontrado(f"Nenhum produto ativo com o código de barras {codigo_barras}.")
    return produto


def _garantir_codigo_livre(db: Session, codigo: str, ignorar_id: int | None = None) -> None:
    existente = db.scalar(select(Produto).where(Produto.codigo_barras == codigo))
    if existente is not None and existente.id != ignorar_id:
        raise Conflito(f"O código de barras {codigo} já pertence ao produto '{existente.nome}'.")


def criar(db: Session, dados: ProdutoCriar) -> Produto:
    _garantir_codigo_livre(db, dados.codigo_barras)
    produto = Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def atualizar(db: Session, produto_id: int, dados: ProdutoAtualizar) -> Produto:
    # A linha é travada porque o admin pode ajustar o estoque enquanto um caixa vende
    # o mesmo produto: assim uma operação espera a outra terminar, sem perder baixas.
    produto = buscar(db, produto_id, travar=True)
    alteracoes = dados.model_dump(exclude_unset=True)

    if "codigo_barras" in alteracoes:
        _garantir_codigo_livre(db, alteracoes["codigo_barras"], ignorar_id=produto.id)

    for campo, valor in alteracoes.items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)
    return produto


def desativar(db: Session, produto_id: int) -> None:
    """Exclusão lógica: o produto some do caixa, mas as vendas antigas continuam íntegras."""
    produto = buscar(db, produto_id, travar=True)
    produto.ativo = False
    db.commit()
