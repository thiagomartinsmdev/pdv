"""Testes de login e controle de acesso por perfil."""

from tests.conftest import SENHA_PADRAO


def test_login_com_sucesso(client, admin):
    resposta = client.post("/auth/login", json={"email": "ADMIN@teste.com", "senha": SENHA_PADRAO})

    assert resposta.status_code == 200
    token = resposta.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["email"] == "admin@teste.com"
    assert me.json()["perfil"] == "admin"


def test_login_com_senha_errada(client, admin):
    resposta = client.post("/auth/login", json={"email": "admin@teste.com", "senha": "errada"})

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha inválidos."


def test_rota_protegida_sem_token(client):
    assert client.get("/auth/me").status_code == 401


def test_token_invalido(client):
    resposta = client.get("/auth/me", headers={"Authorization": "Bearer abc.def.ghi"})

    assert resposta.status_code == 401


def test_usuario_desativado_perde_acesso_na_hora(client, db, operador, auth_operador):
    operador.ativo = False
    db.commit()

    assert client.get("/auth/me", headers=auth_operador).status_code == 401


def test_operador_nao_gerencia_produtos(client, auth_operador):
    resposta = client.post(
        "/produtos",
        json={"nome": "Bala", "codigo_barras": "1", "preco": "0.10"},
        headers=auth_operador,
    )

    assert resposta.status_code == 403


def test_operador_nao_gerencia_usuarios(client, auth_operador):
    assert client.get("/usuarios", headers=auth_operador).status_code == 403
