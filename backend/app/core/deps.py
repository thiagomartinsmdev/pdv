"""Dependências do FastAPI para autenticação e controle de acesso por perfil.

Uso nos routers:
    usuario: Usuario = Depends(get_usuario_atual)   # qualquer usuário logado
    usuario: Usuario = Depends(exigir_admin)        # só admin
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AcessoNegado, NaoAutenticado
from app.core.security import ler_usuario_id_do_token
from app.models import PerfilUsuario, Usuario

# Lê o cabeçalho "Authorization: Bearer <token>". auto_error=False para que a
# mensagem de erro seja a nossa, e não a padrão do FastAPI.
# Também adiciona o botão "Authorize" no /docs.
bearer = HTTPBearer(auto_error=False, description="Token obtido em POST /auth/login")

DbSession = Annotated[Session, Depends(get_db)]


def get_usuario_atual(
    db: DbSession,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Usuario:
    if credenciais is None:
        raise NaoAutenticado("Token de acesso não informado.")

    usuario_id = ler_usuario_id_do_token(credenciais.credentials)
    if usuario_id is None:
        raise NaoAutenticado("Token inválido ou expirado. Faça login novamente.")

    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        raise NaoAutenticado("Usuário não encontrado ou desativado.")
    return usuario


UsuarioAtual = Annotated[Usuario, Depends(get_usuario_atual)]


def exigir_admin(usuario: UsuarioAtual) -> Usuario:
    if usuario.perfil != PerfilUsuario.ADMIN:
        raise AcessoNegado("Apenas administradores podem realizar esta ação.")
    return usuario


AdminAtual = Annotated[Usuario, Depends(exigir_admin)]
