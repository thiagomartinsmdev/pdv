"""Regras de cadastro e consulta de produtos."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import Conflito, NaoEncontrado, RegraNegocio
from app.models import Categoria, ItemVenda, Produto, StatusVenda, Venda
from app.schemas.produto import ProdutoAtualizar, ProdutoCriar
from app.services import imagem_service

# Carrega a categoria de todos os produtos de uma lista com UMA consulta extra,
# em vez de uma consulta por produto (problema N+1).
_COM_CATEGORIA = selectinload(Produto.categoria)


def listar(
    db: Session,
    busca: str | None = None,
    incluir_inativos: bool = False,
    categoria_id: int | None = None,
) -> list[Produto]:
    """Lista produtos ordenados por nome, com busca opcional por nome ou código de barras."""
    consulta = select(Produto).options(_COM_CATEGORIA).order_by(Produto.nome)
    if not incluir_inativos:
        consulta = consulta.where(Produto.ativo.is_(True))
    if categoria_id is not None:
        consulta = consulta.where(Produto.categoria_id == categoria_id)
    if busca:
        # autoescape: um "%" digitado na busca é tratado como texto, e não como curinga.
        consulta = consulta.where(
            or_(Produto.nome.icontains(busca, autoescape=True), Produto.codigo_barras == busca)
        )
    return list(db.scalars(consulta))


def mais_vendidos(db: Session, dias: int = 30, limite: int = 12) -> list[Produto]:
    """Produtos ativos mais vendidos (em unidades) nos últimos `dias` dias.

    Só contam vendas concluídas. Empate: o de maior valor vendido e depois o nome.
    """
    desde = datetime.now(UTC) - timedelta(days=dias)
    unidades = func.sum(ItemVenda.quantidade)
    ids = (
        select(ItemVenda.produto_id)
        .join(ItemVenda.venda)
        .join(ItemVenda.produto)
        .where(
            Venda.status == StatusVenda.CONCLUIDA,
            Venda.data_hora >= desde,
            Produto.ativo.is_(True),
        )
        .group_by(ItemVenda.produto_id, Produto.nome)
        .order_by(unidades.desc(), func.sum(ItemVenda.subtotal).desc(), Produto.nome)
        .limit(limite)
    )
    ranking = list(db.scalars(ids))
    if not ranking:
        return []
    # Busca os produtos de uma vez e devolve na ordem do ranking.
    por_id = {
        p.id: p
        for p in db.scalars(select(Produto).options(_COM_CATEGORIA).where(Produto.id.in_(ranking)))
    }
    return [por_id[i] for i in ranking]


def buscar(db: Session, produto_id: int, travar: bool = False) -> Produto:
    """Busca por id. Com travar=True, bloqueia a linha (SELECT ... FOR UPDATE) até o commit."""
    consulta = select(Produto).where(Produto.id == produto_id)
    if travar:
        consulta = consulta.with_for_update()
    produto = db.scalar(consulta)
    if produto is None:
        raise NaoEncontrado(f"Produto {produto_id} não encontrado.")
    return produto


def buscar_por_codigo(db: Session, codigo_barras: str) -> Produto:
    """Usado pelo leitor de código de barras no caixa: só encontra produtos ativos."""
    produto = db.scalar(
        select(Produto)
        .options(_COM_CATEGORIA)
        .where(Produto.codigo_barras == codigo_barras, Produto.ativo.is_(True))
    )
    if produto is None:
        raise NaoEncontrado(f"Nenhum produto ativo com o código de barras {codigo_barras}.")
    return produto


def _garantir_codigo_livre(db: Session, codigo: str, ignorar_id: int | None = None) -> None:
    existente = db.scalar(select(Produto).where(Produto.codigo_barras == codigo))
    if existente is not None and existente.id != ignorar_id:
        raise Conflito(f"O código de barras {codigo} já pertence ao produto '{existente.nome}'.")


def _validar_categoria(db: Session, categoria_id: int | None) -> None:
    """A categoria escolhida precisa existir e estar ativa (None = sem categoria)."""
    if categoria_id is None:
        return
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise NaoEncontrado(f"Categoria {categoria_id} não encontrada.")
    if not categoria.ativo:
        raise RegraNegocio(f"A categoria '{categoria.nome}' está desativada.")


def _recusar_caminho_local_novo(url: str | None, atual: str | None = None) -> None:
    """Fotos guardadas no servidor só entram pelo upload (ou pelos scripts). Pelo
    formulário, um caminho /uploads/... só é aceito se for a foto que o produto já tem."""
    if imagem_service.eh_local(url) and url != atual:
        raise RegraNegocio("Para usar uma foto do computador, envie o arquivo pelo upload.")


def criar(db: Session, dados: ProdutoCriar) -> Produto:
    _garantir_codigo_livre(db, dados.codigo_barras)
    _validar_categoria(db, dados.categoria_id)
    _recusar_caminho_local_novo(dados.imagem_url)
    produto = Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def atualizar(db: Session, produto_id: int, dados: ProdutoAtualizar) -> Produto:
    # A linha é travada porque o admin pode ajustar o estoque enquanto um caixa vende
    # o mesmo produto: assim uma operação espera a outra terminar, sem perder baixas.
    produto = buscar(db, produto_id, travar=True)
    alteracoes = dados.model_dump(exclude_unset=True)

    if "codigo_barras" in alteracoes:
        _garantir_codigo_livre(db, alteracoes["codigo_barras"], ignorar_id=produto.id)
    # Só valida se a categoria MUDOU: um produto já ligado a uma categoria que depois
    # foi desativada pode continuar sendo editado sem precisar trocá-la.
    if "categoria_id" in alteracoes and alteracoes["categoria_id"] != produto.categoria_id:
        _validar_categoria(db, alteracoes["categoria_id"])
    imagem_antiga = produto.imagem_url
    if "imagem_url" in alteracoes:
        _recusar_caminho_local_novo(alteracoes["imagem_url"], atual=imagem_antiga)

    for campo, valor in alteracoes.items():
        setattr(produto, campo, valor)

    db.commit()
    # Trocou a foto do servidor por um link (ou removeu): o arquivo antigo é apagado.
    if produto.imagem_url != imagem_antiga:
        imagem_service.apagar_se_sem_uso(db, imagem_antiga)
    db.refresh(produto)
    return produto


def definir_imagem(db: Session, produto_id: int, conteudo: bytes) -> Produto:
    """Grava a foto enviada e a associa ao produto, apagando a foto local anterior.

    Ordem pensada para nunca deixar o produto sem foto válida:
    1. valida e grava o arquivo novo;  2. salva no banco;  3. só então apaga o antigo.
    Se o passo 2 falhar, o arquivo novo é que é apagado.
    """
    produto = buscar(db, produto_id, travar=True)
    imagem_antiga = produto.imagem_url
    url_nova, criou = imagem_service.salvar(conteudo)
    try:
        produto.imagem_url = url_nova
        db.commit()
    except Exception:
        db.rollback()
        if criou:
            imagem_service.apagar_arquivo(url_nova)
        raise
    if imagem_antiga != url_nova:
        imagem_service.apagar_se_sem_uso(db, imagem_antiga)
    db.refresh(produto)
    return produto


def remover_imagem(db: Session, produto_id: int) -> Produto:
    """Tira a foto do produto (o caixa volta a mostrar a inicial) e apaga o arquivo local."""
    produto = buscar(db, produto_id, travar=True)
    imagem_antiga = produto.imagem_url
    produto.imagem_url = None
    db.commit()
    imagem_service.apagar_se_sem_uso(db, imagem_antiga)
    db.refresh(produto)
    return produto


def desativar(db: Session, produto_id: int) -> None:
    """Exclusão lógica: o produto some do caixa, mas as vendas antigas continuam íntegras."""
    produto = buscar(db, produto_id, travar=True)
    produto.ativo = False
    db.commit()
