"""Gerenciador do estado da
página de posições de investimento.
"""

import logging
from datetime import date, timedelta

import pandas as pd
from app.utils.state import PageState
from app.wallet.client import WalletApi

logger = logging.getLogger(__name__)


class PositionsState(PageState):
    def __init__(self):
        self._current_history_n_months = None
        self._today = date.today()
        super().__init__("positions")

    def update_state(self, update_history_for_n_months: int = 3):
        # Do we need to initialize?
        initialize = not self.variables.get("initialized", False)

        # Maybe we should update due to new day?
        today = date.today()
        should_update = self._today != today

        # If should initialize or update
        if initialize or should_update:
            self.variables.current_position = WalletApi.get_position(today)

        if (
            update_history_for_n_months > 0
            and update_history_for_n_months != self._current_history_n_months
        ) or should_update:
            self._current_history_n_months = update_history_for_n_months
            self.variables.history = pd.concat(
                [
                    self.variables.current_position.assign(month=today),
                    *[
                        WalletApi.get_position(d).assign(month=d)
                        for d in self._n_previous_months(
                            today, self._current_history_n_months
                        )
                    ],
                ],
            )

        # Update state
        if initialize:
            self.variables.initialized = True

        if should_update:
            self._today = today

    @staticmethod
    def _n_previous_months(ref_date: date, n: int) -> list[date]:
        dates = [ref_date]
        for i in range(1, n + 1):
            prev = dates[-1]
            dates.append(prev - timedelta(prev.day))
        return dates[1:]
