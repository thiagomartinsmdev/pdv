"""Schemas de entrada e saída de produtos."""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.schemas.tipos import ValorMonetario

NomeProduto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
CodigoBarras = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)
]
Estoque = Annotated[int, Field(ge=0)]


class ProdutoCriar(BaseModel):
    nome: NomeProduto
    codigo_barras: CodigoBarras
    preco: ValorMonetario
    quantidade_estoque: Estoque = 0


class ProdutoAtualizar(BaseModel):
    """Todos os campos são opcionais: só o que for enviado é alterado."""

    nome: NomeProduto | None = None
    codigo_barras: CodigoBarras | None = None
    preco: ValorMonetario | None = None
    quantidade_estoque: Estoque | None = None
    ativo: bool | None = None


class ProdutoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    codigo_barras: str
    preco: Decimal
    quantidade_estoque: int
    ativo: bool
