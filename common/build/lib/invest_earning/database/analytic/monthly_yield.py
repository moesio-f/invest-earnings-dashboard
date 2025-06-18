"""Pseudo-view para YoC
mensal por ativo ou grupo
de ativos.
"""

from dataclasses import dataclass, fields
from datetime import date

import sqlalchemy as sa


@dataclass(frozen=True)
class MonthlyYield:
    reference_date: date
    total_earnings: float
    group_or_asset: str
    yoc: float
    cdi: float | None
    ipca: float | None

    @classmethod
    def get(
        cls, session: sa.orm.Session, reference_date: date
    ) -> list["MonthlyYield"]: ...
