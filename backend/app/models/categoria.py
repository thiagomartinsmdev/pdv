from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.produto import Produto


class Categoria(Base):
    """Agrupamento de produtos usado nas abas da grade do caixa (ex.: Pães, Bebidas)."""

    __tablename__ = "categorias"
    __table_args__ = (CheckConstraint("ordem >= 0", name="ordem_nao_negativa"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(60), unique=True)
    # Posição da aba no caixa: menor primeiro (empate: ordem alfabética).
    ordem: Mapped[int] = mapped_column(default=0, server_default="0")
    # Categorias são desativadas, e não apagadas: os produtos continuam ligados a elas.
    ativo: Mapped[bool] = mapped_column(default=True, server_default=true())

    produtos: Mapped[list["Produto"]] = relationship(back_populates="categoria")

    def __repr__(self) -> str:
        return f"<Categoria id={self.id} nome={self.nome!r}>"
