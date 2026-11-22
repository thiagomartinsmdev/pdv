"""Testes de cancelamento de venda."""

from sqlalchemy import func

from app.models import SessaoCaixa, StatusVenda, Venda


def registrar_venda(client, headers, produto_id: int, quantidade: int, valor: str) -> int:
    resposta = client.post(
        "/vendas",
        json={
            "itens": [{"produto_id": produto_id, "quantidade": quantidade}],
            "pagamentos": [{"forma": "dinheiro", "valor": valor}],
        },
        headers=headers,
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()["id"]


def test_cancelamento_devolve_itens_ao_estoque(
    client, db, auth_admin, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto(preco="4.00", estoque=10)
    venda_id = registrar_venda(client, auth_operador, produto.id, 3, "12.00")
    db.refresh(produto)
    assert produto.quantidade_estoque == 7

    resposta = client.post(f"/vendas/{venda_id}/cancelar", headers=auth_admin)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "cancelada"
    db.refresh(produto)
    assert produto.quantidade_estoque == 10


def test_operador_nao_pode_cancelar_venda(client, db, auth_operador, caixa_operador, criar_produto):
    produto = criar_produto(preco="4.00", estoque=10)
    venda_id = registrar_venda(client, auth_operador, produto.id, 3, "12.00")

    resposta = client.post(f"/vendas/{venda_id}/cancelar", headers=auth_operador)

    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Apenas administradores podem realizar esta ação."
    venda = db.get(Venda, venda_id)
    assert venda.status == StatusVenda.CONCLUIDA
    db.refresh(produto)
    assert produto.quantidade_estoque == 7


def test_venda_nao_pode_ser_cancelada_duas_vezes(
    client, db, auth_admin, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto(preco="4.00", estoque=10)
    venda_id = registrar_venda(client, auth_operador, produto.id, 3, "12.00")
    client.post(f"/vendas/{venda_id}/cancelar", headers=auth_admin)

    resposta = client.post(f"/vendas/{venda_id}/cancelar", headers=auth_admin)

    assert resposta.status_code == 409
    db.refresh(produto)
    assert produto.quantidade_estoque == 10  # não devolveu em dobro


def test_nao_cancela_venda_de_caixa_fechado(
    client, db, auth_admin, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto(preco="4.00", estoque=10)
    venda_id = registrar_venda(client, auth_operador, produto.id, 1, "4.00")
    sessao = db.get(SessaoCaixa, caixa_operador.id)
    sessao.fechado_em = func.now()
    db.commit()

    resposta = client.post(f"/vendas/{venda_id}/cancelar", headers=auth_admin)

    assert resposta.status_code == 422
    assert "caixa já fechado" in resposta.json()["detail"]
    db.refresh(produto)
    assert produto.quantidade_estoque == 9


def test_cancelar_venda_inexistente(client, auth_admin):
    assert client.post("/vendas/999/cancelar", headers=auth_admin).status_code == 404
