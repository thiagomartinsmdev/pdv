"""Regras de venda: registro, pagamento, baixa de estoque e cancelamento.

Transação: tudo que uma venda grava (venda, itens, pagamentos e baixa no estoque)
vai para o banco em UM único commit. Se qualquer passo falhar, é feito rollback e
nada fica gravado: não existe venda sem baixa de estoque, nem baixa sem venda.

Travas (SELECT ... FOR UPDATE): as linhas de produto são bloqueadas desde a leitura
do estoque até o commit. Se dois caixas venderem o último item ao mesmo tempo, o
segundo espera o primeiro terminar e então enxerga o estoque já atualizado.
"""

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.datas import intervalo_de_datas
from app.core.exceptions import AcessoNegado, Conflito, NaoEncontrado, RegraNegocio
from app.core.formatacao import reais
from app.models import (
    FormaPagamento,
    ItemVenda,
    Pagamento,
    PerfilUsuario,
    Produto,
    SessaoCaixa,
    StatusVenda,
    Usuario,
    Venda,
)
from app.schemas.venda import ItemVendaEntrada, PagamentoEntrada, VendaCriar
from app.services import caixa_service

CENTAVO = Decimal("0.01")
ZERO = Decimal("0.00")

# Carrega itens, produtos, pagamentos e operador junto com a venda (evita N+1 consultas).
_CARREGAR_DETALHES = (
    selectinload(Venda.itens).selectinload(ItemVenda.produto),
    selectinload(Venda.pagamentos),
    selectinload(Venda.usuario),
)


# ---------------------------------------------------------------------------
# Registro de venda
# ---------------------------------------------------------------------------


def registrar(db: Session, usuario: Usuario, dados: VendaCriar) -> Venda:
    try:
        venda = _montar_venda(db, usuario, dados)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return buscar(db, usuario, venda.id)


def _montar_venda(db: Session, usuario: Usuario, dados: VendaCriar) -> Venda:
    # Trava a sessão do caixa: impede que ela seja fechada no meio desta venda.
    sessao = caixa_service.obter_aberto(db, usuario, travar=True)

    quantidades = _agrupar_itens(dados.itens)
    produtos = _travar_produtos(db, quantidades.keys())
    _validar_produtos(quantidades, produtos)

    itens = [
        ItemVenda(
            produto=produtos[produto_id],
            quantidade=quantidade,
            # O preço é copiado para o item: se o produto mudar de preço amanhã,
            # esta venda continua registrando o valor realmente cobrado.
            preco_unitario=produtos[produto_id].preco,
            subtotal=(produtos[produto_id].preco * quantidade).quantize(CENTAVO),
        )
        for produto_id, quantidade in quantidades.items()
    ]

    subtotal = sum((item.subtotal for item in itens), ZERO)
    if dados.desconto >= subtotal:
        raise RegraNegocio(
            f"O desconto ({reais(dados.desconto)}) deve ser menor que o subtotal "
            f"({reais(subtotal)})."
        )
    total = subtotal - dados.desconto
    pagamentos = _montar_pagamentos(dados.pagamentos, total)

    # Baixa no estoque. As linhas estão travadas, então o valor lido continua válido.
    for produto_id, quantidade in quantidades.items():
        produtos[produto_id].quantidade_estoque -= quantidade

    venda = Venda(
        sessao_caixa=sessao,
        usuario_id=usuario.id,
        subtotal=subtotal,
        desconto=dados.desconto,
        total=total,
        status=StatusVenda.CONCLUIDA,
        itens=itens,
        pagamentos=pagamentos,
    )
    db.add(venda)
    db.flush()  # gera o id, ainda dentro da transação
    return venda


def _agrupar_itens(itens: list[ItemVendaEntrada]) -> dict[int, int]:
    """Soma as quantidades do mesmo produto (ex.: o mesmo pão bipado 3 vezes)."""
    quantidades: dict[int, int] = {}
    for item in itens:
        quantidades[item.produto_id] = quantidades.get(item.produto_id, 0) + item.quantidade
    return quantidades


def _travar_produtos(db: Session, produto_ids: Iterable[int]) -> dict[int, Produto]:
    """Lê e trava (FOR UPDATE) as linhas dos produtos.

    A ordenação por id é proposital: se toda transação trava os produtos na mesma
    ordem, duas vendas simultâneas nunca ficam esperando uma pela outra (deadlock).
    """
    ids = sorted(set(produto_ids))
    consulta = select(Produto).where(Produto.id.in_(ids)).order_by(Produto.id).with_for_update()
    produtos = {produto.id: produto for produto in db.scalars(consulta)}

    faltando = [str(i) for i in ids if i not in produtos]
    if faltando:
        raise NaoEncontrado(f"Produto(s) não encontrado(s): {', '.join(faltando)}.")
    return produtos


def _validar_produtos(quantidades: dict[int, int], produtos: dict[int, Produto]) -> None:
    """Verifica produtos inativos e estoque, listando todos os problemas de uma vez."""
    inativos = [produtos[i].nome for i in quantidades if not produtos[i].ativo]
    if inativos:
        raise RegraNegocio(f"Produto(s) inativo(s) não podem ser vendidos: {', '.join(inativos)}.")

    sem_estoque = [
        f"{produtos[i].nome} (disponível: {produtos[i].quantidade_estoque}, pedido: {qtd})"
        for i, qtd in quantidades.items()
        if produtos[i].quantidade_estoque < qtd
    ]
    if sem_estoque:
        raise RegraNegocio(f"Estoque insuficiente: {'; '.join(sem_estoque)}.")


def _montar_pagamentos(entradas: list[PagamentoEntrada], total: Decimal) -> list[Pagamento]:
    """Valida os pagamentos e calcula o troco.

    Regras:
    - a soma dos pagamentos deve cobrir o total;
    - só há troco em dinheiro, então PIX e cartões juntos não podem passar do total;
    - pagamentos repetidos na mesma forma são somados em um só.
    """
    por_forma: dict[FormaPagamento, Decimal] = {}
    for pagamento in entradas:
        por_forma[pagamento.forma] = por_forma.get(pagamento.forma, ZERO) + pagamento.valor

    total_pago = sum(por_forma.values(), ZERO)
    if total_pago < total:
        raise RegraNegocio(
            f"Pagamento insuficiente: total {reais(total)}, pago {reais(total_pago)}, "
            f"faltam {reais(total - total_pago)}."
        )

    em_dinheiro = por_forma.get(FormaPagamento.DINHEIRO, ZERO)
    fora_dinheiro = total_pago - em_dinheiro
    if fora_dinheiro > total:
        raise RegraNegocio(
            f"PIX e cartão somam {reais(fora_dinheiro)}, mais que o total de {reais(total)}. "
            "Só existe troco para pagamento em dinheiro."
        )

    # Como o que não é dinheiro cabe no total, o troco é sempre <= valor em dinheiro.
    troco = total_pago - total
    return [
        Pagamento(
            forma=forma, valor=valor, troco=troco if forma == FormaPagamento.DINHEIRO else ZERO
        )
        for forma, valor in por_forma.items()
    ]


# ---------------------------------------------------------------------------
# Consulta
# ---------------------------------------------------------------------------


def buscar(db: Session, usuario: Usuario, venda_id: int) -> Venda:
    venda = db.scalar(select(Venda).where(Venda.id == venda_id).options(*_CARREGAR_DETALHES))
    if venda is None:
        raise NaoEncontrado(f"Venda {venda_id} não encontrada.")
    if usuario.perfil != PerfilUsuario.ADMIN and venda.usuario_id != usuario.id:
        raise AcessoNegado("Você só pode consultar as suas próprias vendas.")
    return venda


def listar(
    db: Session,
    usuario: Usuario,
    inicio: date | None = None,
    fim: date | None = None,
    status: StatusVenda | None = None,
    limite: int = 100,
    deslocamento: int = 0,
) -> list[Venda]:
    """Vendas mais recentes primeiro. Admin vê todas; operador vê só as dele."""
    de, ate = intervalo_de_datas(inicio, fim)
    consulta = (
        select(Venda)
        .options(*_CARREGAR_DETALHES)
        .order_by(Venda.data_hora.desc(), Venda.id.desc())
        .limit(limite)
        .offset(deslocamento)
    )
    if usuario.perfil != PerfilUsuario.ADMIN:
        consulta = consulta.where(Venda.usuario_id == usuario.id)
    if de is not None:
        consulta = consulta.where(Venda.data_hora >= de)
    if ate is not None:
        consulta = consulta.where(Venda.data_hora < ate)
    if status is not None:
        consulta = consulta.where(Venda.status == status)
    return list(db.scalars(consulta))


# ---------------------------------------------------------------------------
# Cancelamento
# ---------------------------------------------------------------------------


def cancelar(db: Session, admin: Usuario, venda_id: int) -> Venda:
    """Cancela a venda e devolve os itens ao estoque, numa única transação."""
    try:
        venda = db.scalar(select(Venda).where(Venda.id == venda_id).with_for_update())
        if venda is None:
            raise NaoEncontrado(f"Venda {venda_id} não encontrada.")
        if venda.status == StatusVenda.CANCELADA:
            raise Conflito(f"A venda {venda_id} já está cancelada.")

        sessao = db.get(SessaoCaixa, venda.sessao_caixa_id, with_for_update=True)
        if sessao.fechado_em is not None:
            # O fechamento já foi conferido com este valor em caixa; alterar a venda
            # agora mudaria um caixa fechado retroativamente.
            raise RegraNegocio("Não é possível cancelar uma venda de um caixa já fechado.")

        produtos = _travar_produtos(db, (item.produto_id for item in venda.itens))
        for item in venda.itens:
            produtos[item.produto_id].quantidade_estoque += item.quantidade

        venda.status = StatusVenda.CANCELADA
        db.commit()
    except Exception:
        db.rollback()
        raise
    return buscar(db, admin, venda_id)
