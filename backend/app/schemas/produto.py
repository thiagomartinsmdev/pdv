"""Schemas de entrada e saída de produtos."""

from decimal import Decimal
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
)

from app.schemas.categoria import CategoriaResumo
from app.schemas.tipos import ValorMonetario
from app.services.imagem_service import eh_local

NomeProduto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
CodigoBarras = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Estoque = Annotated[int, Field(ge=0)]


def _vazio_vira_none(valor: object) -> object:
    """Campo de imagem apagado no formulário ("") significa "sem imagem"."""
    if isinstance(valor, str) and not valor.strip():
        return None
    return valor


def _validar_url_imagem(url: str) -> str:
    """Aceita links http(s) com domínio, ou o caminho de uma foto enviada ao servidor
    (/uploads/produtos/...). Isso impede, por exemplo, um link "javascript:..." que
    seria executado ao ser colocado numa página.

    O caminho local é aceito para o formulário poder reenviar a foto atual sem mudança;
    o service recusa trocar para OUTRO caminho local (fotos novas vêm pelo upload)."""
    if eh_local(url):
        return url
    partes = urlsplit(url)
    if partes.scheme not in ("http", "https") or not partes.netloc:
        raise ValueError("O link da imagem deve começar com http:// ou https://.")
    return url


ImagemUrl = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=500),
    AfterValidator(_validar_url_imagem),
]
# O "" -> None roda ANTES de o Pydantic escolher entre "texto" e "None".
ImagemOpcional = Annotated[ImagemUrl | None, BeforeValidator(_vazio_vira_none)]


class ProdutoCriar(BaseModel):
    nome: NomeProduto
    codigo_barras: CodigoBarras
    preco: ValorMonetario
    quantidade_estoque: Estoque = 0
    categoria_id: int | None = None
    imagem_url: ImagemOpcional = None


class ProdutoAtualizar(BaseModel):
    """Todos os campos são opcionais: só o que for enviado é alterado.
    Para tirar a categoria ou a imagem, envie o campo com null."""

    nome: NomeProduto | None = None
    codigo_barras: CodigoBarras | None = None
    preco: ValorMonetario | None = None
    quantidade_estoque: Estoque | None = None
    ativo: bool | None = None
    categoria_id: int | None = None
    imagem_url: ImagemOpcional = None


class ProdutoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    codigo_barras: str
    preco: Decimal
    quantidade_estoque: int
    ativo: bool
    categoria_id: int | None
    categoria: CategoriaResumo | None
    imagem_url: str | None
