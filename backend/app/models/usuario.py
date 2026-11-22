from typing import TYPE_CHECKING

from sqlalchemy import String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import PerfilUsuario
from app.models.tipos import enum_como_texto

if TYPE_CHECKING:
    from app.models.sessao_caixa import SessaoCaixa


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[PerfilUsuario] = mapped_column(enum_como_texto(PerfilUsuario, "perfil"))
    # Usuários não são apagados (têm vendas ligadas a eles); são desativados.
    ativo: Mapped[bool] = mapped_column(default=True, server_default=true())

    sessoes_caixa: Mapped[list["SessaoCaixa"]] = relationship(back_populates="usuario")

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email!r} perfil={self.perfil}>"
