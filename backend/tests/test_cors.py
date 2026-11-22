"""O navegador só deixa o frontend chamar a API se ela autorizar a origem (CORS)."""


def preflight(client, origem: str):
    # Antes de um POST com JSON, o navegador envia um OPTIONS perguntando se pode.
    return client.options(
        "/auth/login",
        headers={
            "Origin": origem,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


def test_frontend_autorizado(client):
    resposta = preflight(client, "http://localhost:5173")

    assert resposta.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_origem_desconhecida_nao_e_autorizada(client):
    resposta = preflight(client, "http://site-malicioso.com")

    assert "access-control-allow-origin" not in resposta.headers
