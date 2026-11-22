"""Tipos de coluna reutilizados pelos models."""

from enum import StrEnum

from sqlalchemy import Enum, Numeric

# Valores em dinheiro: até 99.999.999,99, sempre com 2 casas decimais.
# No Python a coluna é lida como Decimal, que é exato (float não é: 0.1 + 0.2 != 0.3).
Dinheiro = Numeric(precision=10, scale=2)


def enum_como_texto(enum_cls: type[StrEnum], nome: str) -> Enum:
    """Guarda um enum como VARCHAR + CHECK constraint, e não como ENUM nativo do PostgreSQL.

    Assim, para incluir um valor novo basta alterar a CHECK constraint numa migration,
    sem a complexidade de alterar um tipo ENUM do banco.
    """
    return Enum(
        enum_cls,
        name=nome,
        native_enum=False,
        create_constraint=True,
        length=20,
        # Grava o valor ("admin"), e não o nome do membro ("ADMIN").
        values_callable=lambda membros: [m.value for m in membros],
        validate_strings=True,
    )
