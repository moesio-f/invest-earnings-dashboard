"""Utilidades para a API."""

import sqlalchemy as sa
from invest_earning.database.wallet import Earning, Transaction


def update_earning_rights(
    session: sa.orm.Session,
    earning: Earning = None,
    transaction: Transaction = None,
):
    assert (earning is not None) or (transaction is not None)

    # Add to new earning
    if earning:
        earning.right_to_earnings = (
            session.query(Transaction)
            .where(Transaction.asset_b3_code == earning.asset_b3_code)
            .where(Transaction.date <= earning.hold_date)
        )

    # Add to new transaction
    if transaction:
        transaction.entitled_to_earnings = (
            session.query(Earning)
            .where(Earning.asset_b3_code == transaction.asset_b3_code)
            .where(Earning.hold_date >= transaction.date)
        )
