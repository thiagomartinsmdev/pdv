from decimal import Decimal

from sqlalchemy import CheckConstraint, String, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.tipos import Dinheiro


class Produto(Base):
    __tablename__ = "produtos"
    __table_args__ = (
        CheckConstraint("preco >= 0", name="preco_nao_negativo"),
        # Última linha de defesa: mesmo que o código falhe, o banco recusa estoque negativo.
        CheckConstraint("quantidade_estoque >= 0", name="estoque_nao_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    codigo_barras: Mapped[str] = mapped_column(String(50), unique=True)
    preco: Mapped[Decimal] = mapped_column(Dinheiro)
    quantidade_estoque: Mapped[int] = mapped_column(default=0, server_default="0")
    # Produtos com vendas não podem ser apagados; são desativados.
    ativo: Mapped[bool] = mapped_column(default=True, server_default=true())

    def __repr__(self) -> str:
        return f"<Produto id={self.id} nome={self.nome!r} estoque={self.quantidade_estoque}>"
