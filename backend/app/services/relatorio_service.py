"""Relatórios de vendas por período."""

from datetime import date, timedelta
from decimal import ROUND_HALF_UP

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.datas import intervalo_de_datas
from app.core.exceptions import RegraNegocio
from app.models import ItemVenda, Produto, StatusVenda, Venda
from app.schemas.relatorio import ProdutoMaisVendido, RelatorioVendas, VendasDoDia
from app.services import totais

PERIODO_MAXIMO_DIAS = 366


def relatorio_vendas(
    db: Session, inicio: date, fim: date, limite_produtos: int = 10
) -> RelatorioVendas:
    de, ate = intervalo_de_datas(inicio, fim)
    if (fim - inicio).days + 1 > PERIODO_MAXIMO_DIAS:
        raise RegraNegocio(f"O período máximo do relatório é de {PERIODO_MAXIMO_DIAS} dias.")
    no_periodo = (Venda.data_hora >= de, Venda.data_hora < ate)

    quantidade, total = totais.quantidade_e_total(db, *no_periodo)
    ticket_medio = (
        (total / quantidade).quantize(totais.CENTAVO, rounding=ROUND_HALF_UP)
        if quantidade
        else totais.centavos(0)
    )
    canceladas = db.scalar(
        select(func.count(Venda.id)).where(Venda.status == StatusVenda.CANCELADA, *no_periodo)
    )

    return RelatorioVendas(
        inicio=inicio,
        fim=fim,
        total_vendido=total,
        quantidade_vendas=quantidade,
        ticket_medio=ticket_medio,
        quantidade_canceladas=canceladas,
        total_por_forma=totais.total_por_forma(db, *no_periodo),
        produtos_mais_vendidos=_produtos_mais_vendidos(db, no_periodo, limite_produtos),
        vendas_por_dia=_vendas_por_dia(db, no_periodo, inicio, fim),
    )


def _produtos_mais_vendidos(
    db: Session, no_periodo: tuple[ColumnElement[bool], ...], limite: int
) -> list[ProdutoMaisVendido]:
    """Ranking por quantidade vendida; empate desempata pelo valor e depois pelo nome."""
    quantidade = func.sum(ItemVenda.quantidade).label("quantidade")
    total = func.sum(ItemVenda.subtotal).label("total")
    linhas = db.execute(
        select(Produto.id, Produto.nome, quantidade, total)
        .select_from(ItemVenda)
        .join(ItemVenda.produto)
        .join(ItemVenda.venda)
        .where(*totais.vendas_concluidas(*no_periodo))
        .group_by(Produto.id, Produto.nome)
        .order_by(quantidade.desc(), total.desc(), Produto.nome)
        .limit(limite)
    ).all()
    return [
        ProdutoMaisVendido(
            produto_id=linha.id,
            nome=linha.nome,
            quantidade=linha.quantidade,
            total=totais.centavos(linha.total),
        )
        for linha in linhas
    ]


def _vendas_por_dia(
    db: Session, no_periodo: tuple[ColumnElement[bool], ...], inicio: date, fim: date
) -> list[VendasDoDia]:
    """Total por dia no fuso local, preenchendo com zero os dias sem venda."""
    # timezone() do PostgreSQL converte o horário (guardado com fuso) para o horário local,
    # e date() pega só o dia. Assim uma venda às 23h em Brasília fica no dia certo.
    dia = func.date(func.timezone(settings.fuso_horario, Venda.data_hora)).label("dia")
    linhas = db.execute(
        select(dia, func.count(Venda.id), func.sum(Venda.total))
        .where(*totais.vendas_concluidas(*no_periodo))
        .group_by(dia)
    ).all()
    por_dia = {data: (qtd, total) for data, qtd, total in linhas}

    dias = (inicio + timedelta(days=n) for n in range((fim - inicio).days + 1))
    return [
        VendasDoDia(
            data=d,
            quantidade_vendas=por_dia.get(d, (0, None))[0],
            total=totais.centavos(por_dia.get(d, (0, None))[1]),
        )
        for d in dias
    ]
