"""API para comunicação
nativa em Python através
de um facade.
"""

from datetime import date

import pandas as pd
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from pandera.typing import DataFrame

from app.analytics.engine import AnalyticsEngine
from app.analytics.entities import (
    EarningMetrics,
    EarningYield,
    MonthlyEarning,
    MonthlyIndexYoC,
    MonthlyYoC,
)
from app.config import DB_CONFIG
from app.db.models import (
    Asset,
    AssetKind,
    Earning,
    EarningKind,
    EconomicData,
    EconomicIndex,
    Transaction,
    TransactionKind,
)


class APIv1:
    def __init__(self, db: str = None):
        if db is None:
            db = DB_CONFIG.connection_string

        self._engine = sa.create_engine(db)
        self._analytics = AnalyticsEngine(self._engine)

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

    def update_asset(
        self,
        b3_code: str,
        name: str | None = None,
        description: str | None = None,
        kind: AssetKind | None = None,
        added: date | None = None,
    ) -> Asset:
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            asset = session.query(Asset).where(Asset.b3_code == b3_code).one()

            # Update fields
            for field, value in zip(
                ["name", "description", "kind", "added"],
                [name, description, kind, added],
            ):
                if value is not None:
                    setattr(asset, field, value)

            # Commit
            session.commit()

        return asset

    def delete_asset(self, b3_code: str):
        with sa_orm.Session(self._engine) as session:
            # Query
            asset = session.query(Asset).where(Asset.b3_code == b3_code).one()

            # Delete
            session.delete(asset)

            # Commit
            session.commit()

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

    def update_earning(
        self,
        earning_id: int,
        payment_date: date | None = None,
        value_per_share: float | None = None,
        ir_percentage: float | None = None,
        kind: EarningKind | None = None,
    ) -> Earning:
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            earning = session.query(Earning).where(Earning.id == earning_id).one()

            # Update fields
            for field, value in zip(
                [
                    "payment_date",
                    "value_per_share",
                    "ir_percentage",
                    "kind",
                ],
                [payment_date, value_per_share, ir_percentage, kind],
            ):
                if value is not None:
                    setattr(earning, field, value)

            # Commit
            session.commit()

        return earning

    def delete_earning(self, earning_id: int):
        # Delete transaction
        with sa_orm.Session(self._engine) as session:
            # Query transaction
            earning = session.query(Earning).where(Earning.id == earning_id).one()

            # Delete
            session.delete(earning)

            # Commit
            session.commit()

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
    ) -> Transaction:
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

    def update_transaction(
        self,
        transaction_id: int,
        kind: TransactionKind | None = None,
        value_per_share: float | None = None,
        shares: int | None = None,
    ) -> Transaction:
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            transaction = (
                session.query(Transaction).where(Transaction.id == transaction_id).one()
            )

            # Update fields
            for field, value in zip(
                [
                    "kind",
                    "value_per_share",
                    "shares",
                ],
                [kind, value_per_share, shares],
            ):
                if value is not None:
                    setattr(transaction, field, value)

            # Commit
            session.commit()

        return transaction

    def delete_transaction(self, transaction_id: int):
        with sa_orm.Session(self._engine) as session:
            # Query
            transaction = (
                session.query(Transaction).where(Transaction.id == transaction_id).one()
            )

            # Delete
            session.delete(transaction)

            # Commit
            session.commit()

    def transactions(self) -> list[Transaction]:
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            return list(
                session.query(Transaction)
                .options(sa_orm.selectinload(Transaction.entitled_to_earnings))
                .all()
            )

    def add_economic_data(
        self,
        index: EconomicIndex,
        reference_date: date,
        percentage_change: float,
        number_index: float = None,
    ) -> EconomicData:
        self.load_economic_data(
            dict(
                index=index,
                reference_date=reference_date,
                percentage_change=percentage_change,
                number_index=number_index,
            )
        )

    def delete_economic_data(self, index: EconomicIndex, reference_date: date):
        with sa_orm.Session(self._engine) as session:
            # Query
            economic = (
                session.query(EconomicData)
                .where(EconomicData.index == index)
                .where(EconomicData.reference_date == reference_date)
                .one()
            )

            # Delete
            session.delete(economic)

            # Commit
            session.commit()

    def load_economic_data(self, *data: dict):
        data = list(data)

        # Guarantee that reference date is last day
        #   of the month
        for d in data:
            d["reference_date"] = (
                pd.to_datetime(d["reference_date"]) + pd.offsets.MonthEnd(0)
            ).date()

        # Add all data to database
        with sa_orm.Session(self._engine) as session:
            session.execute(sa.insert(EconomicData), data)
            session.commit()

    def economic_data(self) -> list[EconomicData]:
        with sa_orm.Session(self._engine, expire_on_commit=False) as session:
            return list(session.query(EconomicData).all())

    def earning_metrics(self) -> EarningMetrics:
        return self._analytics.earning_metrics()

    def earning_yield(self) -> DataFrame[EarningYield]:
        return self._analytics.earning_yield()

    def monthly_earning(self) -> DataFrame[MonthlyEarning]:
        return self._analytics.monthly_earning()

    def monthly_yoc(self, target_asset: str, date_col: str) -> DataFrame[MonthlyYoC]:
        return self._analytics.monthly_yoc(target_asset, date_col)

    def monthly_index_yoc(
        self, target_asset: str, date_col: str
    ) -> DataFrame[MonthlyIndexYoC]:
        return self._analytics.monthly_index_yoc(target_asset, date_col)

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
