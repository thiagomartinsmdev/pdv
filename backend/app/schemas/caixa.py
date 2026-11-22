"""Schemas de abertura, fechamento e consulta do caixa."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models import FormaPagamento
from app.schemas.tipos import ValorMonetario


class CaixaAbrir(BaseModel):
    valor_abertura: ValorMonetario  # dinheiro deixado na gaveta para troco


class CaixaFechar(BaseModel):
    valor_informado: ValorMonetario  # dinheiro contado na gaveta pelo operador


class ResumoCaixa(BaseModel):
    """Totais das vendas concluídas da sessão (vendas canceladas não entram)."""

    quantidade_vendas: int
    total_vendido: Decimal
    # Valor que ficou no caixa por forma de pagamento (em dinheiro, já descontado o troco).
    total_por_forma: dict[FormaPagamento, Decimal]
    # valor de abertura + dinheiro recebido - troco devolvido
    valor_esperado_dinheiro: Decimal


class CaixaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    aberto_em: datetime
    fechado_em: datetime | None
    valor_abertura: Decimal
    valor_informado_fechamento: Decimal | None
    resumo: ResumoCaixa
    # valor informado - valor esperado: positivo = sobra, negativo = falta.
    # Só existe depois do fechamento.
    diferenca: Decimal | None
