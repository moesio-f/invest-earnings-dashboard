"""Posição de investimentos."""

from dataclasses import dataclass, fields
from datetime import date

import sqlalchemy as sa

from .asset import Transaction, TransactionKind


@dataclass(frozen=True)
class Position:
    b3_code: str
    shares: int
    avg_price: float

    @classmethod
    def get_position(
        cls, session: sa.orm.Session, reference_date: date = None
    ) -> list["Position"]:
        if reference_date is None:
            reference_date = date.max

        is_buy_or_sell = sa.sql.func.IF(Transaction.kind == TransactionKind.buy, 1, -1)
        should_include_price = sa.sql.func.IF(
            Transaction.kind == TransactionKind.buy, 1, 0
        )
        cte = (
            session.query(
                Transaction.asset_b3_code.label("b3_code"),
                sa.sql.func.sum(is_buy_or_sell * Transaction.shares).label("shares"),
                sa.sql.func.sum(
                    should_include_price * Transaction.value_per_share
                ).label("total"),
            )
            .where(Transaction.date <= reference_date)
            .group_by(Transaction.asset_b3_code)
            .cte()
        )
        return list(
            map(
                lambda v: Position(**{k.name: v for k, v in zip(fields(cls), v)}),
                session.query(
                    cte.c.b3_code, cte.c.shares, cte.c.total / cte.c.shares
                ).all(),
            )
        )
