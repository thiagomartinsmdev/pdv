"""Schemas de entrada e saída de vendas."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models import FormaPagamento, StatusVenda
from app.schemas.tipos import ValorMonetario

ValorPositivo = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]


# ---------- Entrada ----------


class ItemVendaEntrada(BaseModel):
    produto_id: int
    quantidade: Annotated[int, Field(gt=0, le=10_000)]


class PagamentoEntrada(BaseModel):
    forma: FormaPagamento
    # Valor entregue pelo cliente nesta forma. Em dinheiro pode passar do total (gera troco).
    valor: ValorPositivo


class VendaCriar(BaseModel):
    """O preço NÃO vem do cliente: é lido do cadastro do produto no momento da venda."""

    itens: Annotated[list[ItemVendaEntrada], Field(min_length=1)]
    pagamentos: Annotated[list[PagamentoEntrada], Field(min_length=1)]
    desconto: ValorMonetario = Decimal("0.00")


# ---------- Saída ----------


class _Resposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProdutoResumo(_Resposta):
    id: int
    nome: str
    codigo_barras: str


class UsuarioResumo(_Resposta):
    id: int
    nome: str


class ItemVendaResposta(_Resposta):
    id: int
    produto: ProdutoResumo
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal


class PagamentoResposta(_Resposta):
    forma: FormaPagamento
    valor: Decimal
    troco: Decimal


class VendaResposta(_Resposta):
    id: int
    sessao_caixa_id: int
    usuario: UsuarioResumo
    data_hora: datetime
    subtotal: Decimal
    desconto: Decimal
    total: Decimal
    status: StatusVenda
    itens: list[ItemVendaResposta]
    pagamentos: list[PagamentoResposta]

    @computed_field
    @property
    def troco(self) -> Decimal:
        """Troco total devolvido ao cliente."""
        return sum((p.troco for p in self.pagamentos), Decimal("0.00"))
