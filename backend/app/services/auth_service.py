"""Regras de autenticação."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NaoAutenticado
from app.core.security import gerar_hash_senha, verificar_senha
from app.models import Usuario

# Hash de uma senha qualquer, usado quando o e-mail não existe (ver autenticar()).
_HASH_FICTICIO = gerar_hash_senha("senha-ficticia-para-comparacao")


def autenticar(db: Session, email: str, senha: str) -> Usuario:
    """Devolve o usuário se e-mail e senha estiverem corretos.

    A mensagem de erro é a mesma para "e-mail não existe" e "senha errada", para
    não revelar quais e-mails estão cadastrados. Pelo mesmo motivo, o bcrypt roda
    mesmo quando o e-mail não existe: assim o tempo de resposta não denuncia nada.
    """
    usuario = db.scalar(select(Usuario).where(Usuario.email == email))

    senha_ok = verificar_senha(senha, usuario.senha_hash if usuario else _HASH_FICTICIO)
    if usuario is None or not senha_ok:
        raise NaoAutenticado("E-mail ou senha inválidos.")
    if not usuario.ativo:
        raise NaoAutenticado("Usuário desativado. Procure um administrador.")
    return usuario
