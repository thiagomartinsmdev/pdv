"""cria tabelas iniciais

Revision ID: 0001
Revises:
Create Date: 2026-11-22
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DINHEIRO = sa.Numeric(precision=10, scale=2)


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("perfil", sa.String(20), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usuarios")),
        sa.UniqueConstraint("email", name=op.f("uq_usuarios_email")),
        sa.CheckConstraint("perfil IN ('admin', 'operador')", name=op.f("ck_usuarios_perfil")),
    )

    op.create_table(
        "produtos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("codigo_barras", sa.String(50), nullable=False),
        sa.Column("preco", DINHEIRO, nullable=False),
        sa.Column("quantidade_estoque", sa.Integer(), server_default="0", nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_produtos")),
        sa.UniqueConstraint("codigo_barras", name=op.f("uq_produtos_codigo_barras")),
        sa.CheckConstraint("preco >= 0", name=op.f("ck_produtos_preco_nao_negativo")),
        sa.CheckConstraint(
            "quantidade_estoque >= 0", name=op.f("ck_produtos_estoque_nao_negativo")
        ),
    )

    op.create_table(
        "sessoes_caixa",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column(
            "aberto_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("fechado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valor_abertura", DINHEIRO, nullable=False),
        sa.Column("valor_informado_fechamento", DINHEIRO, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessoes_caixa")),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], name=op.f("fk_sessoes_caixa_usuario_id_usuarios")
        ),
        sa.CheckConstraint(
            "valor_abertura >= 0", name=op.f("ck_sessoes_caixa_valor_abertura_nao_negativo")
        ),
        sa.CheckConstraint(
            "valor_informado_fechamento >= 0",
            name=op.f("ck_sessoes_caixa_valor_fechamento_nao_negativo"),
        ),
    )
    op.create_index(op.f("ix_sessoes_caixa_usuario_id"), "sessoes_caixa", ["usuario_id"])
    # Um único caixa aberto (fechado_em IS NULL) por usuário.
    op.create_index(
        "uq_sessoes_caixa_usuario_aberto",
        "sessoes_caixa",
        ["usuario_id"],
        unique=True,
        postgresql_where=sa.text("fechado_em IS NULL"),
    )

    op.create_table(
        "vendas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sessao_caixa_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column(
            "data_hora", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("subtotal", DINHEIRO, nullable=False),
        sa.Column("desconto", DINHEIRO, server_default="0", nullable=False),
        sa.Column("total", DINHEIRO, nullable=False),
        sa.Column("status", sa.String(20), server_default="concluida", nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vendas")),
        sa.ForeignKeyConstraint(
            ["sessao_caixa_id"],
            ["sessoes_caixa.id"],
            name=op.f("fk_vendas_sessao_caixa_id_sessoes_caixa"),
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], name=op.f("fk_vendas_usuario_id_usuarios")
        ),
        sa.CheckConstraint("status IN ('concluida', 'cancelada')", name=op.f("ck_vendas_status")),
        sa.CheckConstraint("subtotal >= 0", name=op.f("ck_vendas_subtotal_nao_negativo")),
        sa.CheckConstraint(
            "desconto >= 0 AND desconto <= subtotal", name=op.f("ck_vendas_desconto_valido")
        ),
        sa.CheckConstraint("total = subtotal - desconto", name=op.f("ck_vendas_total_consistente")),
    )
    op.create_index(op.f("ix_vendas_sessao_caixa_id"), "vendas", ["sessao_caixa_id"])
    op.create_index(op.f("ix_vendas_usuario_id"), "vendas", ["usuario_id"])
    op.create_index(op.f("ix_vendas_data_hora"), "vendas", ["data_hora"])

    op.create_table(
        "itens_venda",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("venda_id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("preco_unitario", DINHEIRO, nullable=False),
        sa.Column("subtotal", DINHEIRO, nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_itens_venda")),
        sa.ForeignKeyConstraint(
            ["venda_id"],
            ["vendas.id"],
            name=op.f("fk_itens_venda_venda_id_vendas"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["produto_id"], ["produtos.id"], name=op.f("fk_itens_venda_produto_id_produtos")
        ),
        sa.CheckConstraint("quantidade > 0", name=op.f("ck_itens_venda_quantidade_positiva")),
        sa.CheckConstraint(
            "preco_unitario >= 0", name=op.f("ck_itens_venda_preco_unitario_nao_negativo")
        ),
        sa.CheckConstraint(
            "subtotal = quantidade * preco_unitario",
            name=op.f("ck_itens_venda_subtotal_consistente"),
        ),
    )
    op.create_index(op.f("ix_itens_venda_venda_id"), "itens_venda", ["venda_id"])
    op.create_index(op.f("ix_itens_venda_produto_id"), "itens_venda", ["produto_id"])

    op.create_table(
        "pagamentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("venda_id", sa.Integer(), nullable=False),
        sa.Column("forma", sa.String(20), nullable=False),
        sa.Column("valor", DINHEIRO, nullable=False),
        sa.Column("troco", DINHEIRO, server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pagamentos")),
        sa.ForeignKeyConstraint(
            ["venda_id"],
            ["vendas.id"],
            name=op.f("fk_pagamentos_venda_id_vendas"),
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "forma IN ('dinheiro', 'pix', 'debito', 'credito')", name=op.f("ck_pagamentos_forma")
        ),
        sa.CheckConstraint("valor > 0", name=op.f("ck_pagamentos_valor_positivo")),
        sa.CheckConstraint("troco >= 0", name=op.f("ck_pagamentos_troco_nao_negativo")),
        sa.CheckConstraint(
            "troco = 0 OR forma = 'dinheiro'", name=op.f("ck_pagamentos_troco_somente_dinheiro")
        ),
    )
    op.create_index(op.f("ix_pagamentos_venda_id"), "pagamentos", ["venda_id"])


def downgrade() -> None:
    # Ordem inversa da criação, por causa das chaves estrangeiras.
    op.drop_table("pagamentos")
    op.drop_table("itens_venda")
    op.drop_table("vendas")
    op.drop_table("sessoes_caixa")
    op.drop_table("produtos")
    op.drop_table("usuarios")
