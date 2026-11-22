"""Endpoints de vendas."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.deps import AdminAtual, DbSession, UsuarioAtual
from app.models import StatusVenda, Venda
from app.schemas.venda import VendaCriar, VendaResposta
from app.services import venda_service

router = APIRouter(prefix="/vendas", tags=["Vendas"])


@router.post("", response_model=VendaResposta, status_code=status.HTTP_201_CREATED)
def registrar(dados: VendaCriar, db: DbSession, usuario: UsuarioAtual) -> Venda:
    """Registra uma venda no caixa aberto do usuário e dá baixa no estoque."""
    return venda_service.registrar(db, usuario, dados)


@router.get("", response_model=list[VendaResposta])
def listar(
    db: DbSession,
    usuario: UsuarioAtual,
    inicio: Annotated[date | None, Query(description="Data inicial (AAAA-MM-DD)")] = None,
    fim: Annotated[date | None, Query(description="Data final, inclusive (AAAA-MM-DD)")] = None,
    status_venda: Annotated[StatusVenda | None, Query(alias="status")] = None,
    limite: Annotated[int, Query(ge=1, le=500)] = 100,
    deslocamento: Annotated[int, Query(ge=0, description="Quantas vendas pular")] = 0,
) -> list[Venda]:
    """Histórico de vendas. Admin vê todas; operador vê apenas as próprias."""
    return venda_service.listar(db, usuario, inicio, fim, status_venda, limite, deslocamento)


@router.get("/{venda_id}", response_model=VendaResposta)
def buscar(venda_id: int, db: DbSession, usuario: UsuarioAtual) -> Venda:
    return venda_service.buscar(db, usuario, venda_id)


@router.post("/{venda_id}/cancelar", response_model=VendaResposta)
def cancelar(venda_id: int, db: DbSession, admin: AdminAtual) -> Venda:
    """Cancela a venda e devolve os itens ao estoque. Somente admin."""
    return venda_service.cancelar(db, admin, venda_id)
