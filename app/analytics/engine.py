from datetime import date, datetime
from typing import Callable

import pandas as pd
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from pandera.typing import DataFrame

from app.analytics.entities import (
    EarningMetrics,
    EarningYield,
    MonthlyEarning,
    MonthlyIndexYoC,
    MonthlyYoC,
)
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


class AnalyticsEngine:
    def __init__(self, engine: sa.Engine, cache_ttl: float = 15.0):
        self._engine = engine
        self._cache = dict()
        self._cache["__last_update"] = datetime.now()
        self._cache_ttl = cache_ttl

    def earning_metrics(self) -> EarningMetrics:
        df = self.earning_yield()
        dt = pd.to_datetime(df.payment_date)
        today = date.today()

        def _between(start, end):
            return df[(dt >= start) & (dt <= end)]

        def _last_months(n: int):
            today = pd.to_datetime(date.today())
            start = today + pd.offsets.MonthBegin(-n)
            end = today + pd.offsets.MonthEnd(0)
            return _between(start, end)

        return EarningMetrics(
            n_assets_with_earnings=df.b3_code.nunique(),
            total_earnings=(total := df.total_earnings.sum()),
            collected_earnings=(
                collected := df[df.payment_date <= today].total_earnings.sum()
            ),
            to_collect_earnings=total - collected,
            mean_yoc=df.yoc.mean(),
            mean_yoc_current_month=_last_months(1).yoc.mean(),
            **{f"mean_yoc_{n}m": _last_months(n).yoc.mean() for n in [3, 6, 12]},
        )

    def monthly_index_yoc(
        self, target_asset: str = None, date_col: str = "payment_date"
    ):
        return self._get_and_validate(
            f"monthly_index_yoc_{target_asset}_{date_col}",
            MonthlyIndexYoC,
            self._monthly_index_yoc,
            target_asset,
            date_col,
        )

    def monthly_yoc(self, target_asset: str = None, date_col: str = "payment_date"):
        return self._get_and_validate(
            f"monthly_yoc_{target_asset}_{date_col}",
            MonthlyYoC,
            self._monthly_yoc,
            target_asset,
            date_col,
        )

    def monthly_earning(
        self, kind_col: str = "asset_kind", date_col: str = "payment_date"
    ) -> DataFrame[MonthlyEarning]:
        return self._get_and_validate(
            f"monthly_earning_{kind_col}_{date_col}",
            MonthlyEarning,
            self._monthly_earning,
            kind_col,
            date_col,
        )

    def earning_yield(self) -> DataFrame[EarningYield]:
        return self._get_and_validate(
            "earning_yield", EarningYield, self._earning_yield
        )

    def _get_and_validate(
        self, key: str, model, create_fn: Callable, *create_args, **create_kwargs
    ):
        value = self._get_from_cache(key, create_fn, *create_args, **create_kwargs)
        return model.validate(value)

    def _monthly_index_yoc(self, target_asset: str, date_col: str) -> pd.DataFrame:
        # Fetch YoC
        yoc = self.monthly_yoc(target_asset, date_col)
        yoc["date"] = pd.to_datetime(yoc.reference_date)

        # Fetch economic data
        stmt = (
            sa.select(
                EconomicData.index,
                EconomicData.reference_date.label("date"),
                EconomicData.percentage_change.label("change"),
            )
            .where(EconomicData.index.in_([EconomicIndex.ipca, EconomicIndex.cdi]))
            .where(EconomicData.reference_date.in_(yoc.reference_date.unique()))
        )
        economic = pd.read_sql(
            str(stmt.compile(self._engine, compile_kwargs=dict(literal_binds=True))),
            self._engine,
        ).pivot(index="date", columns="index", values="change")
        economic["cdb"] = 0.85 * economic.cdi
        economic.index = pd.to_datetime(economic.index)

        # Join DataFrames
        df = yoc.join(economic, on="date").drop(columns="date")

        # Fill NaNs with zeroes
        cols = ["cdi", "cdb", "ipca"]
        df.loc[:, cols] = df[cols].fillna(0.0)

        # Return df
        return df

    def _monthly_yoc(self, target_asset: str = None, date_col: str = "payment_date"):
        df = self.earning_yield()[["b3_code", date_col, "asset_kind", "yoc"]].rename(
            columns={date_col: "reference_date", "asset_kind": "group"}
        )
        df["reference_date"] = pd.to_datetime(df.reference_date) + pd.offsets.MonthEnd(
            0
        )
        df["group"] = df.group.map(lambda g: AssetKind.from_value(g).value)

        # Find target rows
        df_target = df.copy()
        if target_asset is not None:
            df_target = df_target[df_target.b3_code == target_asset]
            df_target["group"] = target_asset
        else:
            df_target["group"] = "Todos"
        df_target = df_target.drop(columns="b3_code")

        # Find target YoC
        group_cols = ["reference_date", "group"]
        df_target = df_target.groupby(group_cols).mean().reset_index()

        # Find YoC for other groups
        df_groups = df.drop(columns="b3_code").groupby(group_cols).mean().reset_index()

        # Add global group if it isn't target
        if target_asset is not None:
            df_groups = pd.concat(
                [
                    df_groups,
                    df.drop(columns=["b3_code", "group"])
                    .groupby("reference_date")
                    .mean()
                    .reset_index()
                    .assign(group="Todos"),
                ]
            )

        # Concat DataFrames and set dtypes
        df = pd.concat([df_groups, df_target])
        df["reference_date"] = df.reference_date.dt.date

        return df

    def _monthly_earning(
        self, kind_col: str = "asset_kind", date_col: str = "payment_date"
    ) -> pd.DataFrame:
        df = self.earning_yield()[[kind_col, date_col, "total_earnings"]].rename(
            columns={kind_col: "group", date_col: "reference_date", kind_col: "group"}
        )
        df["reference_date"] = (
            pd.to_datetime(df.reference_date) + pd.offsets.MonthEnd(0)
        ).dt.date
        df["group"] = df.group.map(
            lambda g: (
                EarningKind.from_value(g)
                if kind_col == "kind"
                else AssetKind.from_value(g)
            ).value
        )

        # Aggregate by <date, kind> and sum
        df = df.groupby(["reference_date", "group"]).sum().reset_index()

        # Return aggregate
        return df

    def _earning_yield(self) -> pd.DataFrame:
        dtypes = self._model_to_dtypes(EarningYield)
        stmt = (
            sa.select(
                Earning.id.label("earning_id"),
                Earning.asset_b3_code.label("b3_code"),
                Earning.hold_date,
                Earning.payment_date,
                Earning.value_per_share,
                Earning.kind,
                Asset.kind.label("asset_kind"),
                Earning.ir_percentage.label("ir"),
                Earning.value_per_share,
                Transaction.value_per_share.label("share_price"),
                Transaction.shares,
                Transaction.kind.label("transaction_kind"),
            )
            .select_from(Earning)
            .join(Earning.asset)
            .join(Earning.right_to_earnings)
        )
        df = pd.read_sql(
            str(stmt.compile(self._engine)),
            self._engine,
        )

        # Degenerate case:
        if df.empty:
            return pd.DataFrame(columns=list(dtypes)).astype(dtypes)

        # Data cleansing/filtering
        df = df.drop(columns=["value_per_share__1"])
        df = df.astype(
            {c: dtypes[c] if c in dtypes else df.dtypes[c] for c in df.columns}
        )

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
            "asset_kind",
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

        # Query economic index data for payment date
        df["economic_date"] = (
            pd.to_datetime(df.hold_date) + pd.offsets.MonthEnd(0)
        ).dt.date
        stmt = (
            sa.select(
                EconomicData.index,
                EconomicData.reference_date.label("economic_date"),
                EconomicData.percentage_change.label("change"),
            )
            .where(EconomicData.index.in_([EconomicIndex.ipca, EconomicIndex.cdi]))
            .where(EconomicData.reference_date.in_(df.economic_date.unique()))
        )
        df_economic = (
            pd.read_sql(
                str(
                    stmt.compile(self._engine, compile_kwargs=dict(literal_binds=True))
                ),
                self._engine,
            )
            .pivot(index="economic_date", columns="index", values="change")
            .rename(columns=dict(cdi="cdi_on_hold_month", ipca="ipca_on_hold_month"))
        )

        # Join DataFrame
        df.economic_date = df.economic_date.map(lambda d: d.isoformat())
        df = df.join(df_economic, on="economic_date")
        df = df.drop(columns="economic_date")

        # Maybe df_economic was empty for the target dates, we should ensure
        #   cdi and ipca appear as None
        for c in ["cdi_on_hold_month", "ipca_on_hold_month"]:
            if c not in df.columns:
                df[c] = float("nan")

        return df

    def _model_to_dtypes(self, model) -> dict:
        schema = model.to_schema()
        return {
            column_name: column_type.dtype.type.name
            for column_name, column_type in schema.columns.items()
        }

    def _get_from_cache(
        self, key: str, create_fn: Callable, *create_args, **create_kwargs
    ):
        # Should invalidate cache?
        db_meta = self._db_state()
        cache_meta = self._cache.get("__db_meta", None)
        timestamp = datetime.now()
        since_last_update = timestamp - self._cache["__last_update"]

        # If db changed or TTL expired, renew cache
        if db_meta != cache_meta or since_last_update.total_seconds() > self._cache_ttl:
            print("Invalidated")
            keys = list(self._cache)
            for k in keys:
                del self._cache[k]
            self._cache["__db_meta"] = db_meta
            self._cache["__last_update"] = timestamp

        # Maybe add to cache
        if key not in self._cache:
            self._cache[key] = create_fn(*create_args, **create_kwargs)

        # Return cached
        return self._cache[key]

    def _db_state(self) -> dict:
        with sa_orm.Session(self._engine) as session:
            return {
                "n_entities": sum(
                    session.query(e).count()
                    for e in [Asset, Transaction, Earning, EconomicData]
                ),
            }
