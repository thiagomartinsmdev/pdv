"""Valores fixos usados nos models (perfis, status e formas de pagamento)."""

from enum import StrEnum


class PerfilUsuario(StrEnum):
    ADMIN = "admin"
    OPERADOR = "operador"


class StatusVenda(StrEnum):
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class FormaPagamento(StrEnum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    DEBITO = "debito"
    CREDITO = "credito"
