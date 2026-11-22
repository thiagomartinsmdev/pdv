from decimal import Decimal


def reais(valor: Decimal) -> str:
    """Formata um valor para mensagens: Decimal("1234.5") -> "R$ 1.234,50"."""
    texto = f"{valor:,.2f}"  # "1,234.50"
    return "R$ " + texto.replace(",", "_").replace(".", ",").replace("_", ".")
