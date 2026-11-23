from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.tipos import Dinheiro

if TYPE_CHECKING:
    from app.models.categoria import Categoria


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
    # Opcionais: produto sem categoria aparece só na aba "Todos"; sem imagem, o
    # caixa mostra a inicial do nome.
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"), index=True)
    imagem_url: Mapped[str | None] = mapped_column(String(500))

    categoria: Mapped["Categoria | None"] = relationship(back_populates="produtos")

    def __repr__(self) -> str:
        return f"<Produto id={self.id} nome={self.nome!r} estoque={self.quantidade_estoque}>"
