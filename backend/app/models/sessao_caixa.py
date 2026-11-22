from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.tipos import Dinheiro

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.venda import Venda


class SessaoCaixa(Base):
    """Período em que um operador está com o caixa aberto.

    Enquanto `fechado_em` for NULL, o caixa está aberto.
    """

    __tablename__ = "sessoes_caixa"
    __table_args__ = (
        # Índice único PARCIAL: só vale para as linhas com o caixa aberto.
        # Garante no próprio banco que cada usuário tenha no máximo um caixa aberto,
        # mesmo se duas requisições de abertura chegarem ao mesmo tempo.
        Index(
            "uq_sessoes_caixa_usuario_aberto",
            "usuario_id",
            unique=True,
            postgresql_where=text("fechado_em IS NULL"),
        ),
        CheckConstraint("valor_abertura >= 0", name="valor_abertura_nao_negativo"),
        CheckConstraint("valor_informado_fechamento >= 0", name="valor_fechamento_nao_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    aberto_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    fechado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valor_abertura: Mapped[Decimal] = mapped_column(Dinheiro)
    valor_informado_fechamento: Mapped[Decimal | None] = mapped_column(Dinheiro)

    usuario: Mapped["Usuario"] = relationship(back_populates="sessoes_caixa")
    vendas: Mapped[list["Venda"]] = relationship(back_populates="sessao_caixa")

    @property
    def aberta(self) -> bool:
        return self.fechado_em is None

    def __repr__(self) -> str:
        return f"<SessaoCaixa id={self.id} usuario_id={self.usuario_id} aberta={self.aberta}>"
