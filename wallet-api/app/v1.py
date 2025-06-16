"""API para comunicação
nativa em Python através
de um facade.
"""

from datetime import date
from typing import Optional

import pandas as pd
import sqlalchemy as sa
from fastapi import APIRouter
from invest_earning.database.wallet import (
    Asset,
    AssetKind,
    Earning,
    EarningKind,
    EconomicData,
    EconomicIndex,
    Transaction,
    TransactionKind,
)

from .db import RequiresSession

router = APIRouter(prefix="/v1", tags=["V1"])
asset_router = APIRouter(prefix="/asset", tags=["Ativos"])


@asset_router.get("/")
def assets(b3_code: str | list[str] = None, session=RequiresSession):
    """Retorna os ativos requeridos. Se `null`, retorna todos os
    ativos cadastrados.
    """
    return list(session.query(Asset).all())


@asset_router.post("/create")
def create_asset(
    b3_code: str,
    name: str,
    description: str,
    kind: AssetKind,
    added: date,
    session=RequiresSession,
):
    """Tenta realizar a criação de um ativo."""
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


@asset_router.patch("/update/{b3_code}")
def update_asset(
    b3_code: str,
    name: str = None,
    description: str = None,
    kind: AssetKind = None,
    added: date = None,
    session=RequiresSession,
):
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
    with sa.orm.Session(self._engine) as session:
        # Query
        asset = session.query(Asset).where(Asset.b3_code == b3_code).one()

        # Delete
        session.delete(asset)

        # Commit
        session.commit()


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
    with sa.orm.Session(self._engine, expire_on_commit=False) as session:
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
    with sa.orm.Session(self._engine, expire_on_commit=False) as session:
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
    with sa.orm.Session(self._engine) as session:
        # Query transaction
        earning = session.query(Earning).where(Earning.id == earning_id).one()

        # Delete
        session.delete(earning)

        # Commit
        session.commit()


def earnings(self) -> list[Earning]:
    with sa.orm.Session(self._engine, expire_on_commit=False) as session:
        return list(
            session.query(Earning)
            .options(sa.orm.selectinload(Earning.right_to_earnings))
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
    with sa.orm.Session(self._engine, expire_on_commit=False) as session:
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
    with sa.orm.Session(self._engine, expire_on_commit=False) as session:
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
    with sa.orm.Session(self._engine) as session:
        # Query
        transaction = (
            session.query(Transaction).where(Transaction.id == transaction_id).one()
        )

        # Delete
        session.delete(transaction)

        # Commit
        session.commit()


def transactions(self) -> list[Transaction]:
    with sa.orm.Session(self._engine, expire_on_commit=False) as session:
        return list(
            session.query(Transaction)
            .options(sa.orm.selectinload(Transaction.entitled_to_earnings))
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
    with sa.orm.Session(self._engine) as session:
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
    with sa.orm.Session(self._engine) as session:
        session.execute(sa.insert(EconomicData), data)
        session.commit()


def economic_data(self) -> list[EconomicData]:
    with sa.orm.Session(self._engine, expire_on_commit=False) as session:
        return list(session.query(EconomicData).all())


def _update_earning_rights(
    self,
    earning: Earning = None,
    transaction: Transaction = None,
    session: sa.orm.Session = None,
):
    assert (earning is not None) or (transaction is not None)
    should_manage_session = session is None
    if should_manage_session:
        session = sa.orm.Session(self._engine)

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


router.include_router(asset_router)
