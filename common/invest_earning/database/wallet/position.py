"""Posição de investimentos."""

from dataclasses import dataclass, fields
from datetime import date

import sqlalchemy as sa

from .asset import Asset, AssetKind, Transaction, TransactionKind


@dataclass(frozen=True)
class Position:
    b3_code: str
    shares: int
    avg_price: float
    total_invested: float
    asset_kind: AssetKind

    @classmethod
    def get(
        cls, session: sa.orm.Session, reference_date: date = None
    ) -> list["Position"]:
        if reference_date is None:
            reference_date = date.max

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
                )
                .where(cte.c.buy - cte.c.sell != 0)
                .all(),
            )
        )
