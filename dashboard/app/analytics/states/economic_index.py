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


class EconomicIndexState(PageState):
    _EY_COLUMNS = [c.key for c in EarningYield.__table__.columns]

    def __init__(self):
        super().__init__("economic_index")
        self.variables.today = date.today()

    def update_state(self):
        today = date.today()

        # Is page initialized?
        initialize = not self.variables.get("initialized", False)

        if initialize or today != self.variables.today:
            with db.get_session() as session:
                # Get global metrics
                self.variables.metrics = dict()
                self.variables.earning_yield = pd.DataFrame(
                    [
                        {k: getattr(ey, k) for k in self._EY_COLUMNS}
                        for ey in session.query(EarningYield).all()
                    ],
                    columns=self._EY_COLUMNS,
                )

            # Map enum columns
            for c in ["asset_kind", "earning_kind"]:
                self.variables.earning_yield[c] = self.variables.earning_yield[c].map(
                    lambda v: v.value
                )

            # Metadata
            self.variables.asset_codes = sorted(
                self.variables.earning_yield.b3_code.unique().tolist()
            )
            cols = ["hold_date", "payment_date"]
            self.variables.min_date = earning_yield[cols].min(axis=None)
            self.variables.max_date = earning_yield[cols].max(axis=None)

            # Update others
            self.variables.initialized = True
            self.variables.today = today
