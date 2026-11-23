"""Importa fotos de produto em lote a partir de uma pasta.

Uso (dentro da pasta backend/, com o venv ativo):
    python -m scripts.importar_fotos C:\\fotos
    python -m scripts.importar_fotos C:\\fotos --pular-existentes

Regras:
- Cada arquivo deve se chamar <código de barras>.<extensão>, por exemplo
  7891000000014.jpg. Extensões aceitas: .jpg, .jpeg, .png e .webp.
- Cada arquivo passa pela mesma validação do upload: tipo real (pelos primeiros
  bytes) e no máximo 2 MB.
- Por padrão, a foto da pasta SUBSTITUI a que o produto já tem (e a foto antiga
  guardada no servidor é apagada). Com --pular-existentes, produtos que já têm foto
  ficam como estão.
- Pode rodar várias vezes: o nome do arquivo salvo é um hash do conteúdo, então a
  mesma foto não é gravada de novo, e produtos que já estão com ela são pulados.
"""

import argparse
import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.exceptions import ErroAplicacao
from app.models import Produto
from app.services import imagem_service, produto_service

EXTENSOES = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass
class Relatorio:
    importados: list[str] = field(default_factory=list)  # "arquivo -> produto"
    iguais: list[str] = field(default_factory=list)  # já estavam com esta foto
    pulados: list[str] = field(default_factory=list)  # já tinham foto (--pular-existentes)
    sem_produto: list[str] = field(default_factory=list)  # nenhum produto com esse código
    repetidos: list[str] = field(default_factory=list)  # 2 arquivos para o mesmo código
    invalidos: list[str] = field(default_factory=list)  # "arquivo: motivo"
    ignorados: list[str] = field(default_factory=list)  # extensão não aceita


def nome_pelo_conteudo(conteudo: bytes) -> str:
    """Nome do arquivo salvo: hash do conteúdo (a mesma foto gera sempre o mesmo nome)."""
    return hashlib.sha256(conteudo).hexdigest()[:32]


def importar(db: Session, pasta: Path, pular_existentes: bool = False) -> Relatorio:
    relatorio = Relatorio()
    codigos_vistos: dict[str, str] = {}

    for arquivo in sorted(p for p in pasta.iterdir() if p.is_file()):
        if arquivo.suffix.lower() not in EXTENSOES:
            relatorio.ignorados.append(arquivo.name)
            continue

        codigo = arquivo.stem.strip()
        if codigo in codigos_vistos:
            relatorio.repetidos.append(f"{arquivo.name} (já usado: {codigos_vistos[codigo]})")
            continue
        codigos_vistos[codigo] = arquivo.name

        produto = db.scalar(select(Produto).where(Produto.codigo_barras == codigo))
        if produto is None:
            relatorio.sem_produto.append(arquivo.name)
            continue

        try:
            with arquivo.open("rb") as entrada:
                conteudo = imagem_service.ler_com_limite(entrada)
            extensao = imagem_service.validar(conteudo)
        except ErroAplicacao as erro:
            relatorio.invalidos.append(f"{arquivo.name}: {erro.mensagem}")
            continue

        nome = nome_pelo_conteudo(conteudo)
        destino = f"{imagem_service.PREFIXO_URL}{nome}.{extensao}"
        # Já está com esta foto (e o arquivo existe no disco): nada a fazer.
        if produto.imagem_url == destino and imagem_service.caminho_local(destino).exists():
            relatorio.iguais.append(f"{arquivo.name} -> {produto.nome}")
            continue
        if pular_existentes and produto.imagem_url:
            relatorio.pulados.append(f"{arquivo.name} -> {produto.nome}")
            continue

        # Mesma rotina do upload: grava, salva no banco e só então apaga a foto antiga.
        produto_service.definir_imagem(db, produto.id, conteudo, nome_base=nome)
        relatorio.importados.append(f"{arquivo.name} -> {produto.nome}")

    return relatorio


def imprimir(relatorio: Relatorio) -> None:
    secoes = [
        ("Importadas", relatorio.importados),
        ("Já estavam com esta foto (puladas)", relatorio.iguais),
        ("Produto já tinha foto (--pular-existentes)", relatorio.pulados),
        ("Nenhum produto com este código de barras", relatorio.sem_produto),
        ("Mais de um arquivo para o mesmo código", relatorio.repetidos),
        ("Arquivos inválidos", relatorio.invalidos),
        ("Ignorados (extensão não aceita)", relatorio.ignorados),
    ]
    for titulo, itens in secoes:
        print(f"{titulo}: {len(itens)}")
        for item in itens:
            print(f"  - {item}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.importar_fotos",
        description="Importa fotos nomeadas pelo código de barras (ex.: 7891000000014.jpg).",
    )
    parser.add_argument("pasta", type=Path, help="pasta com as fotos")
    parser.add_argument(
        "--pular-existentes",
        action="store_true",
        help="não troca a foto de produtos que já têm uma",
    )
    args = parser.parse_args(argv)

    if not args.pasta.is_dir():
        print(f"Pasta não encontrada: {args.pasta}", file=sys.stderr)
        return 2

    with SessionLocal() as db:
        relatorio = importar(db, args.pasta, pular_existentes=args.pular_existentes)
    imprimir(relatorio)
    return 0


if __name__ == "__main__":
    sys.exit(main())
