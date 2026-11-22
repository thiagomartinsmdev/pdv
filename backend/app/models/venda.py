from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import StatusVenda
from app.models.tipos import Dinheiro, enum_como_texto

if TYPE_CHECKING:
    from app.models.item_venda import ItemVenda
    from app.models.pagamento import Pagamento
    from app.models.sessao_caixa import SessaoCaixa
    from app.models.usuario import Usuario


class Venda(Base):
    __tablename__ = "vendas"
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="subtotal_nao_negativo"),
        CheckConstraint("desconto >= 0 AND desconto <= subtotal", name="desconto_valido"),
        CheckConstraint("total = subtotal - desconto", name="total_consistente"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sessao_caixa_id: Mapped[int] = mapped_column(ForeignKey("sessoes_caixa.id"), index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    # Indexado porque os relatórios e o histórico filtram por período.
    data_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    subtotal: Mapped[Decimal] = mapped_column(Dinheiro)
    desconto: Mapped[Decimal] = mapped_column(Dinheiro, default=Decimal("0"), server_default="0")
    total: Mapped[Decimal] = mapped_column(Dinheiro)
    status: Mapped[StatusVenda] = mapped_column(
        enum_como_texto(StatusVenda, "status"),
        default=StatusVenda.CONCLUIDA,
        server_default=StatusVenda.CONCLUIDA.value,
    )

    sessao_caixa: Mapped["SessaoCaixa"] = relationship(back_populates="vendas")
    usuario: Mapped["Usuario"] = relationship()
    # cascade: itens e pagamentos são salvos junto com a venda (e não existem sem ela).
    itens: Mapped[list["ItemVenda"]] = relationship(
        back_populates="venda", cascade="all, delete-orphan"
    )
    pagamentos: Mapped[list["Pagamento"]] = relationship(
        back_populates="venda", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Venda id={self.id} total={self.total} status={self.status}>"
