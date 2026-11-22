"""Tipos reutilizados pelos schemas."""

from decimal import Decimal
from typing import Annotated

from pydantic import Field

# Valor em dinheiro: não negativo, no máximo 2 casas decimais e 10 dígitos (igual à coluna).
# Na resposta JSON o Pydantic envia Decimal como texto ("8.49"), o que preserva o valor
# exato; o front converte para número só na hora de exibir.
ValorMonetario = Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]
