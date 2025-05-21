from datetime import date
from enum import Enum
from io import StringIO
from typing import Callable

import pandas as pd

from app.dashboard.api import api
from app.dashboard.state import Manager, ScopedState
from app.dashboard.state.proxies import ProxiedValue
from app.db.models import AssetKind, EarningKind, EconomicIndex, TransactionKind


def create_asset(
    data: ScopedState,
    callback: Callable[[], None] = None,
):
    api.create_asset(
        b3_code=data.b3_code(),
        name=data.name(),
        description=data.description(),
        kind=AssetKind.from_value(data.kind()),
        added=date.today(),
    )

    if callback:
        callback()


def update_asset(data: ScopedState, callback: Callable[[], None] = None):
    api.update_asset(
        b3_code=data.b3_code(),
        name=data.name(),
        description=data.description(),
        kind=AssetKind.from_value(data.kind()),
        added=data.added(),
    )

    if callback:
        callback()


def add_transaction(data: ScopedState, callback: Callable[[], None] = None):
    api.add_transaction(
        asset_b3_code=data.asset_b3_code(),
        date=data.date(),
        value_per_share=data.value_per_share(),
        shares=data.shares(),
        kind=TransactionKind.from_value(data.kind()),
    )

    if callback:
        callback()


def transaction_update(
    data: ScopedState, transaction_id: int, callback: Callable[[], None] = None
):
    api.update_transaction(
        transaction_id=transaction_id,
        kind=TransactionKind.from_value(data.kind()),
        value_per_share=data.value_per_share(),
        shares=data.shares(),
    )

    if callback:
        callback()


def add_earning(data: ScopedState, callback: Callable[[], None] = None):
    api.add_earning(
        asset_b3_code=data.asset_b3_code(),
        hold_date=data.hold_date(),
        payment_date=data.payment_date(),
        value_per_share=data.value_per_share(),
        ir_percentage=data.ir_percentage(),
        kind=EarningKind.from_value(data.kind()),
    )

    if callback:
        callback()


def add_economic(data: ScopedState, callback: Callable[[], None] = None):
    api.add_economic_data(
        index=data.index(),
        reference_date=data.reference_date(),
        percentage_change=data.percentage_change(),
    )

    if callback:
        callback()


def load_economic_data(data: ScopedState, callback: Callable[[], None] = None):
    io = StringIO(data.csv_contents())
    io.seek(0)
    data = pd.read_csv(io).to_dict("records")
    for d in data:
        d["index"] = EconomicIndex.from_value(d["index"])

    api.load_economic_data(*data)

    if callback:
        callback()


def csv_insert(
    data: ScopedState,
    add_fn: Callable[[ScopedState], None],
    callback: Callable[[], None] = None,
):
    io = StringIO(data.csv_contents())
    io.seek(0)
    df = pd.read_csv(io)

    for _, row in df.iterrows():
        # Prepare state
        state = Manager.get_data_state("csv_insert")
        for idx, value in row.items():
            if isinstance(value, Enum):
                value = value.from_value(value)

            if "date" in idx:
                value = date.fromisoformat(value)

            state[idx] = ProxiedValue(value)

        # Add for this row
        add_fn(state)

        # Clear scope to avoid any
        #   mismatch
        state.remove()

    if callback:
        callback()
