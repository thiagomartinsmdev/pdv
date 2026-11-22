"""Funções de segurança: hash de senha (bcrypt) e tokens de acesso (JWT)."""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import settings


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha. O salt é aleatório e fica embutido no hash."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere se a senha informada corresponde ao hash salvo no banco."""
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))


def criar_token_acesso(usuario_id: int) -> str:
    """Gera um JWT assinado que identifica o usuário.

    O token leva apenas o id (claim "sub") e a validade. O perfil NÃO vai no token:
    ele é lido do banco a cada requisição, então uma mudança de perfil ou a
    desativação do usuário vale na hora, sem esperar o token expirar.
    """
    agora = datetime.now(UTC)
    payload = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.jwt_expira_minutos),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algoritmo)


def ler_usuario_id_do_token(token: str) -> int | None:
    """Valida assinatura e validade do token e devolve o id do usuário.

    Retorna None se o token for inválido, adulterado ou estiver expirado.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algoritmo],
            options={"require": ["sub", "exp"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
