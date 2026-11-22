"""Endpoints de autenticação. Os routers só recebem, delegam ao service e respondem."""

from fastapi import APIRouter

from app.core.config import settings
from app.core.deps import DbSession, UsuarioAtual
from app.core.security import criar_token_acesso
from app.models import Usuario
from app.schemas.auth import LoginRequisicao, TokenResposta
from app.schemas.usuario import UsuarioResposta
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResposta)
def login(dados: LoginRequisicao, db: DbSession) -> TokenResposta:
    """Recebe e-mail e senha e devolve um token JWT."""
    usuario = auth_service.autenticar(db, dados.email, dados.senha)
    return TokenResposta(
        access_token=criar_token_acesso(usuario.id),
        expira_em_minutos=settings.jwt_expira_minutos,
        usuario=UsuarioResposta.model_validate(usuario),
    )


@router.get("/me", response_model=UsuarioResposta)
def me(usuario: UsuarioAtual) -> Usuario:
    """Devolve os dados do usuário dono do token."""
    return usuario
