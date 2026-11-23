"""Testes de produtos: categoria, imagem, filtro e mais vendidos."""

from datetime import UTC, datetime, timedelta

import pytest

from app.models import Venda


def novo_produto(**extras):
    return {"nome": "Bolo de cenoura", "codigo_barras": "123", "preco": "5.00", **extras}


# ---------- Categoria e imagem no cadastro ----------


def test_produto_devolve_categoria_e_imagem(client, auth_admin, criar_categoria):
    doces = criar_categoria("Doces")
    url = "https://exemplo.com/bolo.jpg"

    resposta = client.post(
        "/produtos", json=novo_produto(categoria_id=doces.id, imagem_url=url), headers=auth_admin
    )

    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["categoria_id"] == doces.id
    assert corpo["categoria"] == {"id": doces.id, "nome": "Doces"}
    assert corpo["imagem_url"] == url


def test_produto_sem_categoria_e_sem_imagem(client, auth_admin):
    corpo = client.post("/produtos", json=novo_produto(), headers=auth_admin).json()

    assert corpo["categoria"] is None
    assert corpo["imagem_url"] is None


@pytest.mark.parametrize(
    "url",
    ["javascript:alert(1)", "ftp://exemplo.com/a.jpg", "exemplo.com/a.jpg", "https://" + "a" * 500],
)
def test_link_de_imagem_invalido_e_recusado(client, auth_admin, url):
    resposta = client.post("/produtos", json=novo_produto(imagem_url=url), headers=auth_admin)

    assert resposta.status_code == 422


def test_categoria_inexistente_ou_inativa_e_recusada(client, auth_admin, criar_categoria):
    inativa = criar_categoria("Antigas", ativo=False)

    inexistente = client.post("/produtos", json=novo_produto(categoria_id=999), headers=auth_admin)
    desativada = client.post(
        "/produtos", json=novo_produto(categoria_id=inativa.id), headers=auth_admin
    )

    assert inexistente.status_code == 404
    assert desativada.status_code == 422
    assert "desativada" in desativada.json()["detail"]


def test_patch_troca_e_remove_categoria_e_imagem(
    client, auth_admin, criar_categoria, criar_produto
):
    paes, doces = criar_categoria("Pães"), criar_categoria("Doces")
    produto = criar_produto(categoria=paes, imagem_url="https://exemplo.com/a.jpg")

    trocada = client.patch(
        f"/produtos/{produto.id}", json={"categoria_id": doces.id}, headers=auth_admin
    )
    assert trocada.json()["categoria"]["nome"] == "Doces"

    # "" no link (campo apagado no formulário) e null na categoria limpam os dois.
    limpa = client.patch(
        f"/produtos/{produto.id}", json={"categoria_id": None, "imagem_url": ""}, headers=auth_admin
    )
    assert limpa.json()["categoria"] is None
    assert limpa.json()["imagem_url"] is None


def test_produto_de_categoria_desativada_continua_editavel(
    client, db, auth_admin, criar_categoria, criar_produto
):
    """Desativar a categoria não pode travar a edição dos produtos ligados a ela."""
    categoria = criar_categoria("Sazonais")
    produto = criar_produto(categoria=categoria)
    categoria.ativo = False
    db.commit()

    resposta = client.patch(
        f"/produtos/{produto.id}",
        json={"preco": "6.00", "categoria_id": categoria.id},
        headers=auth_admin,
    )

    assert resposta.status_code == 200, resposta.text


# ---------- Filtro por categoria ----------


def test_filtro_por_categoria(client, auth_operador, criar_categoria, criar_produto):
    paes, bebidas = criar_categoria("Pães"), criar_categoria("Bebidas")
    criar_produto("Pão francês", categoria=paes)
    criar_produto("Baguete", categoria=paes)
    criar_produto("Suco", categoria=bebidas)
    criar_produto("Sem categoria")

    resposta = client.get("/produtos", params={"categoria_id": paes.id}, headers=auth_operador)

    assert [p["nome"] for p in resposta.json()] == ["Baguete", "Pão francês"]


def test_listagem_nao_faz_uma_consulta_por_produto(
    client, engine, auth_operador, criar_categoria, criar_produto
):
    """A categoria é carregada em lote: o número de consultas não cresce (sem N+1)."""
    from sqlalchemy import event

    categorias = [criar_categoria(f"Categoria {i}") for i in range(5)]

    def consultas() -> int:
        contador = {"total": 0}

        def contar(*_args) -> None:
            contador["total"] += 1

        event.listen(engine, "before_cursor_execute", contar)
        try:
            assert client.get("/produtos", headers=auth_operador).status_code == 200
        finally:
            event.remove(engine, "before_cursor_execute", contar)
        return contador["total"]

    criar_produto("Produto 0", categoria=categorias[0])
    com_um = consultas()
    for i, categoria in enumerate(categorias[1:], start=1):
        criar_produto(f"Produto {i}", categoria=categoria)

    assert consultas() == com_um


# ---------- Mais vendidos ----------


def vender(client, headers, itens) -> int:
    corpo = {
        "itens": [{"produto_id": p.id, "quantidade": q} for p, q in itens],
        "pagamentos": [{"forma": "dinheiro", "valor": "99999.00"}],  # cobre qualquer total
    }
    resposta = client.post("/vendas", json=corpo, headers=headers)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()["id"]


def test_mais_vendidos_dos_ultimos_30_dias(
    client, db, auth_admin, admin, abrir_caixa, criar_produto, criar_categoria
):
    abrir_caixa(admin)
    paes = criar_categoria("Pães")
    pao = criar_produto("Pão francês", preco="1.00", estoque=1000, categoria=paes)
    leite = criar_produto("Leite", preco="5.00", estoque=1000)
    cafe = criar_produto("Café", preco="20.00", estoque=1000)
    bolo = criar_produto("Bolo", preco="8.00", estoque=1000)
    desativado = criar_produto("Antigo", estoque=1000)

    vender(client, auth_admin, [(pao, 10), (leite, 3)])
    vender(client, auth_admin, [(leite, 2), (cafe, 1), (desativado, 50)])
    # Venda cancelada não conta.
    cancelada = vender(client, auth_admin, [(bolo, 40)])
    client.post(f"/vendas/{cancelada}/cancelar", headers=auth_admin)
    # Venda de 31 dias atrás não conta.
    antiga = vender(client, auth_admin, [(cafe, 100)])
    db.get(Venda, antiga).data_hora = datetime.now(UTC) - timedelta(days=31)
    desativado.ativo = False
    db.commit()

    resposta = client.get("/produtos/mais-vendidos", headers=auth_admin)

    assert resposta.status_code == 200
    ranking = [p["nome"] for p in resposta.json()]
    assert ranking == ["Pão francês", "Leite", "Café"]  # 10, 5 e 1 unidade(s)
    assert resposta.json()[0]["categoria"]["nome"] == "Pães"


def test_mais_vendidos_respeita_limite_e_operador_acessa(
    client, auth_operador, caixa_operador, criar_produto
):
    produtos = [criar_produto(f"P{i}", estoque=100) for i in range(3)]
    vender(client, auth_operador, [(produtos[0], 3), (produtos[1], 2), (produtos[2], 1)])

    resposta = client.get("/produtos/mais-vendidos", params={"limite": 2}, headers=auth_operador)

    assert resposta.status_code == 200
    assert [p["nome"] for p in resposta.json()] == ["P0", "P1"]


def test_mais_vendidos_sem_vendas(client, auth_operador):
    assert client.get("/produtos/mais-vendidos", headers=auth_operador).json() == []
