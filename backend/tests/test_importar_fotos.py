"""Testes do script de importação de fotos em lote."""

from app.core.config import settings
from app.services import imagem_service
from scripts.importar_fotos import importar, main

JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 200
JPG_2 = b"\xff\xd8\xff\xe1" + b"\x11" * 200  # outra foto
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
WEBP = b"RIFF" + (212).to_bytes(4, "little") + b"WEBPVP8 " + b"\x00" * 200


def arquivos_salvos() -> list:
    return sorted(imagem_service.pasta_produtos().iterdir())


def test_importa_pelo_codigo_de_barras(db, tmp_path, criar_produto):
    pao, leite, cafe = criar_produto("Pão"), criar_produto("Leite"), criar_produto("Café")
    (tmp_path / f"{pao.codigo_barras}.jpg").write_bytes(JPG)
    (tmp_path / f"{leite.codigo_barras}.PNG").write_bytes(PNG)  # maiúscula também vale
    (tmp_path / f"{cafe.codigo_barras}.webp").write_bytes(WEBP)

    relatorio = importar(db, tmp_path)

    assert len(relatorio.importados) == 3
    for produto, extensao in [(pao, "jpg"), (leite, "png"), (cafe, "webp")]:
        db.refresh(produto)
        assert produto.imagem_url.endswith(f".{extensao}")
        assert imagem_service.caminho_local(produto.imagem_url).exists()


def test_relata_o_que_nao_bateu(db, tmp_path, criar_produto):
    pao = criar_produto("Pão")
    (tmp_path / "0000000000000.jpg").write_bytes(JPG)  # nenhum produto
    (tmp_path / f"{pao.codigo_barras}.jpg").write_bytes(b"texto, nao imagem")  # inválido
    (tmp_path / "leia-me.txt").write_text("oi")  # extensão não aceita
    (tmp_path / "animacao.gif").write_bytes(b"GIF89a")

    relatorio = importar(db, tmp_path)

    assert relatorio.importados == []
    assert relatorio.sem_produto == ["0000000000000.jpg"]
    assert relatorio.invalidos == [
        f"{pao.codigo_barras}.jpg: O arquivo não é uma imagem JPG, PNG ou WebP válida."
    ]
    assert sorted(relatorio.ignorados) == ["animacao.gif", "leia-me.txt"]
    assert arquivos_salvos() == []


def test_arquivo_grande_e_invalido(db, tmp_path, criar_produto):
    pao = criar_produto("Pão")
    (tmp_path / f"{pao.codigo_barras}.jpg").write_bytes(
        JPG + b"\x00" * settings.tamanho_maximo_imagem
    )

    relatorio = importar(db, tmp_path)

    assert len(relatorio.invalidos) == 1
    assert "2 MB" in relatorio.invalidos[0]


def test_rodar_de_novo_nao_duplica(db, tmp_path, criar_produto):
    pao, leite = criar_produto("Pão"), criar_produto("Leite")
    (tmp_path / f"{pao.codigo_barras}.jpg").write_bytes(JPG)
    (tmp_path / f"{leite.codigo_barras}.png").write_bytes(PNG)
    importar(db, tmp_path)
    antes = arquivos_salvos()

    relatorio = importar(db, tmp_path)

    assert relatorio.importados == []
    assert len(relatorio.iguais) == 2
    assert arquivos_salvos() == antes


def test_arquivo_apagado_do_disco_e_gravado_de_novo(db, tmp_path, criar_produto):
    pao = criar_produto("Pão")
    (tmp_path / f"{pao.codigo_barras}.jpg").write_bytes(JPG)
    importar(db, tmp_path)
    db.refresh(pao)
    imagem_service.caminho_local(pao.imagem_url).unlink()

    relatorio = importar(db, tmp_path)

    assert len(relatorio.importados) == 1
    assert imagem_service.caminho_local(pao.imagem_url).exists()


def test_substitui_foto_existente_e_apaga_a_antiga(db, tmp_path, criar_produto):
    pao = criar_produto("Pão")
    (tmp_path / f"{pao.codigo_barras}.jpg").write_bytes(JPG)
    importar(db, tmp_path)
    db.refresh(pao)
    antiga = imagem_service.caminho_local(pao.imagem_url)

    (tmp_path / f"{pao.codigo_barras}.jpg").write_bytes(JPG_2)  # foto nova, mesmo nome
    relatorio = importar(db, tmp_path)

    db.refresh(pao)
    assert len(relatorio.importados) == 1
    assert not antiga.exists()
    assert imagem_service.caminho_local(pao.imagem_url).read_bytes() == JPG_2


def test_substitui_link_externo(db, tmp_path, criar_produto):
    pao = criar_produto("Pão", imagem_url="https://exemplo.com/pao.jpg")
    (tmp_path / f"{pao.codigo_barras}.jpg").write_bytes(JPG)

    importar(db, tmp_path)

    db.refresh(pao)
    assert imagem_service.eh_local(pao.imagem_url)


def test_pular_existentes_mantem_quem_ja_tem_foto(db, tmp_path, criar_produto):
    com_foto = criar_produto("Com foto", imagem_url="https://exemplo.com/a.jpg")
    sem_foto = criar_produto("Sem foto")
    (tmp_path / f"{com_foto.codigo_barras}.jpg").write_bytes(JPG)
    (tmp_path / f"{sem_foto.codigo_barras}.jpg").write_bytes(JPG_2)

    relatorio = importar(db, tmp_path, pular_existentes=True)

    db.refresh(com_foto)
    db.refresh(sem_foto)
    assert com_foto.imagem_url == "https://exemplo.com/a.jpg"
    assert imagem_service.eh_local(sem_foto.imagem_url)
    assert len(relatorio.pulados) == 1
    assert len(relatorio.importados) == 1


def test_dois_arquivos_para_o_mesmo_codigo(db, tmp_path, criar_produto):
    pao = criar_produto("Pão")
    (tmp_path / f"{pao.codigo_barras}.jpg").write_bytes(JPG)
    (tmp_path / f"{pao.codigo_barras}.png").write_bytes(PNG)

    relatorio = importar(db, tmp_path)

    assert len(relatorio.importados) == 1
    assert relatorio.repetidos == [f"{pao.codigo_barras}.png (já usado: {pao.codigo_barras}.jpg)"]


def test_mesma_foto_em_dois_produtos_vira_um_arquivo_so(db, tmp_path, criar_produto):
    """Arquivo compartilhado: tirar a foto de um produto não apaga a do outro."""
    a, b = criar_produto("A"), criar_produto("B")
    (tmp_path / f"{a.codigo_barras}.jpg").write_bytes(JPG)
    (tmp_path / f"{b.codigo_barras}.jpg").write_bytes(JPG)

    importar(db, tmp_path)
    db.refresh(a)
    db.refresh(b)
    assert a.imagem_url == b.imagem_url
    assert len(arquivos_salvos()) == 1

    from app.services import produto_service

    produto_service.remover_imagem(db, a.id)
    assert imagem_service.caminho_local(b.imagem_url).exists()


def test_pasta_inexistente(tmp_path, capsys):
    codigo = main([str(tmp_path / "nao-existe")])

    assert codigo == 2
    assert "Pasta não encontrada" in capsys.readouterr().err
