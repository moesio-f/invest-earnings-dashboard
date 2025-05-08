from datetime import date

import pandas as pd
import sqlalchemy as sa
from pandera.typing import DataFrame

from app.analytics.entities import EarningYield
from app.db.models import Earning, Transaction, TransactionKind


class EarningAnalytics:
    def __init__(self, engine: sa.Engine):
        self._engine = engine

    @property
    def earning_yield(self) -> DataFrame[EarningYield]:
        return EarningYield.validate(self._earning_yield())

    def _earning_yield(self) -> pd.DataFrame:
        transaction_kind = Transaction.kind.label("transaction_kind")
        stmt = (
            sa.select(
                Earning.id.label("earning_id"),
                Earning.asset_b3_code.label("b3_code"),
                Earning.hold_date,
                Earning.payment_date,
                Earning.value_per_share,
                Earning.kind,
                Earning.ir_percentage.label("ir"),
                Earning.value_per_share,
                Transaction.value_per_share.label("share_price"),
                Transaction.shares,
                transaction_kind,
            )
            .select_from(Earning)
            .join(Earning.right_to_earnings)
        )
        df = pd.read_sql(str(stmt.compile(self._engine)), self._engine)

        # Degenerate case:
        if df.empty:
            schema = EarningYield.to_schema()
            column_names = list(schema.columns.keys())
            data_types = {
                column_name: column_type.dtype.type.name
                for column_name, column_type in schema.columns.items()
            }
            return pd.DataFrame(columns=column_names).astype(data_types)

        # Data cleansing/filtering
        df = df.drop(columns=["value_per_share__1"])

        # Add new column to hold average_price
        df["avg_price"] = df.shares * df.share_price
        df = df.drop(columns=["share_price"])

        # Group by dividend
        cols = [
            "earning_id",
            "b3_code",
            "hold_date",
            "payment_date",
            "value_per_share",
            "kind",
            "ir",
            "transaction_kind",
        ]
        groupby = df.groupby(cols)

        # Find the sum of avg_price and shares
        df = groupby.sum().reset_index()
        df["avg_price"] = df.avg_price / df.shares

        # Find actual number os shares to receive earning
        is_sell = df.transaction_kind != TransactionKind.buy.name
        df.loc[is_sell, ["shares"]] = -df.loc[is_sell, ["shares"]]
        df.loc[is_sell, ["avg_price"]] = 0.0
        df = df.drop(columns=["transaction_kind"])
        cols = list(df.columns)
        cols.remove("shares")
        cols.remove("avg_price")
        df = df.groupby(cols).sum().reset_index()

        # Find the dividend share after IR
        df["ir_adjusted_value_per_share"] = df.value_per_share * (1 - df.ir / 100)

        # Find total dividend
        df["total_earnings"] = df.ir_adjusted_value_per_share * df.shares

        # Find YoC
        df["yoc"] = 100 * (df.ir_adjusted_value_per_share / df.avg_price)

        # Update dates dtypes and final drop
        df = df.drop(columns=["earning_id"])
        for c in ["hold_date", "payment_date"]:
            df[c] = df[c].astype(str).map(date.fromisoformat)

        return df
