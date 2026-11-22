"""Gerenciamento de usuários. Todos os endpoints exigem perfil admin.

Não há DELETE: usuários têm vendas e caixas ligados a eles, então são
desativados (PATCH com "ativo": false) em vez de apagados.
"""

from fastapi import APIRouter, status

from app.core.deps import AdminAtual, DbSession
from app.models import Usuario
from app.schemas.usuario import UsuarioAtualizar, UsuarioCriar, UsuarioResposta
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("", response_model=list[UsuarioResposta])
def listar(db: DbSession, _admin: AdminAtual) -> list[Usuario]:
    return usuario_service.listar(db)


@router.get("/{usuario_id}", response_model=UsuarioResposta)
def buscar(usuario_id: int, db: DbSession, _admin: AdminAtual) -> Usuario:
    return usuario_service.buscar(db, usuario_id)


@router.post("", response_model=UsuarioResposta, status_code=status.HTTP_201_CREATED)
def criar(dados: UsuarioCriar, db: DbSession, _admin: AdminAtual) -> Usuario:
    return usuario_service.criar(db, dados)


@router.patch("/{usuario_id}", response_model=UsuarioResposta)
def atualizar(
    usuario_id: int, dados: UsuarioAtualizar, db: DbSession, admin: AdminAtual
) -> Usuario:
    return usuario_service.atualizar(db, usuario_id, dados, admin_logado=admin)
