"""Testes do relatório de vendas por período.

Cenário (datas no horário de Brasília), relatório de 03/11 a 06/11:
- V1 03/11 10:00  5 x A (2,00) + 1 x B (5,00) = 15,00   dinheiro 20,00 (troco 5,00)
- V2 03/11 23:30  1 x C (10,00)               = 10,00   pix (já é 04/11 em UTC)
- V3 05/11 09:00  2 x A + 1 x C = 14,00 - 2,00 desc. = 12,00   débito
- V4 05/11 12:00  10 x B = 50,00   crédito   -> CANCELADA
- V5 07/11 08:00  1 x B = 5,00     pix       -> fora do período
"""

from datetime import datetime

import pytest

from app.core.datas import FUSO
from app.models import Venda

URL = "/relatorios/vendas"
PERIODO = {"inicio": "2026-11-03", "fim": "2026-11-06"}


@pytest.fixture
def cenario(client, db, admin, auth_admin, abrir_caixa, criar_produto):
    abrir_caixa(admin)
    a = criar_produto("Produto A", preco="2.00", estoque=100)
    b = criar_produto("Produto B", preco="5.00", estoque=100)
    c = criar_produto("Produto C", preco="10.00", estoque=100)

    def vender(quando: datetime, itens, forma: str, valor: str, desconto: str = "0") -> int:
        corpo = {
            "itens": [{"produto_id": p.id, "quantidade": q} for p, q in itens],
            "pagamentos": [{"forma": forma, "valor": valor}],
            "desconto": desconto,
        }
        resposta = client.post("/vendas", json=corpo, headers=auth_admin)
        assert resposta.status_code == 201, resposta.text
        venda_id = resposta.json()["id"]
        db.get(Venda, venda_id).data_hora = quando.replace(tzinfo=FUSO)
        db.commit()
        return venda_id

    vender(datetime(2026, 11, 3, 10, 0), [(a, 5), (b, 1)], "dinheiro", "20.00")
    vender(datetime(2026, 11, 3, 23, 30), [(c, 1)], "pix", "10.00")
    vender(datetime(2026, 11, 5, 9, 0), [(a, 2), (c, 1)], "debito", "12.00", desconto="2.00")
    v4 = vender(datetime(2026, 11, 5, 12, 0), [(b, 10)], "credito", "50.00")
    vender(datetime(2026, 11, 7, 8, 0), [(b, 1)], "pix", "5.00")
    client.post(f"/vendas/{v4}/cancelar", headers=auth_admin)
    return {"a": a, "b": b, "c": c}


def test_totais_do_periodo(client, auth_admin, cenario):
    corpo = client.get(URL, params=PERIODO, headers=auth_admin).json()

    assert corpo["quantidade_vendas"] == 3
    assert corpo["total_vendido"] == "37.00"
    assert corpo["ticket_medio"] == "12.33"  # 37,00 / 3 = 12,333...
    assert corpo["quantidade_canceladas"] == 1


def test_total_por_forma_desconta_troco_e_ignora_cancelada(client, auth_admin, cenario):
    corpo = client.get(URL, params=PERIODO, headers=auth_admin).json()

    assert corpo["total_por_forma"] == {
        "dinheiro": "15.00",  # 20,00 recebidos - 5,00 de troco
        "pix": "10.00",
        "debito": "12.00",
        "credito": "0.00",  # a única venda no crédito foi cancelada
    }


def test_produtos_mais_vendidos(client, auth_admin, cenario):
    corpo = client.get(URL, params=PERIODO, headers=auth_admin).json()

    ranking = [(p["nome"], p["quantidade"], p["total"]) for p in corpo["produtos_mais_vendidos"]]
    assert ranking == [
        ("Produto A", 7, "14.00"),
        ("Produto C", 2, "20.00"),
        ("Produto B", 1, "5.00"),  # as 10 unidades da venda cancelada não contam
    ]


def test_limite_de_produtos(client, auth_admin, cenario):
    params = {**PERIODO, "limite_produtos": 1}
    corpo = client.get(URL, params=params, headers=auth_admin).json()

    assert [p["nome"] for p in corpo["produtos_mais_vendidos"]] == ["Produto A"]


def test_vendas_por_dia_no_fuso_local_com_dias_zerados(client, auth_admin, cenario):
    corpo = client.get(URL, params=PERIODO, headers=auth_admin).json()

    assert corpo["vendas_por_dia"] == [
        {"data": "2026-11-03", "quantidade_vendas": 2, "total": "25.00"},  # inclui a das 23:30
        {"data": "2026-11-04", "quantidade_vendas": 0, "total": "0.00"},
        {"data": "2026-11-05", "quantidade_vendas": 1, "total": "12.00"},
        {"data": "2026-11-06", "quantidade_vendas": 0, "total": "0.00"},
    ]


def test_periodo_sem_vendas_retorna_zeros(client, auth_admin):
    params = {"inicio": "2026-01-01", "fim": "2026-01-01"}
    corpo = client.get(URL, params=params, headers=auth_admin).json()

    assert corpo["quantidade_vendas"] == 0
    assert corpo["total_vendido"] == "0.00"
    assert corpo["ticket_medio"] == "0.00"
    assert corpo["produtos_mais_vendidos"] == []
    assert corpo["total_por_forma"]["dinheiro"] == "0.00"


def test_operador_nao_acessa_relatorios(client, auth_operador):
    assert client.get(URL, params=PERIODO, headers=auth_operador).status_code == 403


@pytest.mark.parametrize(
    "params",
    [
        {"inicio": "2026-11-06", "fim": "2026-11-03"},  # início depois do fim
        {"inicio": "2025-01-01", "fim": "2026-12-31"},  # mais de 366 dias
    ],
)
def test_periodo_invalido(client, auth_admin, params):
    assert client.get(URL, params=params, headers=auth_admin).status_code == 422


def test_datas_sao_obrigatorias(client, auth_admin):
    assert client.get(URL, headers=auth_admin).status_code == 422
