from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Numeric

from .base import Base
from .entities import EconomicIndex


class EconomicData(Base):
    __tablename__ = "economic_data"

    index: Mapped[EconomicIndex] = mapped_column(
        primary_key=True, comment="Indíce ecônomico que os dados se referem."
    )
    reference_date: Mapped[date] = mapped_column(
        primary_key=True, comment="Data de referência."
    )
    percentage_change = mapped_column(
        Numeric(),
        nullable=False,
        comment="Variação do indicador para o mês de referência.",
    )
    number_index = mapped_column(
        Numeric(precision=12, scale=6),
        nullable=True,
        comment="Número índice (se disponível).",
    )
