"""Endpoints de produtos.

Consultas: qualquer usuário logado (o operador precisa buscar produtos no caixa).
Cadastro, alteração e desativação: somente admin.
"""

from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.core.deps import AdminAtual, DbSession, UsuarioAtual
from app.models import PerfilUsuario, Produto
from app.schemas.produto import ProdutoAtualizar, ProdutoCriar, ProdutoResposta
from app.services import produto_service

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("", response_model=list[ProdutoResposta])
def listar(
    db: DbSession,
    usuario: UsuarioAtual,
    busca: Annotated[str | None, Query(description="Parte do nome ou código exato")] = None,
    incluir_inativos: Annotated[bool, Query(description="Só tem efeito para admin")] = False,
    categoria_id: Annotated[int | None, Query(description="Só produtos desta categoria")] = None,
) -> list[Produto]:
    incluir_inativos = incluir_inativos and usuario.perfil == PerfilUsuario.ADMIN
    return produto_service.listar(
        db, busca=busca, incluir_inativos=incluir_inativos, categoria_id=categoria_id
    )


# As rotas com caminho fixo ficam ANTES de "/{produto_id}": senão o FastAPI tentaria
# ler "mais-vendidos" como um id numérico e responderia 422.
@router.get("/mais-vendidos", response_model=list[ProdutoResposta])
def mais_vendidos(
    db: DbSession,
    _usuario: UsuarioAtual,
    dias: Annotated[int, Query(ge=1, le=365, description="Janela de tempo, em dias")] = 30,
    limite: Annotated[int, Query(ge=1, le=50)] = 12,
) -> list[Produto]:
    """Produtos ativos mais vendidos nos últimos dias (aba "Mais vendidos" do caixa)."""
    return produto_service.mais_vendidos(db, dias=dias, limite=limite)


@router.get("/codigo/{codigo_barras}", response_model=ProdutoResposta)
def buscar_por_codigo(codigo_barras: str, db: DbSession, _usuario: UsuarioAtual) -> Produto:
    """Busca usada pelo leitor de código de barras do caixa (só produtos ativos)."""
    return produto_service.buscar_por_codigo(db, codigo_barras)


@router.get("/{produto_id}", response_model=ProdutoResposta)
def buscar(produto_id: int, db: DbSession, _usuario: UsuarioAtual) -> Produto:
    return produto_service.buscar(db, produto_id)


@router.post("", response_model=ProdutoResposta, status_code=status.HTTP_201_CREATED)
def criar(dados: ProdutoCriar, db: DbSession, _admin: AdminAtual) -> Produto:
    return produto_service.criar(db, dados)


@router.patch("/{produto_id}", response_model=ProdutoResposta)
def atualizar(
    produto_id: int, dados: ProdutoAtualizar, db: DbSession, _admin: AdminAtual
) -> Produto:
    return produto_service.atualizar(db, produto_id, dados)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar(produto_id: int, db: DbSession, _admin: AdminAtual) -> Response:
    """Desativa o produto (exclusão lógica). Para reativar, use PATCH com "ativo": true."""
    produto_service.desativar(db, produto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
