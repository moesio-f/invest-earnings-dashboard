"""Tabela de análises do EarningYield."""

from datetime import date

from invest_earning.database.base import AnalyticBase
from invest_earning.database.wallet.entities import AssetKind, EarningKind
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger, Integer, Numeric


class EarningYield(AnalyticBase):
    __tablename__ = "earning_yield"

    # Dados do ativo
    b3_code: Mapped[str] = mapped_column(index=True, comment="Código B3 do ativo.")
    asset_kind: Mapped[AssetKind] = mapped_column(index=True, comment="Tipo do ativo.")

    # Dados do provento
    earning_id = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        comment="ID automático de provento.",
    )
    earning_kind: Mapped[EarningKind] = mapped_column(
        index=True, comment="Tipo do provento."
    )
    hold_date: Mapped[date] = mapped_column(index=True, comment="Data de custódia.")
    payment_date: Mapped[date] = mapped_column(index=True, comment="Data de pagamento.")
    ir: Mapped[float] = mapped_column(
        comment="Taxa (%) de incidência do Imposto de Renda."
    )
    value_per_share = mapped_column(
        Numeric(precision=10, scale=5, asdecimal=False),
        comment="Valor do provento por unidade.",
    )
    ir_adjusted_value_per_share = mapped_column(
        Numeric(precision=10, scale=5, asdecimal=False),
        comment="Valor líquido do provento por unidade.",
    )

    # Posição do ativo na data de custódia
    shares: Mapped[int] = mapped_column(
        comment="Quantidade de unidades do ativo na data de custódia."
    )
    avg_price = mapped_column(
        Numeric(precision=10, scale=5, asdecimal=False),
        comment="Preço médio pago pelo ativo na data de custódia.",
    )

    # YoC
    yoc = mapped_column(
        Numeric(precision=10, scale=5, asdecimal=False),
        comment="Yield On Cost (YoC) com relação ao preço médio.",
    )

    # Dados econômicos
    cdi_on_hold_month = mapped_column(
        Numeric(asdecimal=False),
        nullable=False,
        comment="Variação do CDI no mês da data de custódia.",
    )
    ipca_on_hold_month = mapped_column(
        Numeric(asdecimal=False),
        nullable=False,
        comment="Variação do CDI no mês da data de custódia.",
    )
