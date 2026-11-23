"""Schemas de entrada e saída de categorias."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NomeCategoria = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=2, max_length=60)
]
Ordem = Annotated[int, Field(ge=0, le=9999)]


class CategoriaCriar(BaseModel):
    nome: NomeCategoria
    ordem: Ordem = 0


class CategoriaAtualizar(BaseModel):
    """Todos os campos são opcionais: só o que for enviado é alterado."""

    nome: NomeCategoria | None = None
    ordem: Ordem | None = None
    ativo: bool | None = None


class CategoriaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    ordem: int
    ativo: bool


class CategoriaResumo(BaseModel):
    """Categoria embutida na resposta do produto."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
