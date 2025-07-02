"""Gerenciador de estado da página
home.
"""

import logging
from datetime import date

import pandas as pd
from app.analytics import constants, db
from app.utils.state import PageState
from invest_earning.database.analytic.earning_yield import EarningYield

logger = logging.getLogger(__name__)


class HomeState(PageState):
    _EY_COLUMNS = [c.key for c in EarningYield.__table__.columns]

    def __init__(self):
        super().__init__("home")
        self.variables.today = date.today()

    def update_state(self):
        # Get today
        today = date.today()

        # Is page initialized?
        initialize = not self.variables.get("initialized", False)

        # Maybe update earning yield and others
        if initialize or today != self.variables.today:
            with db.get_session() as session:

                # Get earning yield for previous N months
                self.variables.earning_yield = pd.DataFrame(
                    [
                        {k: getattr(ey, k) for k in self._EY_COLUMNS}
                        for ey in session.query(EarningYield)
                        .where(EarningYield.shares > 0)
                        .all()
                    ],
                    columns=self._EY_COLUMNS,
                )

            # Map enum columns
            for c in ["asset_kind", "earning_kind"]:
                self.variables.earning_yield[c] = self.variables.earning_yield[c].map(
                    lambda v: v.value
                )

            # Get global metrics
            df = self.variables.earning_yield
            self.variables.metrics = dict(
                n_assets_with_earnings=df.b3_code.nunique(),
                total_earnings=(total := df.total_earnings.sum()),
                collected_earnings=(
                    collected := df[df.payment_date <= today].total_earnings.sum()
                ),
                to_collect_earnings=total - collected,
                mean_yoc=df.yoc.mean(),
                **{
                    f"mean_yoc_{n}m": self._last_months(
                        df, "payment_date", n
                    ).yoc.mean()
                    for n in [1, 3, 6, 12]
                },
            )
            del df

            # Get asset codes
            self.variables.asset_codes = sorted(
                self.variables.earning_yield.b3_code.unique().tolist()
            )

            # Get minimum and max dates
            cols = ["hold_date", "payment_date"]
            self.variables.min_date = self.variables.earning_yield[cols].min(axis=None)
            self.variables.max_date = self.variables.earning_yield[cols].max(axis=None)

            # Set initialized flag
            self.variables.initialized = True

        # Get current month ey
        self.variables.current_month_ey = self.variables.earning_yield[
            self.variables.earning_yield.payment_date.map(
                lambda d: (d.month == today.month) and (d.year == today.year)
            )
        ]

        # Get filters parameters
        try:
            asset = self.components["filter_asset"].get()
            earning_kind = self.components["filter_earning_kind"].get()
            date_col = {"Pagamento": "payment_date", "Custódia": "hold_date"}.get(
                self.components["filter_date_kind"].get()
            )
            start_date = self.components["filter_start_date"].get()
            end_date = self.components["filter_end_date"].get()
        except:
            asset = "Todos"
            earning_kind = constants.EarningKinds
            date_col = "payment_date"
            start_date = self.variables.min_date
            end_date = self.variables.max_date

        # Apply filters
        df = self.variables.earning_yield
        if not df.empty and asset != "Todos":
            df = df[df.b3_code == asset]

        if not df.empty:
            df = df[df.earning_kind.isin(earning_kind)]
            df = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]

        # Make the filtered version available
        self.variables.filtered_ey = df

        # Make today available
        self.variables.today = today

    @staticmethod
    def _last_months(df: pd.DataFrame, dt: str, n: int):
        dt = pd.to_datetime(df[dt])

        def _between(start, end):
            return df[(dt >= start) & (dt <= end)]

        today = pd.to_datetime(date.today())
        start = today + pd.offsets.MonthBegin(-n)
        end = today + pd.offsets.MonthEnd(0)
        return _between(start, end)
