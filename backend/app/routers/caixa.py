"""Endpoints do caixa. Cada usuário opera somente o próprio caixa."""

from fastapi import APIRouter, status

from app.core.deps import DbSession, UsuarioAtual
from app.schemas.caixa import CaixaAbrir, CaixaFechar, CaixaResposta
from app.services import caixa_service

router = APIRouter(prefix="/caixa", tags=["Caixa"])


@router.get("/atual", response_model=CaixaResposta | None)
def atual(db: DbSession, usuario: UsuarioAtual) -> CaixaResposta | None:
    """Caixa aberto do usuário logado com o resumo parcial, ou null se não houver.

    Não ter caixa aberto é um estado normal (não um erro), por isso a resposta é 200.
    """
    sessao = caixa_service.buscar_aberto(db, usuario)
    if sessao is None:
        return None
    return caixa_service.montar_resposta(db, sessao)


@router.post("/abrir", response_model=CaixaResposta, status_code=status.HTTP_201_CREATED)
def abrir(dados: CaixaAbrir, db: DbSession, usuario: UsuarioAtual) -> CaixaResposta:
    sessao = caixa_service.abrir(db, usuario, dados.valor_abertura)
    return caixa_service.montar_resposta(db, sessao)


@router.post("/fechar", response_model=CaixaResposta)
def fechar(dados: CaixaFechar, db: DbSession, usuario: UsuarioAtual) -> CaixaResposta:
    """Fecha o caixa e devolve o valor esperado em dinheiro e a diferença."""
    sessao = caixa_service.fechar(db, usuario, dados.valor_informado)
    return caixa_service.montar_resposta(db, sessao)
