"""Dispatcher de notificações."""

import re
from enum import Enum

import pika
from fastapi import Depends
from invest_earning.database.wallet import Asset, Earning, EconomicData, Transaction

from .config import DISPATCHER_CONFIG


class NotificationDispatcher:
    class Operation(Enum):
        CREATED = "CREATED"
        UPDATED = "UPDATED"
        DELETED = "DELETED"

    def __init__(self):
        self._conn = pika.BlockingConnection(
            pika.URLParameters(DISPATCHER_CONFIG.connection_url)
        )
        self._ch = self._conn.channel()

        # Create temporary queue
        self._ch.queue_declare("", auto_delete=True)

    def close(self):
        self._ch.close()
        self._conn.close()

    def notify_asset_create(self, asset: Asset):
        self._notify(self.Operation.CREATED, Asset, asset.b3_code)

    def notify_asset_delete(self, asset: Asset):
        self._notify(self.Operation.DELETED, Asset, asset.b3_code)

    def notify_earning_create(self, earning: Earning):
        self._notify(
            self.Operation.CREATED, Earning, earning.id, Asset, earning.asset_b3_code
        )

    def notify_earning_update(self, earning: Earning, updated_fields: dict[str, tuple]):
        self._notify(
            self.Operation.UPDATED, Earning, earning.id, Asset, earning.asset_b3_code
        )

    def notify_earning_delete(self, earning: Earning):
        self._notify(
            self.Operation.DELETED, Earning, earning.id, Asset, earning.asset_b3_code
        )

    def notify_transaction_create(self, transaction: Transaction):
        self._notify(
            self.Operation.CREATED,
            Transaction,
            transaction.id,
            Asset,
            transaction.asset_b3_code,
        )

    def notify_transaction_update(
        self, transaction: Transaction, updated_fields: dict[str, tuple]
    ):
        self._notify(
            self.Operation.UPDATED,
            Transaction,
            transaction.id,
            Asset,
            transaction.asset_b3_code,
        )

    def notify_transaction_delete(self, transaction: Transaction):
        self._notify(
            self.Operation.DELETED,
            Transaction,
            transaction.id,
            Asset,
            transaction.asset_b3_code,
        )

    def notify_economic_add(self, economic: EconomicData):
        self._notify(
            self.Operation.CREATED, EconomicData, self._economic_pk_to_str(economic)
        )

    def notify_economic_delete(self, economic: EconomicData):
        self._notify(
            self.Operation.DELETED, EconomicData, self._economic_pk_to_str(economic)
        )

    def _notify(
        self,
        operation: Operation,
        ent_cls: type[Earning | EconomicData | Transaction | Asset],
        ent_id: str | int,
        ref_cls: type[Earning | EconomicData | Transaction | Asset] = None,
        ref_id: str | int = None,
    ):
        # Format notification message
        ent_name = self._normalize_name(ent_cls.__name__)
        data = f"[wallet-api] {operation.value} {ent_name} WITH ID {ent_id}"

        # Maybe has a reference?
        if ref_cls is not None:
            assert ref_id is not None
            ref_name = self._normalize_name(ref_cls.__name__)
            data = f"{data} WITH REFERENCE TO {ref_name} WITH ID {ref_id}"

        # Publish into queue
        self._ch.basic_publish(
            exchange="",
            routing_key=DISPATCHER_CONFIG.notification_queue,
            body=data,
            properties=pika.BasicProperties(
                content_type="text/plain",
                content_encoding="utf-8",
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
        )

    @staticmethod
    def _economic_pk_to_str(economic: EconomicData) -> str:
        return f"{economic.index}_{economic.reference_date.strftime('%Y_%m_%d')}"

    @staticmethod
    def _normalize_name(name: str) -> str:
        return "_".join(re.findall(r"[A-Z][a-z]+", name)).lower()


def get_dispatcher() -> NotificationDispatcher:
    dispatcher = NotificationDispatcher()
    yield dispatcher
    dispatcher.close()


RequiresDispatcher = Depends(get_dispatcher)
