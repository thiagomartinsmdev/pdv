"""Regras de gerenciamento de usuários (somente admin)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import Conflito, NaoEncontrado, RegraNegocio
from app.core.security import gerar_hash_senha
from app.models import PerfilUsuario, Usuario
from app.schemas.usuario import UsuarioAtualizar, UsuarioCriar


def listar(db: Session) -> list[Usuario]:
    return list(db.scalars(select(Usuario).order_by(Usuario.nome)))


def buscar(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise NaoEncontrado(f"Usuário {usuario_id} não encontrado.")
    return usuario


def _garantir_email_livre(db: Session, email: str, ignorar_id: int | None = None) -> None:
    existente = db.scalar(select(Usuario).where(Usuario.email == email))
    if existente is not None and existente.id != ignorar_id:
        raise Conflito(f"Já existe um usuário com o e-mail {email}.")


def criar(db: Session, dados: UsuarioCriar) -> Usuario:
    _garantir_email_livre(db, dados.email)
    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
        perfil=dados.perfil,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def atualizar(
    db: Session, usuario_id: int, dados: UsuarioAtualizar, admin_logado: Usuario
) -> Usuario:
    usuario = buscar(db, usuario_id)
    # exclude_unset: considera só os campos que vieram no JSON.
    alteracoes = dados.model_dump(exclude_unset=True)

    # Impede que o admin tire o próprio acesso e fique trancado para fora do sistema.
    if usuario.id == admin_logado.id:
        if alteracoes.get("ativo") is False:
            raise RegraNegocio("Você não pode desativar o seu próprio usuário.")
        if alteracoes.get("perfil", PerfilUsuario.ADMIN) != PerfilUsuario.ADMIN:
            raise RegraNegocio("Você não pode remover o seu próprio perfil de administrador.")

    if "email" in alteracoes:
        _garantir_email_livre(db, alteracoes["email"], ignorar_id=usuario.id)
    if "senha" in alteracoes:
        usuario.senha_hash = gerar_hash_senha(alteracoes.pop("senha"))

    for campo, valor in alteracoes.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario
