"""Testes de registro de venda, pagamento e troco."""

import threading
from decimal import Decimal

from sqlalchemy import func, select

from app.core.exceptions import RegraNegocio
from app.models import ItemVenda, Venda
from app.schemas.venda import VendaCriar
from app.services import venda_service


def venda(itens: list[tuple[int, int]], pagamentos: list[tuple[str, str]], desconto: str = "0"):
    """Monta o JSON de uma venda: itens=[(produto_id, qtd)], pagamentos=[(forma, valor)]."""
    return {
        "itens": [{"produto_id": p, "quantidade": q} for p, q in itens],
        "pagamentos": [{"forma": f, "valor": v} for f, v in pagamentos],
        "desconto": desconto,
    }


def contar_vendas(db) -> int:
    return db.scalar(select(func.count(Venda.id)))


# ---------- Venda com sucesso ----------


def test_venda_com_sucesso_baixa_estoque_e_salva_itens(
    client, db, auth_operador, caixa_operador, criar_produto
):
    pao = criar_produto("Pão francês", preco="0.90", estoque=100)
    leite = criar_produto("Leite 1L", preco="5.29", estoque=10)

    resposta = client.post(
        "/vendas",
        json=venda([(pao.id, 10), (leite.id, 2)], [("pix", "19.58")]),
        headers=auth_operador,
    )

    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["subtotal"] == "19.58"  # 10 x 0,90 + 2 x 5,29
    assert corpo["total"] == "19.58"
    assert corpo["status"] == "concluida"
    assert corpo["sessao_caixa_id"] == caixa_operador.id
    assert len(corpo["itens"]) == 2

    db.refresh(pao)
    db.refresh(leite)
    assert pao.quantidade_estoque == 90
    assert leite.quantidade_estoque == 8


def test_venda_aplica_desconto(client, auth_operador, caixa_operador, criar_produto):
    produto = criar_produto(preco="10.00")

    resposta = client.post(
        "/vendas",
        json=venda([(produto.id, 3)], [("debito", "27.50")], desconto="2.50"),
        headers=auth_operador,
    )

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["subtotal"] == "30.00"
    assert resposta.json()["desconto"] == "2.50"
    assert resposta.json()["total"] == "27.50"


def test_mesmo_produto_repetido_vira_um_item_so(
    client, db, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto(preco="1.50", estoque=10)

    resposta = client.post(
        "/vendas",
        json=venda([(produto.id, 1), (produto.id, 2)], [("pix", "4.50")]),
        headers=auth_operador,
    )

    assert resposta.status_code == 201, resposta.text
    itens = resposta.json()["itens"]
    assert len(itens) == 1
    assert itens[0]["quantidade"] == 3
    db.refresh(produto)
    assert produto.quantidade_estoque == 7


def test_preco_do_item_nao_muda_quando_produto_muda_de_preco(
    client, db, auth_operador, auth_admin, caixa_operador, criar_produto
):
    produto = criar_produto(preco="8.00")
    venda_id = client.post(
        "/vendas", json=venda([(produto.id, 1)], [("pix", "8.00")]), headers=auth_operador
    ).json()["id"]

    client.patch(f"/produtos/{produto.id}", json={"preco": "12.00"}, headers=auth_admin)

    item = db.scalar(select(ItemVenda).where(ItemVenda.venda_id == venda_id))
    assert item.preco_unitario == Decimal("8.00")
    assert client.get(f"/vendas/{venda_id}", headers=auth_admin).json()["total"] == "8.00"


# ---------- Caixa ----------


def test_venda_sem_caixa_aberto_e_recusada(client, db, auth_operador, criar_produto):
    produto = criar_produto(estoque=5)

    resposta = client.post(
        "/vendas", json=venda([(produto.id, 1)], [("pix", "10.00")]), headers=auth_operador
    )

    assert resposta.status_code == 422
    assert "caixa aberto" in resposta.json()["detail"]
    db.refresh(produto)
    assert produto.quantidade_estoque == 5


# ---------- Estoque ----------


def test_venda_sem_estoque_informa_o_produto(
    client, db, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto("Croissant", estoque=2)

    resposta = client.post(
        "/vendas", json=venda([(produto.id, 3)], [("pix", "30.00")]), headers=auth_operador
    )

    assert resposta.status_code == 422
    assert (
        resposta.json()["detail"] == "Estoque insuficiente: Croissant (disponível: 2, pedido: 3)."
    )
    db.refresh(produto)
    assert produto.quantidade_estoque == 2
    assert contar_vendas(db) == 0


def test_venda_e_tudo_ou_nada(client, db, auth_operador, caixa_operador, criar_produto):
    """Se um item não tem estoque, nenhum outro item da venda pode ter baixa."""
    com_estoque = criar_produto("Café", estoque=10)
    sem_estoque = criar_produto("Manteiga", estoque=0)

    resposta = client.post(
        "/vendas",
        json=venda([(com_estoque.id, 1), (sem_estoque.id, 1)], [("pix", "20.00")]),
        headers=auth_operador,
    )

    assert resposta.status_code == 422
    assert "Manteiga" in resposta.json()["detail"]
    db.refresh(com_estoque)
    assert com_estoque.quantidade_estoque == 10
    assert contar_vendas(db) == 0


def test_produto_inativo_nao_pode_ser_vendido(
    client, db, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto("Sonho")
    produto.ativo = False
    db.commit()

    resposta = client.post(
        "/vendas", json=venda([(produto.id, 1)], [("pix", "10.00")]), headers=auth_operador
    )

    assert resposta.status_code == 422
    assert "inativo" in resposta.json()["detail"]


def test_venda_simultanea_do_ultimo_item(
    fabrica_sessao, db, criar_usuario, abrir_caixa, criar_produto
):
    """Dois caixas tentam vender o último item ao mesmo tempo: só um pode conseguir.

    Sem o with_for_update(), os dois leriam estoque = 1, os dois venderiam e o
    estoque terminaria em 0 com 2 unidades vendidas.
    """
    produto = criar_produto("Bolo", estoque=1)
    operadores = [criar_usuario(f"op{i}@teste.com") for i in (1, 2)]
    for operador in operadores:
        abrir_caixa(operador)
    dados = VendaCriar.model_validate(venda([(produto.id, 1)], [("pix", "10.00")]))

    resultados: list[str] = []
    largada = threading.Barrier(2)

    def vender(usuario_id: int) -> None:
        with fabrica_sessao() as sessao:
            usuario = sessao.get(type(operadores[0]), usuario_id)
            largada.wait()  # os dois começam juntos
            try:
                venda_service.registrar(sessao, usuario, dados)
                resultados.append("vendeu")
            except RegraNegocio:
                resultados.append("sem estoque")

    threads = [threading.Thread(target=vender, args=(op.id,)) for op in operadores]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)

    assert sorted(resultados) == ["sem estoque", "vendeu"]
    db.refresh(produto)
    assert produto.quantidade_estoque == 0
    assert contar_vendas(db) == 1


# ---------- Pagamento e troco ----------


def test_calculo_de_troco_em_dinheiro(client, auth_operador, caixa_operador, criar_produto):
    produto = criar_produto(preco="7.35")

    resposta = client.post(
        "/vendas", json=venda([(produto.id, 2)], [("dinheiro", "20.00")]), headers=auth_operador
    )

    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["total"] == "14.70"
    assert corpo["troco"] == "5.30"
    assert corpo["pagamentos"] == [{"forma": "dinheiro", "valor": "20.00", "troco": "5.30"}]


def test_pagamento_misto_troco_fica_no_dinheiro(
    client, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto(preco="50.00")

    resposta = client.post(
        "/vendas",
        json=venda([(produto.id, 1)], [("credito", "30.00"), ("dinheiro", "50.00")]),
        headers=auth_operador,
    )

    assert resposta.status_code == 201, resposta.text
    pagamentos = {p["forma"]: p for p in resposta.json()["pagamentos"]}
    assert pagamentos["credito"]["troco"] == "0.00"
    assert pagamentos["dinheiro"]["troco"] == "30.00"
    assert resposta.json()["troco"] == "30.00"


def test_pagamento_exato_nao_tem_troco(client, auth_operador, caixa_operador, criar_produto):
    produto = criar_produto(preco="10.00")

    resposta = client.post(
        "/vendas", json=venda([(produto.id, 1)], [("dinheiro", "10.00")]), headers=auth_operador
    )

    assert resposta.json()["troco"] == "0.00"


def test_pagamento_insuficiente_e_recusado(
    client, db, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto(preco="25.00", estoque=5)

    resposta = client.post(
        "/vendas",
        json=venda([(produto.id, 1)], [("dinheiro", "10.00"), ("pix", "5.00")]),
        headers=auth_operador,
    )

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == (
        "Pagamento insuficiente: total R$ 25,00, pago R$ 15,00, faltam R$ 10,00."
    )
    db.refresh(produto)
    assert produto.quantidade_estoque == 5
    assert contar_vendas(db) == 0


def test_pix_acima_do_total_e_recusado(client, auth_operador, caixa_operador, criar_produto):
    """Não existe troco em PIX/cartão."""
    produto = criar_produto(preco="10.00")

    resposta = client.post(
        "/vendas", json=venda([(produto.id, 1)], [("pix", "15.00")]), headers=auth_operador
    )

    assert resposta.status_code == 422
    assert "Só existe troco para pagamento em dinheiro" in resposta.json()["detail"]


def test_desconto_maior_ou_igual_ao_subtotal_e_recusado(
    client, auth_operador, caixa_operador, criar_produto
):
    produto = criar_produto(preco="10.00")

    resposta = client.post(
        "/vendas",
        json=venda([(produto.id, 1)], [("pix", "1.00")], desconto="10.00"),
        headers=auth_operador,
    )

    assert resposta.status_code == 422
    assert "desconto" in resposta.json()["detail"]


# ---------- Consulta ----------


def test_operador_so_ve_as_proprias_vendas(
    client, criar_usuario, abrir_caixa, auth_operador, caixa_operador, auth_admin, criar_produto
):
    from tests.conftest import cabecalho

    produto = criar_produto(estoque=10)
    outro = criar_usuario("outro@teste.com")
    abrir_caixa(outro)
    corpo = venda([(produto.id, 1)], [("pix", "10.00")])
    minha = client.post("/vendas", json=corpo, headers=auth_operador).json()["id"]
    alheia = client.post("/vendas", json=corpo, headers=cabecalho(outro)).json()["id"]

    ids_operador = [v["id"] for v in client.get("/vendas", headers=auth_operador).json()]
    ids_admin = [v["id"] for v in client.get("/vendas", headers=auth_admin).json()]

    assert ids_operador == [minha]
    assert sorted(ids_admin) == sorted([minha, alheia])
    assert client.get(f"/vendas/{alheia}", headers=auth_operador).status_code == 403


def test_filtro_por_periodo(client, db, auth_admin, admin, abrir_caixa, criar_produto):
    from datetime import datetime

    from app.core.datas import FUSO

    produto = criar_produto(estoque=10)
    abrir_caixa(admin)
    corpo = venda([(produto.id, 1)], [("pix", "10.00")])
    ids = [client.post("/vendas", json=corpo, headers=auth_admin).json()["id"] for _ in range(2)]
    # 23h do dia 04/11 no horário de Brasília (já é dia 05 em UTC) e 10h do dia 05/11.
    db.get(Venda, ids[0]).data_hora = datetime(2026, 11, 4, 23, 0, tzinfo=FUSO)
    db.get(Venda, ids[1]).data_hora = datetime(2026, 11, 5, 10, 0, tzinfo=FUSO)
    db.commit()

    def buscar(**params):
        return [v["id"] for v in client.get("/vendas", params=params, headers=auth_admin).json()]

    assert buscar(inicio="2026-11-04", fim="2026-11-04") == [ids[0]]
    assert buscar(inicio="2026-11-05", fim="2026-11-05") == [ids[1]]
    assert buscar(inicio="2026-11-04", fim="2026-11-05") == [ids[1], ids[0]]
    resposta = client.get(
        "/vendas", params={"inicio": "2026-11-06", "fim": "2026-11-05"}, headers=auth_admin
    )
    assert resposta.status_code == 422
