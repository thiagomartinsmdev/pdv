"""Schemas (Pydantic) de entrada e saída de usuários.

Os schemas definem o formato do JSON da API. Eles são separados dos models
(tabelas) para que campos como senha_hash nunca saiam na resposta.
"""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

from app.models import PerfilUsuario

# E-mail sempre em minúsculas, para que "Admin@PDV.com" e "admin@pdv.com" sejam o mesmo.
Email = Annotated[EmailStr, AfterValidator(lambda email: email.lower())]
Nome = Annotated[str, Field(min_length=2, max_length=100)]
Senha = Annotated[str, Field(min_length=6, max_length=72)]  # bcrypt usa até 72 bytes


class UsuarioCriar(BaseModel):
    nome: Nome
    email: Email
    senha: Senha
    perfil: PerfilUsuario = PerfilUsuario.OPERADOR


class UsuarioAtualizar(BaseModel):
    """Todos os campos são opcionais: só o que for enviado é alterado."""

    nome: Nome | None = None
    email: Email | None = None
    senha: Senha | None = None
    perfil: PerfilUsuario | None = None
    ativo: bool | None = None


class UsuarioResposta(BaseModel):
    # from_attributes permite criar o schema direto a partir de um objeto do SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
