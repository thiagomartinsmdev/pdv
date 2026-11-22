"""Regras de abertura, fechamento e conferência do caixa."""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import Conflito, RegraNegocio
from app.models import FormaPagamento, SessaoCaixa, Usuario, Venda
from app.schemas.caixa import CaixaResposta, ResumoCaixa
from app.services import totais


def buscar_aberto(db: Session, usuario: Usuario, travar: bool = False) -> SessaoCaixa | None:
    """Devolve o caixa aberto do usuário, ou None.

    Com travar=True, a linha da sessão fica bloqueada até o commit. Isso impede, por
    exemplo, que uma venda seja registrada enquanto o mesmo caixa está sendo fechado.
    """
    consulta = select(SessaoCaixa).where(
        SessaoCaixa.usuario_id == usuario.id, SessaoCaixa.fechado_em.is_(None)
    )
    if travar:
        consulta = consulta.with_for_update()
    return db.scalar(consulta)


def obter_aberto(db: Session, usuario: Usuario, travar: bool = False) -> SessaoCaixa:
    """Como buscar_aberto, mas gera erro se não houver caixa aberto."""
    sessao = buscar_aberto(db, usuario, travar=travar)
    if sessao is None:
        raise RegraNegocio("Você não tem um caixa aberto. Abra o caixa para continuar.")
    return sessao


def abrir(db: Session, usuario: Usuario, valor_abertura: Decimal) -> SessaoCaixa:
    if buscar_aberto(db, usuario) is not None:
        raise Conflito("Você já tem um caixa aberto. Feche-o antes de abrir outro.")

    sessao = SessaoCaixa(usuario_id=usuario.id, valor_abertura=valor_abertura)
    db.add(sessao)
    try:
        db.commit()
    except IntegrityError:
        # Duas aberturas simultâneas passaram pela verificação acima: o índice único
        # parcial do banco deixa só uma ser gravada, e a outra cai aqui.
        db.rollback()
        raise Conflito("Você já tem um caixa aberto. Feche-o antes de abrir outro.") from None
    db.refresh(sessao)
    return sessao


def fechar(db: Session, usuario: Usuario, valor_informado: Decimal) -> SessaoCaixa:
    sessao = obter_aberto(db, usuario, travar=True)
    sessao.fechado_em = func.now()
    sessao.valor_informado_fechamento = valor_informado
    db.commit()
    db.refresh(sessao)
    return sessao


def calcular_resumo(db: Session, sessao: SessaoCaixa) -> ResumoCaixa:
    da_sessao = Venda.sessao_caixa_id == sessao.id
    quantidade, total_vendido = totais.quantidade_e_total(db, da_sessao)
    por_forma = totais.total_por_forma(db, da_sessao)

    return ResumoCaixa(
        quantidade_vendas=quantidade,
        total_vendido=total_vendido,
        total_por_forma=por_forma,
        valor_esperado_dinheiro=sessao.valor_abertura + por_forma[FormaPagamento.DINHEIRO],
    )


def montar_resposta(db: Session, sessao: SessaoCaixa) -> CaixaResposta:
    """Junta os dados da sessão com o resumo e a diferença do fechamento."""
    resumo = calcular_resumo(db, sessao)
    diferenca = None
    if sessao.valor_informado_fechamento is not None:
        diferenca = sessao.valor_informado_fechamento - resumo.valor_esperado_dinheiro

    return CaixaResposta(
        id=sessao.id,
        usuario_id=sessao.usuario_id,
        aberto_em=sessao.aberto_em,
        fechado_em=sessao.fechado_em,
        valor_abertura=sessao.valor_abertura,
        valor_informado_fechamento=sessao.valor_informado_fechamento,
        resumo=resumo,
        diferenca=diferenca,
    )
