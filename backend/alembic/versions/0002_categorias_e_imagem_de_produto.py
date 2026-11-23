"""categorias e imagem de produto

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-23
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(60), nullable=False),
        sa.Column("ordem", sa.Integer(), server_default="0", nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categorias")),
        sa.UniqueConstraint("nome", name=op.f("uq_categorias_nome")),
        sa.CheckConstraint("ordem >= 0", name=op.f("ck_categorias_ordem_nao_negativa")),
    )

    # Colunas novas são opcionais (NULL), então os produtos existentes continuam válidos.
    op.add_column("produtos", sa.Column("categoria_id", sa.Integer(), nullable=True))
    op.add_column("produtos", sa.Column("imagem_url", sa.String(500), nullable=True))
    op.create_foreign_key(
        op.f("fk_produtos_categoria_id_categorias"),
        "produtos",
        "categorias",
        ["categoria_id"],
        ["id"],
    )
    op.create_index(op.f("ix_produtos_categoria_id"), "produtos", ["categoria_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_produtos_categoria_id"), table_name="produtos")
    op.drop_constraint(op.f("fk_produtos_categoria_id_categorias"), "produtos", type_="foreignkey")
    op.drop_column("produtos", "imagem_url")
    op.drop_column("produtos", "categoria_id")
    op.drop_table("categorias")
