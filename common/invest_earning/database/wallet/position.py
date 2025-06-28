"""Posição de investimentos."""

from dataclasses import dataclass, fields
from datetime import date

import sqlalchemy as sa

from .asset import Asset, AssetKind, Transaction, TransactionKind, Earning
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
    total_earnings: float
    total_ir_adjusted_earnings: float
    yield_on_cost: float
    rate_of_return: float

    @classmethod
    def get(
        cls, session: sa.orm.Session, reference_date: date = None
    ) -> list["Position"]:
        if reference_date is None:
            reference_date = date.max

        # Most recent prices
        max_date = (
            session.query(
                MarketPrice.asset_b3_code,
                sa.sql.func.max(MarketPrice.reference_date).label("reference_date"),
            )
            .where(MarketPrice.reference_date <= reference_date)
            .group_by(MarketPrice.asset_b3_code)
            .subquery()
        )
        most_recent_prices = (
            session.query(
                MarketPrice.asset_b3_code.label("b3_code"),
                MarketPrice.closing_price.label("closing_price"),
            )
            .where(MarketPrice.asset_b3_code == max_date.c.asset_b3_code)
            .where(MarketPrice.reference_date == max_date.c.reference_date)
            .subquery()
        )

        # Total earnings paid per share up to reference_date
        total_earnings_per_share = (
            session.query(
                Earning.asset_b3_code.label("b3_code"),
                sa.sql.func.sum(
                    Earning.value_per_share * (1 - (Earning.ir_percentage / 100))
                ).label("total_ir_adjusted_earnings"),
                sa.sql.func.sum(Earning.value_per_share).label("total_earnings"),
            )
            .where(Earning.payment_date <= reference_date)
            .group_by(Earning.asset_b3_code)
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

        # Utility operations
        shares = cte.c.buy - cte.c.sell
        avg_price = cte.c.total_buy / cte.c.buy
        total_invested = shares * avg_price
        current_price = sa.sql.func.coalesce(
            most_recent_prices.c.closing_price,
            avg_price,
        )
        balance = shares * current_price
        total_earnings = shares * sa.sql.func.coalesce(
            total_earnings_per_share.c.total_earnings, 0
        )
        total_ir_adjusted_earnings = shares * sa.sql.func.coalesce(
            total_earnings_per_share.c.total_ir_adjusted_earnings, 0
        )

        return list(
            map(
                lambda v: Position(**{k.name: v for k, v in zip(fields(cls), v)}),
                session.query(
                    cte.c.b3_code,
                    shares,
                    avg_price,
                    total_invested,
                    cte.c.asset_kind,
                    current_price,
                    balance,
                    total_earnings,
                    total_ir_adjusted_earnings,
                    100 * total_ir_adjusted_earnings / total_invested,
                    100
                    * ((total_ir_adjusted_earnings + balance) - total_invested)
                    / total_invested,
                )
                .outerjoin(
                    total_earnings_per_share,
                    total_earnings_per_share.c.b3_code == cte.c.b3_code,
                )
                .outerjoin(
                    most_recent_prices,
                    most_recent_prices.c.b3_code == cte.c.b3_code,
                )
                .where(cte.c.buy - cte.c.sell != 0)
                .all(),
            )
        )
