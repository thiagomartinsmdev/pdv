"""Testes de abertura e fechamento de caixa."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import SessaoCaixa


def test_abrir_caixa(client, auth_operador):
    resposta = client.post("/caixa/abrir", json={"valor_abertura": "150.00"}, headers=auth_operador)

    assert resposta.status_code == 201
    assert resposta.json()["resumo"]["valor_esperado_dinheiro"] == "150.00"
    assert client.get("/caixa/atual", headers=auth_operador).json()["id"] == resposta.json()["id"]


def test_sem_caixa_aberto_atual_retorna_null(client, auth_operador):
    resposta = client.get("/caixa/atual", headers=auth_operador)

    assert resposta.status_code == 200
    assert resposta.json() is None


def test_nao_abre_dois_caixas_para_o_mesmo_usuario(client, auth_operador, caixa_operador):
    resposta = client.post("/caixa/abrir", json={"valor_abertura": "10.00"}, headers=auth_operador)

    assert resposta.status_code == 409


def test_banco_impede_dois_caixas_abertos(db, operador, caixa_operador):
    """O índice único parcial protege a regra mesmo se o código for contornado."""
    db.add(SessaoCaixa(usuario_id=operador.id, valor_abertura=0))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_fechamento_calcula_esperado_e_diferenca(
    client, auth_operador, auth_admin, caixa_operador, criar_produto
):
    """Abertura 100. Vendas: 20 (pago 50 em dinheiro, troco 30), 10 no PIX e 15
    cancelada. Esperado em dinheiro: 100 + 50 - 30 = 120. Contado: 118 -> falta 2."""
    produto = criar_produto(preco="5.00", estoque=20)

    def vender(qtd: int, forma: str, valor: str) -> int:
        corpo = {
            "itens": [{"produto_id": produto.id, "quantidade": qtd}],
            "pagamentos": [{"forma": forma, "valor": valor}],
        }
        return client.post("/vendas", json=corpo, headers=auth_operador).json()["id"]

    vender(4, "dinheiro", "50.00")
    vender(2, "pix", "10.00")
    cancelada = vender(3, "dinheiro", "15.00")
    client.post(f"/vendas/{cancelada}/cancelar", headers=auth_admin)

    resposta = client.post(
        "/caixa/fechar", json={"valor_informado": "118.00"}, headers=auth_operador
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["resumo"]["quantidade_vendas"] == 2
    assert corpo["resumo"]["total_vendido"] == "30.00"
    assert corpo["resumo"]["total_por_forma"] == {
        "dinheiro": "20.00",
        "pix": "10.00",
        "debito": "0.00",
        "credito": "0.00",
    }
    assert corpo["resumo"]["valor_esperado_dinheiro"] == "120.00"
    assert corpo["diferenca"] == "-2.00"
    assert corpo["fechado_em"] is not None
    assert client.get("/caixa/atual", headers=auth_operador).json() is None


def test_venda_depois_do_fechamento_e_recusada(
    client, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto()
    client.post("/caixa/fechar", json={"valor_informado": "100.00"}, headers=auth_operador)

    resposta = client.post(
        "/vendas",
        json={
            "itens": [{"produto_id": produto.id, "quantidade": 1}],
            "pagamentos": [{"forma": "pix", "valor": "10.00"}],
        },
        headers=auth_operador,
    )

    assert resposta.status_code == 422
