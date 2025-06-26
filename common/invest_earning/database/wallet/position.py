"""Posição de investimentos."""

from dataclasses import dataclass, fields
from datetime import date

import sqlalchemy as sa

from .asset import Asset, AssetKind, Transaction, TransactionKind
from .market_price import MarketPrice


@dataclass(frozen=True)
class Position:
    b3_code: str
    shares: int
    avg_price: float
    total_invested: float
    asset_kind: AssetKind
    current_price: float
    balance: float

    @classmethod
    def get(
        cls, session: sa.orm.Session, reference_date: date = None
    ) -> list["Position"]:
        if reference_date is None:
            reference_date = date.max

        # Most recent prices
        # Assumes that all assets have data
        #   for max(reference_date)
        max_date = (
            session.query(sa.sql.func.max(MarketPrice.reference_date))
            .where(MarketPrice.reference_date <= reference_date)
            .scalar_subquery()
        )
        most_recent_prices = (
            session.query(
                MarketPrice.asset_b3_code.label("b3_code"),
                MarketPrice.closing_price.label("closing_price"),
            )
            .where(MarketPrice.reference_date == max_date)
            .subquery()
        )

        # Aggregate transactions and market prices
        is_buy = sa.sql.func.cast(Transaction.kind == TransactionKind.buy, sa.INTEGER)
        is_sell = 1 - is_buy
        asset_b3_code = Transaction.asset_b3_code.label("b3_code")
        cte = (
            session.query(
                asset_b3_code,
                Asset.kind.label("asset_kind"),
                sa.sql.func.sum(is_buy * Transaction.shares).label("buy"),
                sa.sql.func.sum(is_sell * Transaction.shares).label("sell"),
                sa.sql.func.sum(
                    is_buy * Transaction.value_per_share * Transaction.shares
                ).label("total_buy"),
                sa.sql.func.sum(
                    is_sell * Transaction.value_per_share * Transaction.shares
                ).label("total_sell"),
            )
            .join(Asset, Asset.b3_code == asset_b3_code)
            .where(Transaction.date <= reference_date)
            .group_by(Transaction.asset_b3_code, Asset.b3_code)
            .cte()
        )

        return list(
            map(
                lambda v: Position(**{k.name: v for k, v in zip(fields(cls), v)}),
                session.query(
                    cte.c.b3_code,
                    cte.c.buy - cte.c.sell,
                    cte.c.total_buy / cte.c.buy,
                    (cte.c.buy - cte.c.sell) * (cte.c.total_buy / cte.c.buy),
                    cte.c.asset_kind,
                    sa.sql.func.coalesce(
                        most_recent_prices.c.closing_price,
                        cte.c.total_buy / cte.c.buy,
                    ),
                    sa.sql.func.coalesce(
                        (cte.c.buy - cte.c.sell) * most_recent_prices.c.closing_price,
                        (cte.c.buy - cte.c.sell) * (cte.c.total_buy / cte.c.buy),
                    ),
                )
                .outerjoin(
                    most_recent_prices,
                    most_recent_prices.c.b3_code == cte.c.b3_code,
                )
                .where(cte.c.buy - cte.c.sell != 0)
                .all(),
            )
        )
