"""Schemas dos relatórios."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.models import FormaPagamento


class ProdutoMaisVendido(BaseModel):
    produto_id: int
    nome: str
    quantidade: int
    # Soma dos itens pelo preço cobrado na venda (antes do desconto geral da venda).
    total: Decimal


class VendasDoDia(BaseModel):
    data: date
    quantidade_vendas: int
    total: Decimal


class RelatorioVendas(BaseModel):
    """Resumo das vendas concluídas no período. Vendas canceladas só entram na contagem própria."""

    inicio: date
    fim: date
    total_vendido: Decimal
    quantidade_vendas: int
    ticket_medio: Decimal  # total vendido / quantidade de vendas
    quantidade_canceladas: int
    total_por_forma: dict[FormaPagamento, Decimal]
    produtos_mais_vendidos: list[ProdutoMaisVendido]
    # Todos os dias do período, inclusive os sem venda (com zero), prontos para o gráfico.
    vendas_por_dia: list[VendasDoDia]
