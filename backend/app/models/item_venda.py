from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.tipos import Dinheiro

if TYPE_CHECKING:
    from app.models.produto import Produto
    from app.models.venda import Venda


class ItemVenda(Base):
    __tablename__ = "itens_venda"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="quantidade_positiva"),
        CheckConstraint("preco_unitario >= 0", name="preco_unitario_nao_negativo"),
        CheckConstraint("subtotal = quantidade * preco_unitario", name="subtotal_consistente"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    venda_id: Mapped[int] = mapped_column(
        ForeignKey("vendas.id", ondelete="CASCADE"), index=True
    )
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), index=True)
    quantidade: Mapped[int]
    # Cópia do preço no momento da venda: se o preço do produto mudar depois,
    # as vendas antigas continuam com o valor que foi realmente cobrado.
    preco_unitario: Mapped[Decimal] = mapped_column(Dinheiro)
    subtotal: Mapped[Decimal] = mapped_column(Dinheiro)

    venda: Mapped["Venda"] = relationship(back_populates="itens")
    produto: Mapped["Produto"] = relationship()

    def __repr__(self) -> str:
        return f"<ItemVenda produto_id={self.produto_id} qtd={self.quantidade}>"
