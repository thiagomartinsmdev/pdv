"""Somatórios de vendas usados pelo fechamento de caixa e pelos relatórios.

Ficam num lugar só para que caixa e relatórios sigam exatamente a mesma regra:
só vendas concluídas contam, e em dinheiro o troco devolvido é descontado.
"""

from decimal import Decimal

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.models import FormaPagamento, Pagamento, StatusVenda, Venda

CENTAVO = Decimal("0.01")


def centavos(valor: Decimal | int | None) -> Decimal:
    """Normaliza para 2 casas decimais (None/0 vira 0.00)."""
    return Decimal(valor or 0).quantize(CENTAVO)


def vendas_concluidas(*filtros: ColumnElement[bool]) -> tuple[ColumnElement[bool], ...]:
    return (Venda.status == StatusVenda.CONCLUIDA, *filtros)


def quantidade_e_total(db: Session, *filtros: ColumnElement[bool]) -> tuple[int, Decimal]:
    """Quantidade de vendas concluídas e soma dos totais."""
    quantidade, total = db.execute(
        select(func.count(Venda.id), func.sum(Venda.total)).where(*vendas_concluidas(*filtros))
    ).one()
    return quantidade, centavos(total)


def total_por_forma(db: Session, *filtros: ColumnElement[bool]) -> dict[FormaPagamento, Decimal]:
    """Valor que ficou no caixa por forma de pagamento (todas as formas, mesmo as zeradas)."""
    linhas = db.execute(
        select(Pagamento.forma, func.sum(Pagamento.valor - Pagamento.troco))
        .join(Venda)
        .where(*vendas_concluidas(*filtros))
        .group_by(Pagamento.forma)
    ).all()
    recebido = dict(linhas)
    return {forma: centavos(recebido.get(forma)) for forma in FormaPagamento}
