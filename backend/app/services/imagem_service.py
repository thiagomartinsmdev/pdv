"""Fotos de produto guardadas no próprio servidor.

- Validação pelo TIPO REAL do arquivo: os primeiros bytes ("assinatura") de JPG, PNG
  e WebP. A extensão e o tipo informados pelo navegador não são confiáveis.
- O arquivo é salvo em <uploads_dir>/produtos com um nome que não vem do usuário, e
  a extensão vem do tipo detectado.
- No banco fica o caminho relativo (/uploads/produtos/<nome>), que continua válido
  se a API mudar de endereço.
- Um arquivo só é apagado se estiver dentro da pasta de uploads e nenhum produto
  ainda o usar.
"""

import logging
import re
import secrets
from pathlib import Path
from typing import BinaryIO

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ArquivoMuitoGrande, RegraNegocio
from app.models import Produto

log = logging.getLogger(__name__)

PREFIXO_URL = "/uploads/produtos/"
# Só nomes gerados por nós: letras, números, "_" ou "-", com uma das 3 extensões.
_URL_LOCAL = re.compile(r"^/uploads/produtos/([A-Za-z0-9_-]{8,80}\.(?:jpg|png|webp))$")
_TAMANHO_BLOCO = 64 * 1024


class ImagemInvalida(RegraNegocio):
    """O arquivo não é um JPG, PNG ou WebP de verdade."""


def pasta_produtos() -> Path:
    pasta = Path(settings.uploads_dir) / "produtos"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def detectar_extensao(conteudo: bytes) -> str | None:
    """Extensão pelo conteúdo: "jpg", "png", "webp" ou None se não for nenhum deles."""
    if conteudo.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if conteudo.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(conteudo) >= 12 and conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":
        return "webp"
    return None


def ler_com_limite(arquivo: BinaryIO, limite: int | None = None) -> bytes:
    """Lê o arquivo em blocos e para assim que passar do limite, sem carregar o resto."""
    limite = settings.tamanho_maximo_imagem if limite is None else limite
    partes: list[bytes] = []
    lido = 0
    while bloco := arquivo.read(_TAMANHO_BLOCO):
        lido += len(bloco)
        if lido > limite:
            raise ArquivoMuitoGrande(
                f"A imagem passa de {limite // (1024 * 1024)} MB. Envie um arquivo menor."
            )
        partes.append(bloco)
    return b"".join(partes)


def validar(conteudo: bytes) -> str:
    """Devolve a extensão do tipo real, ou lança ImagemInvalida."""
    if len(conteudo) > settings.tamanho_maximo_imagem:
        raise ArquivoMuitoGrande(
            f"A imagem passa de {settings.tamanho_maximo_imagem // (1024 * 1024)} MB."
        )
    extensao = detectar_extensao(conteudo)
    if extensao is None:
        raise ImagemInvalida("O arquivo não é uma imagem JPG, PNG ou WebP válida.")
    return extensao


def salvar(conteudo: bytes, nome_base: str | None = None) -> tuple[str, bool]:
    """Valida e grava. Devolve (caminho relativo /uploads/produtos/..., criou_arquivo).

    nome_base: sem ele, o nome é aleatório. O importador em lote passa um hash do
    conteúdo, para a mesma foto não ser gravada duas vezes; nesse caso o arquivo pode
    já existir (criou_arquivo=False) e talvez esteja em uso por outro produto.
    """
    extensao = validar(conteudo)
    nome = f"{nome_base or secrets.token_hex(16)}.{extensao}"
    destino = pasta_produtos() / nome
    if destino.exists():
        return PREFIXO_URL + nome, False
    destino.write_bytes(conteudo)
    return PREFIXO_URL + nome, True


def eh_local(url: str | None) -> bool:
    return bool(url) and _URL_LOCAL.match(url) is not None


def caminho_local(url: str | None) -> Path | None:
    """Arquivo correspondente a um caminho /uploads/produtos/..., ou None.

    Recusa qualquer coisa fora do formato gerado por nós e qualquer caminho que, depois
    de resolvido, saia da pasta de uploads (proteção contra "../").
    """
    if not url:
        return None
    combinacao = _URL_LOCAL.match(url)
    if combinacao is None:
        return None
    pasta = pasta_produtos().resolve()
    caminho = (pasta / combinacao.group(1)).resolve()
    return caminho if caminho.parent == pasta else None


def apagar_se_sem_uso(db: Session, url: str | None) -> bool:
    """Apaga o arquivo local se nenhum produto o usa mais. Links externos são ignorados.

    Chamar DEPOIS do commit: se a gravação no banco falhar, a foto antiga continua lá.
    """
    caminho = caminho_local(url)
    if caminho is None:
        return False
    em_uso = db.scalar(select(func.count(Produto.id)).where(Produto.imagem_url == url))
    if em_uso:
        return False
    try:
        caminho.unlink(missing_ok=True)
    except OSError:
        # Não impede a operação: no máximo sobra um arquivo órfão na pasta.
        log.warning("Não foi possível apagar a imagem antiga %s", caminho, exc_info=True)
        return False
    return True


def apagar_arquivo(url: str | None) -> None:
    """Apaga um arquivo recém-gravado que não chegou a ser usado (ex.: commit falhou)."""
    caminho = caminho_local(url)
    if caminho is not None:
        caminho.unlink(missing_ok=True)
