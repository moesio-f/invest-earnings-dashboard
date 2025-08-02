"""Callbacks para componentes do streamlit."""

import logging
from datetime import date
from io import StringIO
from typing import Callable

import pandas as pd
from app.utils.state import Manager, ScopedState

from .client import WalletApi

logger = logging.getLogger(__name__)


def create_asset(
    data: ScopedState,
    callback: Callable[[], None] = None,
):
    if "bulk_data" not in data:
        data = [
            dict(
                b3_code=data.b3_code(),
                name=data.name(),
                description=data.description(),
                kind=data.kind(),
                added=date.today(),
            )
        ]
    else:
        data = data.bulk_data

    for d in data:
        WalletApi.create_asset(**d)

    if callback:
        callback()


def update_asset(data: ScopedState, callback: Callable[[], None] = None):
    WalletApi.update_asset(
        b3_code=data.b3_code(),
        name=data.name(),
        description=data.description(),
        kind=data.kind(),
        added=data.added(),
    )

    if callback:
        callback()


def create_transaction(data: ScopedState, callback: Callable[[], None] = None):
    if "bulk_data" not in data:
        data = [
            dict(
                asset_b3_code=data.asset_b3_code(),
                date=data.date(),
                value_per_share=data.value_per_share(),
                shares=data.shares(),
                kind=data.kind(),
            )
        ]
    else:
        data = data.bulk_data

    for d in data:
        WalletApi.create_transaction(**d)

    if callback:
        callback()


def update_transaction(
    data: ScopedState, transaction_id: int, callback: Callable[[], None] = None
):
    WalletApi.update_transaction(
        transaction_id=transaction_id,
        kind=data.kind(),
        value_per_share=data.value_per_share(),
        shares=data.shares(),
    )

    if callback:
        callback()


def create_earning(data: ScopedState, callback: Callable[[], None] = None):
    if "bulk_data" not in data:
        data = [
            dict(
                asset_b3_code=data.asset_b3_code(),
                hold_date=data.hold_date(),
                payment_date=data.payment_date(),
                value_per_share=data.value_per_share(),
                ir_percentage=data.ir_percentage(),
                kind=data.kind(),
            )
        ]
    else:
        data = data.bulk_data

    for d in data:
        WalletApi.create_earning(**d)

    if callback:
        callback()


def update_or_delete_earning(
    data: ScopedState, earning_id: int, callback: Callable[[], None] = None
):
    logger.debug("Called for earning with id %d.", earning_id)
    logger.debug(
        "Called with following data: %s", {k: v.get() for k, v in data.items()}
    )

    if data.get("should_delete", False):
        logger.debug(
            "Operation is delete. Ignoring all fields and only using `earning_id`."
        )
        WalletApi.delete_earning(earning_id)
        logger.debug("Success delete.")
    else:
        WalletApi.update_earning(
            earning_id=earning_id,
            hold_date=data.hold_date(),
            payment_date=data.payment_date(),
            kind=data.kind(),
            value_per_share=data.value_per_share(),
            ir_percentage=data.ir_percentage(),
        )
        logger.debug("Success update.")

    if callback:
        callback()


def add_economic(data: ScopedState, callback: Callable[[], None] = None):
    logger.debug("Called with following data: %s", data.keys())
    if "bulk_data" in data:
        data = data.bulk_data
    else:
        data = [
            dict(
                index=data.index(),
                reference_date=data.reference_date(),
                percentage_change=data.percentage_change(),
            )
        ]

    logger.debug("Adding following data: %s", data)
    WalletApi.economic_add(data)

    if callback:
        callback()


def csv_insert(
    data: ScopedState,
    fn: Callable[[ScopedState], None],
    callback: Callable[[], None] = None,
):
    # Load DataFrame from string
    io = StringIO(data.csv_contents())
    io.seek(0)
    df = pd.read_csv(io)

    # Create state
    state = Manager.get_data_state("csv_insert")
    state.bulk_data = df.to_dict(orient="records")

    # Apply function
    fn(state)

    # Clear state
    state.clear()

    if callback:
        callback()
