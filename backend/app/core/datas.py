"""Conversão de filtros por data (dias do calendário) em intervalos de data e hora."""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.core.exceptions import RegraNegocio

FUSO = ZoneInfo(settings.fuso_horario)


def intervalo_de_datas(
    inicio: date | None, fim: date | None
) -> tuple[datetime | None, datetime | None]:
    """Converte [inicio, fim] (dias inteiros, no fuso local) em [de, ate).

    Ex.: inicio=fim=05/11 vira de 05/11 00:00 até 06/11 00:00 (exclusivo), no horário
    de Brasília. Sem isso, uma venda às 22h do dia 05 (01h do dia 06 em UTC) cairia
    no dia errado.
    """
    if inicio and fim and inicio > fim:
        raise RegraNegocio("A data inicial não pode ser posterior à data final.")
    de = datetime.combine(inicio, time.min, tzinfo=FUSO) if inicio else None
    ate = datetime.combine(fim + timedelta(days=1), time.min, tzinfo=FUSO) if fim else None
    return de, ate
