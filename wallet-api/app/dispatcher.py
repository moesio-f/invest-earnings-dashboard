"""Dispatcher de notificações."""

from invest_earning.database.wallet import (
    Asset,
    Earning,
    EconomicData,
    Transaction,
)


class _NotificationDispatcher:
    def notify_asset_create(self, asset: Asset): ...

    def notify_asset_delete(self, asset: Asset): ...

    def notify_earning_create(self, earning: Earning): ...

    def notify_earning_update(
        self, earning: Earning, updated_fields: dict[str, tuple]
    ): ...

    def notify_earning_delete(self, earning: Earning): ...

    def notify_transaction_create(self, transaction: Transaction): ...

    def notify_transaction_update(
        self, transaction: Transaction, updated_fields: dict[str, tuple]
    ): ...

    def notify_transaction_delete(self, earning: Earning): ...

    def notify_economic_add(self, economic: EconomicData): ...

    def notify_economic_delete(self, economic: EconomicData): ...


NotificationDispatcher = _NotificationDispatcher()
