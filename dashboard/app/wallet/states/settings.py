"""Gerenciador do estado da página
de configurações da carteira."""

import logging

from app.utils.state import PageState
from app.wallet import constants
from app.wallet.client import WalletApi

logger = logging.getLogger(__name__)


class SettingState(PageState):
    def __init__(self):
        super().__init__("settings")

    def update_state(
        self,
        update_assets: bool = False,
        update_transactions: bool = False,
        update_earnings: bool = False,
        update_economic_data: bool = False,
    ):
        # Find current state of componentes
        components = self.components

        # Is page initialized?
        initialize = not self._state.get("initialized", False)

        # Update assets
        if update_assets or initialize:
            self._state.assets = WalletApi.list_assets().sort_values(
                ["kind", "b3_code"]
            )
            self._state.asset_codes = sorted(
                self._state.assets.b3_code.sort_values().tolist()
            )
            logger.debug(
                "API returned %d assets (colums=%s).",
                len(self._state.assets),
                self._state.assets.columns,
            )

        # Update transactions
        if update_transactions or initialize:
            self._state.transactions = WalletApi.list_transactions().sort_values(
                "date", ascending=False
            )
            logger.debug(
                "API returned %d transactions (colums=%s).",
                len(self._state.transactions),
                self._state.transactions.columns,
            )

        # Update earnings
        if update_earnings or initialize:
            self._state.earnings = WalletApi.list_earnings().sort_values(
                "payment_date", ascending=False
            )
            logger.debug(
                "API returned %d earnings (colums=%s).",
                len(self._state.earnings),
                self._state.earnings.columns,
            )
        # Update economic data
        if update_economic_data or initialize:
            self._state.economic = WalletApi.list_economic().sort_values(
                "reference_date", ascending=False
            )
            logger.debug(
                "API returned %d economic entries (colums=%s).",
                len(self._state.economic),
                self._state.economic.columns,
            )

        # Apply filters
        for default, st_key in zip(
            [
                ("Todos", constants.TransactionKinds),
                (
                    "Todos",
                    constants.EarningKinds,
                ),
            ],
            ["transaction", "earning"],
        ):
            try:
                code = components[f"{st_key}_filter_code"]
                kind = components[f"{st_key}_filter_kind"]
            except:
                code, kind = default

            def _filter(row) -> bool:
                return (code == "Todos" or row.asset_b3_code == code) and (
                    row.kind in kind
                )

            key = f"{st_key}s"
            if not self._state[key].empty:
                self._state[key] = self._state[key][
                    self._state[key].apply(_filter, axis=1)
                ]

        # If we initialized, set flag
        if initialize:
            self._state.initialized = True
