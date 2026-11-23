"""Testes do upload de fotos de produto."""

from pathlib import Path

import pytest

from app.core.config import settings
from app.services import imagem_service

# Conteúdos mínimos com a assinatura real de cada formato (os primeiros bytes).
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 200
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
WEBP = b"RIFF" + (212).to_bytes(4, "little") + b"WEBPVP8 " + b"\x00" * 200
GIF = b"GIF89a" + b"\x00" * 200
TEXTO = b"isto nao e uma imagem"


def enviar(client, headers, produto_id, conteudo, nome="foto.jpg", tipo="image/jpeg"):
    return client.post(
        f"/produtos/{produto_id}/imagem",
        files={"arquivo": (nome, conteudo, tipo)},
        headers=headers,
    )


def arquivo_da_url(url: str) -> Path:
    return imagem_service.caminho_local(url)


# ---------- Envio ----------


@pytest.mark.parametrize(
    ("conteudo", "extensao", "tipo"),
    [(JPG, "jpg", "image/jpeg"), (PNG, "png", "image/png"), (WEBP, "webp", "image/webp")],
)
def test_envia_foto_valida(client, auth_admin, criar_produto, conteudo, extensao, tipo):
    produto = criar_produto()

    resposta = enviar(client, auth_admin, produto.id, conteudo)

    assert resposta.status_code == 200, resposta.text
    url = resposta.json()["imagem_url"]
    assert url.startswith("/uploads/produtos/") and url.endswith(f".{extensao}")
    assert arquivo_da_url(url).read_bytes() == conteudo

    # A rota estática serve o arquivo, com o tipo correto e o cabeçalho nosniff.
    servida = client.get(url)
    assert servida.status_code == 200
    assert servida.headers["content-type"] == tipo
    assert servida.headers["x-content-type-options"] == "nosniff"
    assert servida.content == conteudo


def test_extensao_vem_do_conteudo_e_nao_do_nome(client, auth_admin, criar_produto):
    """Um PNG enviado com nome .jpg é salvo como .png (o nome do usuário não é usado)."""
    produto = criar_produto()

    url = enviar(client, auth_admin, produto.id, PNG, nome="../../segredo.jpg").json()["imagem_url"]

    assert url.endswith(".png")
    assert "segredo" not in url


@pytest.mark.parametrize(
    ("conteudo", "nome"),
    [(GIF, "animacao.gif"), (TEXTO, "falsa.jpg"), (b"", "vazia.jpg")],
)
def test_tipo_invalido_e_recusado(client, auth_admin, criar_produto, conteudo, nome):
    produto = criar_produto()

    resposta = enviar(client, auth_admin, produto.id, conteudo, nome=nome)

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "O arquivo não é uma imagem JPG, PNG ou WebP válida."
    assert list(imagem_service.pasta_produtos().iterdir()) == []


def test_arquivo_maior_que_2mb_e_recusado(client, auth_admin, criar_produto):
    produto = criar_produto()
    grande = JPG + b"\x00" * settings.tamanho_maximo_imagem  # passa do limite

    resposta = enviar(client, auth_admin, produto.id, grande)

    assert resposta.status_code == 413
    assert "2 MB" in resposta.json()["detail"]
    assert list(imagem_service.pasta_produtos().iterdir()) == []


def test_operador_nao_envia_foto(client, auth_operador, criar_produto):
    produto = criar_produto()

    assert enviar(client, auth_operador, produto.id, JPG).status_code == 403


def test_produto_inexistente(client, auth_admin):
    assert enviar(client, auth_admin, 999, JPG).status_code == 404
    assert list(imagem_service.pasta_produtos().iterdir()) == []


# ---------- Troca e remoção apagam a foto antiga ----------


def test_trocar_foto_apaga_o_arquivo_antigo(client, auth_admin, criar_produto):
    produto = criar_produto()
    antiga = arquivo_da_url(enviar(client, auth_admin, produto.id, JPG).json()["imagem_url"])

    nova_url = enviar(client, auth_admin, produto.id, PNG).json()["imagem_url"]

    assert not antiga.exists()
    assert arquivo_da_url(nova_url).exists()


def test_remover_foto_apaga_o_arquivo(client, auth_admin, criar_produto):
    produto = criar_produto()
    arquivo = arquivo_da_url(enviar(client, auth_admin, produto.id, JPG).json()["imagem_url"])

    resposta = client.delete(f"/produtos/{produto.id}/imagem", headers=auth_admin)

    assert resposta.status_code == 200
    assert resposta.json()["imagem_url"] is None
    assert not arquivo.exists()


def test_trocar_foto_local_por_link_apaga_o_arquivo(client, auth_admin, criar_produto):
    produto = criar_produto()
    arquivo = arquivo_da_url(enviar(client, auth_admin, produto.id, JPG).json()["imagem_url"])

    resposta = client.patch(
        f"/produtos/{produto.id}",
        json={"imagem_url": "https://exemplo.com/foto.jpg"},
        headers=auth_admin,
    )

    assert resposta.json()["imagem_url"] == "https://exemplo.com/foto.jpg"
    assert not arquivo.exists()


def test_editar_produto_reenviando_a_mesma_foto_local(client, auth_admin, criar_produto):
    """O formulário reenvia o imagem_url atual: isso não pode apagar nem recusar a foto."""
    produto = criar_produto()
    url = enviar(client, auth_admin, produto.id, JPG).json()["imagem_url"]

    resposta = client.patch(
        f"/produtos/{produto.id}", json={"preco": "12.00", "imagem_url": url}, headers=auth_admin
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["imagem_url"] == url
    assert arquivo_da_url(url).exists()


def test_nao_aceita_outro_caminho_local_pelo_formulario(client, auth_admin, criar_produto):
    """Fotos do servidor só entram pelo upload: o PATCH não pode apontar para o arquivo
    de outro produto (o que faria a remoção de um apagar a foto do outro)."""
    dono, outro = criar_produto("Dono"), criar_produto("Outro")
    url = enviar(client, auth_admin, dono.id, JPG).json()["imagem_url"]

    resposta = client.patch(f"/produtos/{outro.id}", json={"imagem_url": url}, headers=auth_admin)

    assert resposta.status_code == 422
    assert "envie o arquivo pelo upload" in resposta.json()["detail"]


def test_arquivo_em_uso_por_outro_produto_nao_e_apagado(db, criar_produto):
    """Arquivos compartilhados (o importador em lote reaproveita fotos iguais) só são
    apagados quando nenhum produto os usa mais."""
    url, _ = imagem_service.salvar(JPG, nome_base="compartilhada0001")
    a, b = criar_produto("A", imagem_url=url), criar_produto("B", imagem_url=url)

    a.imagem_url = None
    db.commit()
    assert imagem_service.apagar_se_sem_uso(db, url) is False  # B ainda usa
    assert arquivo_da_url(url).exists()

    b.imagem_url = None
    db.commit()
    assert imagem_service.apagar_se_sem_uso(db, url) is True
    assert not arquivo_da_url(url).exists()


# ---------- Proteções do serviço de imagens ----------


@pytest.mark.parametrize(
    "url",
    [
        "/uploads/produtos/../../app/main.py",
        "/uploads/produtos/..%2F..%2Fsegredo.jpg",
        "/uploads/outra-pasta/abcdefgh.jpg",
        "/uploads/produtos/abc.exe",
        "C:/Windows/win.ini",
        "https://exemplo.com/foto.jpg",
    ],
)
def test_caminhos_fora_da_pasta_sao_ignorados(db, url):
    assert imagem_service.caminho_local(url) is None
    assert imagem_service.apagar_se_sem_uso(db, url) is False


def test_leitura_para_ao_passar_do_limite():
    import io

    with pytest.raises(imagem_service.ArquivoMuitoGrande):
        imagem_service.ler_com_limite(io.BytesIO(b"x" * 1001), limite=1000)
    assert imagem_service.ler_com_limite(io.BytesIO(b"x" * 1000), limite=1000) == b"x" * 1000
