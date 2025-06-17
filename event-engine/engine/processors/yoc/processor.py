"""Processador de Yield On Cost (YoC)."""

import json
import logging

import pika
import sqlalchemy as sa

from engine.utils.messages import (
    AnalyticEvent,
    AnalyticTable,
    AnalyticTrigger,
    DatabaseOperation,
    QueryInformation,
    QueryKind,
    WalletEntity,
    WalletUpdateInformation,
)

logger = logging.getLogger(__name__)


class YoCProcessor:
    def __init__(
        self, queue: str, broker_url: str, wallet_db_url: str, analytic_db_url: str
    ):
        self._conn, self._ch = None, None
        self._wallet_engine = None
        self._analytic_engine = None
        self._broker_url = broker_url
        self._queue = queue
        self._wallet_url = wallet_db_url
        self._analytic_url = analytic_db_url

    def run(self):
        try:
            logger.debug("Setting up connection for YoC processor...")
            self._setup_connection()
            logger.info(
                "YoC processor has started. Listening to '%s'.",
                self._queue,
            )
            self._ch.start_consuming()
        finally:
            self._stop_connection()

    def _setup_connections(self):
        assert self._conn is None
        assert self._wallet_session is None
        assert self._analytic_session is None

        self._conn = pika.BlockingConnection(pika.URLParameters(self._broker_url))
        self._ch = self._conn.channel()
        self._wallet_engine = sa.create_engine(self._wallet_url)
        self._analytic_engine = sa.create_engine(self._analytic_url)

        # Setup broker queue
        self._ch.queue_declare(queue=self._queue, durable=True)
        self._ch.basic_consume(self._queue, self._on_notification, auto_ack=False)

    def _stop_connections(self):
        if self._ch is not None:
            self._ch.stop_consuming()
            self._ch = None

        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _on_notification(
        self,
        channel: pika.channel.Channel,
        method_frame: pika.spec.Basic.Deliver,
        header_frame: pika.spec.BasicProperties,
        body: bytes,
    ):
        if header_frame.content_type == "application/json":
            event = AnalyticEvent(
                **json.loads(body.decode(header_frame.content_encoding))
            )

            # Select processing function
            if event.trigger == AnalyticTrigger.wallet_update:
                self._process_wallet_update(event.update_information)
            elif event.trigger == AnalyticTrigger.dashboard_query:
                self._process_dashboard_query(event.query_information)

        # Work has been done
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def _process_wallet_update(self, event: WalletUpdateInformation):
        match event.operation:
            case DatabaseOperation.CREATED:
                match event.entity:
                    case WalletEntity.earning:
                        ...
                    case _:
                        return
            case DatabaseOperation.UPDATED:
                ...
            case DatabaseOperation.DELETED:
                ...

    def _process_dashboard_query(self, event: QueryInformation): ...
