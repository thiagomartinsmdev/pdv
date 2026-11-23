"""Endpoints de categorias.

Listagem: qualquer usuário logado (o caixa monta as abas da grade com ela).
Cadastro, alteração e desativação: somente admin.
"""

from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.core.deps import AdminAtual, DbSession, UsuarioAtual
from app.models import Categoria, PerfilUsuario
from app.schemas.categoria import CategoriaAtualizar, CategoriaCriar, CategoriaResposta
from app.services import categoria_service

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("", response_model=list[CategoriaResposta])
def listar(
    db: DbSession,
    usuario: UsuarioAtual,
    incluir_inativas: Annotated[bool, Query(description="Só tem efeito para admin")] = False,
) -> list[Categoria]:
    """Categorias na ordem das abas do caixa."""
    incluir_inativas = incluir_inativas and usuario.perfil == PerfilUsuario.ADMIN
    return categoria_service.listar(db, incluir_inativas=incluir_inativas)


@router.post("", response_model=CategoriaResposta, status_code=status.HTTP_201_CREATED)
def criar(dados: CategoriaCriar, db: DbSession, _admin: AdminAtual) -> Categoria:
    return categoria_service.criar(db, dados)


@router.patch("/{categoria_id}", response_model=CategoriaResposta)
def atualizar(
    categoria_id: int, dados: CategoriaAtualizar, db: DbSession, _admin: AdminAtual
) -> Categoria:
    return categoria_service.atualizar(db, categoria_id, dados)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar(categoria_id: int, db: DbSession, _admin: AdminAtual) -> Response:
    """Desativa a categoria. Para reativar, use PATCH com "ativo": true."""
    categoria_service.desativar(db, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
