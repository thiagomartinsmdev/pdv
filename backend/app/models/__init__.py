"""Importa todos os models.

Isso registra todas as tabelas em `Base.metadata`, o que o Alembic precisa
para enxergá-las, e permite importar com `from app.models import Produto`.
"""

from app.models.enums import FormaPagamento, PerfilUsuario, StatusVenda
from app.models.item_venda import ItemVenda
from app.models.pagamento import Pagamento
from app.models.produto import Produto
from app.models.sessao_caixa import SessaoCaixa
from app.models.usuario import Usuario
from app.models.venda import Venda

__all__ = [
    "FormaPagamento",
    "ItemVenda",
    "Pagamento",
    "PerfilUsuario",
    "Produto",
    "SessaoCaixa",
    "StatusVenda",
    "Usuario",
    "Venda",
]
