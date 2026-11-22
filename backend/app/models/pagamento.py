from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import FormaPagamento
from app.models.tipos import Dinheiro, enum_como_texto

if TYPE_CHECKING:
    from app.models.venda import Venda


class Pagamento(Base):
    __tablename__ = "pagamentos"
    __table_args__ = (
        CheckConstraint("valor > 0", name="valor_positivo"),
        CheckConstraint("troco >= 0", name="troco_nao_negativo"),
        # Regra de negócio garantida também pelo banco: só há troco em dinheiro.
        CheckConstraint("troco = 0 OR forma = 'dinheiro'", name="troco_somente_dinheiro"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    venda_id: Mapped[int] = mapped_column(
        ForeignKey("vendas.id", ondelete="CASCADE"), index=True
    )
    forma: Mapped[FormaPagamento] = mapped_column(enum_como_texto(FormaPagamento, "forma"))
    # Valor recebido nesta forma de pagamento (em dinheiro, inclui o que volta de troco).
    valor: Mapped[Decimal] = mapped_column(Dinheiro)
    troco: Mapped[Decimal] = mapped_column(Dinheiro, default=Decimal("0"), server_default="0")

    venda: Mapped["Venda"] = relationship(back_populates="pagamentos")

    def __repr__(self) -> str:
        return f"<Pagamento forma={self.forma} valor={self.valor} troco={self.troco}>"
