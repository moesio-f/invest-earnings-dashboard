"""Dados de mercado."""

from datetime import date

from invest_earning.database.base import WalletBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric

from .asset import Asset


class MarketPrice(WalletBase):
    __tablename__ = "market_price"

    # Identificação
    reference_date: Mapped[date] = mapped_column(
        comment="Data de referência dos dados.",
        primary_key=True,
        index=True,
    )
    asset_b3_code: Mapped[str] = mapped_column(
        ForeignKey("asset.b3_code", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="Ativo sobre o qual esse dado se refere.",
    )

    # Dados econômicos
    closing_price = mapped_column(
        Numeric(precision=10, scale=5, asdecimal=False),
        comment="Cota de fechamento na data de referência.",
        nullable=False,
    )

    # Mapeamento do ativo
    asset: Mapped[Asset] = relationship()
