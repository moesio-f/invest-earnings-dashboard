"""API para comunicação
nativa em Python através
de um facade.
"""

from datetime import date

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from pandera.typing import DataFrame

from app.analytics.earning_yield import EarningAnalytics
from app.analytics.entities import EarningYield
from app.config import DB_CONFIG
from app.db.models import (
    Asset,
    AssetKind,
    Earning,
    EarningKind,
    Transaction,
    TransactionKind,
)


class v1Facade:
    def __init__(self, db: str = None):
        if db is None:
            db = DB_CONFIG.connection_string

        self._engine = sa.create_engine(db)
        self._analytics = EarningAnalytics(self._engine)

    def create_asset(
        self, b3_code: str, name: str, description: str, kind: AssetKind, added: date
    ) -> Asset:
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            asset = Asset(
                b3_code=b3_code,
                name=name,
                description=description,
                kind=kind,
                added=added,
            )
            session.add(asset)
            session.commit()

        return asset

    def assets(self) -> list[Asset]:
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            return list(session.query(Asset).all())

    def add_earning(
        self,
        asset_b3_code: str,
        hold_date: date,
        payment_date: date,
        value_per_share: float,
        ir_percentage: float,
        kind: EarningKind,
    ) -> Earning:
        # Create earning
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            earning = Earning(
                asset_b3_code=asset_b3_code,
                hold_date=hold_date,
                payment_date=payment_date,
                value_per_share=value_per_share,
                ir_percentage=ir_percentage,
                kind=kind,
            )
            session.add(earning)

            # Update earnings rights
            self._update_earning_rights(earning=earning, session=session)

            # Commit
            session.commit()

        return earning

    def earnings(self) -> list[Earning]:
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            return list(
                session.query(Earning)
                .options(sa_orm.selectinload(Earning.right_to_earnings))
                .all()
            )

    def add_transaction(
        self,
        asset_b3_code: str,
        date: date,
        kind: TransactionKind,
        value_per_share: float,
        shares: int,
    ):
        # Create transaction
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            transaction = Transaction(
                asset_b3_code=asset_b3_code,
                date=date,
                kind=kind,
                value_per_share=value_per_share,
                shares=shares,
            )
            session.add(transaction)

            # Update earnings rights
            self._update_earning_rights(transaction=transaction, session=session)

            # Commit
            session.commit()

        return transaction

    def transactions(self) -> list[Transaction]:
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            return list(
                session.query(Transaction)
                .options(sa_orm.selectinload(Transaction.entitled_to_earnings))
                .all()
            )

    def earning_yield(self) -> DataFrame[EarningYield]:
        return self._analytics.earning_yield

    def _update_earning_rights(
        self,
        earning: Earning = None,
        transaction: Transaction = None,
        session: sa_orm.Session = None,
    ):
        assert (earning is not None) or (transaction is not None)
        should_manage_session = session is None
        if should_manage_session:
            session = sa_orm.Session(self._engine)

        # Add to new earning
        if earning:
            # Guarantee object is in this session
            if earning not in session:
                session.add(earning)

            transactions = (
                session.query(Transaction)
                .where(Transaction.asset_b3_code == earning.asset_b3_code)
                .where(Transaction.date <= earning.hold_date)
            )
            earning.right_to_earnings.extend(transactions)

        # Add to new transaction
        if transaction:
            # Guarantee object is in this session
            if transaction not in session:
                session.add(transaction)

            earnings = (
                session.query(Earning)
                .where(Earning.asset_b3_code == transaction.asset_b3_code)
                .where(Earning.hold_date >= transaction.date)
            )
            transaction.entitled_to_earnings.extend(earnings)

        # Commit transaction and close
        if should_manage_session:
            session.commit()
            session.close()
