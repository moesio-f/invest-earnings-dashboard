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
        # Is page initialized?
        initialize = not self.variables.get("initialized", False)

        # Update assets
        if update_assets or initialize:
            self.variables.assets = WalletApi.list_assets().sort_values(
                ["kind", "b3_code"]
            )
            self.variables.asset_codes = sorted(
                self.variables.assets.b3_code.sort_values().tolist()
            )
            logger.debug(
                "API returned %d assets (colums=%s).",
                len(self.variables.assets),
                self.variables.assets.columns,
            )

        # Update transactions
        if update_transactions or initialize:
            self.variables.transactions = WalletApi.list_transactions().sort_values(
                "date", ascending=False
            )
            logger.debug(
                "API returned %d transactions (colums=%s).",
                len(self.variables.transactions),
                self.variables.transactions.columns,
            )

        # Update earnings
        if update_earnings or initialize:
            self.variables.earnings = WalletApi.list_earnings().sort_values(
                "payment_date", ascending=False
            )
            logger.debug(
                "API returned %d earnings (colums=%s).",
                len(self.variables.earnings),
                self.variables.earnings.columns,
            )
        # Update economic data
        if update_economic_data or initialize:
            self.variables.economic = WalletApi.list_economic().sort_values(
                "reference_date", ascending=False
            )
            logger.debug(
                "API returned %d economic entries (colums=%s).",
                len(self.variables.economic),
                self.variables.economic.columns,
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
                code = self.components[f"{st_key}_filter_code"].get()
                kind = self.components[f"{st_key}_filter_kind"].get()
            except:
                code, kind = default

            def _filter(row) -> bool:
                return (code == "Todos" or row.asset_b3_code == code) and (
                    row.kind in kind
                )

            key = f"{st_key}s"
            filtered_key = f"filtered_{key}"
            self.variables[filtered_key] = self.variables[key]
            if len(self.variables[filtered_key]) > 0:
                self.variables[filtered_key] = self.variables[filtered_key][
                    self.variables[filtered_key].apply(_filter, axis=1)
                ]

        # If we initialized, set flag
        if initialize:
            self.variables.initialized = True
