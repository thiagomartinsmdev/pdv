"""Testes de categorias."""

from app.models import Categoria


def test_lista_categorias_ativas_na_ordem_das_abas(client, auth_operador, criar_categoria):
    criar_categoria("Bebidas", ordem=20)
    criar_categoria("Pães", ordem=10)
    criar_categoria("Antigas", ordem=0, ativo=False)

    resposta = client.get("/categorias", headers=auth_operador)

    assert resposta.status_code == 200
    assert [c["nome"] for c in resposta.json()] == ["Pães", "Bebidas"]


def test_admin_pode_ver_inativas_e_operador_nao(client, auth_admin, auth_operador, criar_categoria):
    criar_categoria("Pães")
    criar_categoria("Antigas", ativo=False)
    params = {"incluir_inativas": True}

    nomes_admin = [
        c["nome"] for c in client.get("/categorias", params=params, headers=auth_admin).json()
    ]
    nomes_operador = [
        c["nome"] for c in client.get("/categorias", params=params, headers=auth_operador).json()
    ]

    assert sorted(nomes_admin) == ["Antigas", "Pães"]
    assert nomes_operador == ["Pães"]


def test_admin_cria_edita_e_desativa(client, db, auth_admin):
    criada = client.post("/categorias", json={"nome": "  Doces ", "ordem": 30}, headers=auth_admin)
    assert criada.status_code == 201
    assert criada.json() == {"id": criada.json()["id"], "nome": "Doces", "ordem": 30, "ativo": True}
    categoria_id = criada.json()["id"]

    editada = client.patch(f"/categorias/{categoria_id}", json={"ordem": 5}, headers=auth_admin)
    assert editada.json()["ordem"] == 5

    assert client.delete(f"/categorias/{categoria_id}", headers=auth_admin).status_code == 204
    assert db.get(Categoria, categoria_id).ativo is False


def test_nome_repetido_sem_diferenciar_maiusculas(client, auth_admin, criar_categoria):
    criar_categoria("Bebidas")

    resposta = client.post("/categorias", json={"nome": "BEBIDAS"}, headers=auth_admin)

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Já existe a categoria 'Bebidas'."


def test_operador_nao_gerencia_categorias(client, auth_operador, criar_categoria):
    categoria = criar_categoria("Pães")

    assert (
        client.post("/categorias", json={"nome": "Doces"}, headers=auth_operador).status_code == 403
    )
    assert (
        client.patch(
            f"/categorias/{categoria.id}", json={"ordem": 1}, headers=auth_operador
        ).status_code
        == 403
    )
    assert client.delete(f"/categorias/{categoria.id}", headers=auth_operador).status_code == 403


def test_categoria_inexistente(client, auth_admin):
    assert client.patch("/categorias/999", json={"ordem": 1}, headers=auth_admin).status_code == 404
