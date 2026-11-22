from pydantic import BaseModel, Field

from app.schemas.usuario import Email, UsuarioResposta


class LoginRequisicao(BaseModel):
    email: Email
    senha: str = Field(min_length=1)


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_em_minutos: int
    # Já devolve os dados do usuário para o front não precisar chamar /auth/me logo em seguida.
    usuario: UsuarioResposta
