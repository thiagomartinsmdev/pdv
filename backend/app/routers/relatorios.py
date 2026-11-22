"""Endpoints de relatórios. Somente admin."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.core.deps import AdminAtual, DbSession
from app.schemas.relatorio import RelatorioVendas
from app.services import relatorio_service

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.get("/vendas", response_model=RelatorioVendas)
def vendas(
    db: DbSession,
    _admin: AdminAtual,
    inicio: Annotated[date, Query(description="Data inicial (AAAA-MM-DD)")],
    fim: Annotated[date, Query(description="Data final, inclusive (AAAA-MM-DD)")],
    limite_produtos: Annotated[int, Query(ge=1, le=50)] = 10,
) -> RelatorioVendas:
    """Total, quantidade, ticket médio, produtos mais vendidos, formas de pagamento e
    vendas por dia no período. Considera apenas vendas concluídas."""
    return relatorio_service.relatorio_vendas(db, inicio, fim, limite_produtos)
