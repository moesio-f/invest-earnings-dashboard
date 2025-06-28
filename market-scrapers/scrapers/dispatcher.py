"""Dispatcher de notificações."""

from datetime import date

import pika

from .config import CONFIG as config


class _NotificationDispatcher:
    def __init__(self):
        self._conn = pika.BlockingConnection(pika.URLParameters(config.broker_url))
        self._ch = self._conn.channel()

        # Create temporary queue
        self._ch.queue_declare("", auto_delete=True)

    def close(self):
        if self._ch is not None:
            self._ch.close()
            self._ch = None

        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def notify_extraction(self, b3_code: str, start_date: date, end_date: date):
        # Format notification message
        msg = (
            "[market-scraper] SCRAPPED PRICES FOR asset "
            f"WITH ID {b3_code} BETWEEN {start_date.isoformat()} "
            f"AND {end_date.isoformat()}"
        )

        # Publish into queue
        self._ch.basic_publish(
            exchange="",
            routing_key=config.notification_queue,
            body=msg,
            properties=pika.BasicProperties(
                content_type="text/plain",
                content_encoding="utf-8",
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
        )


Dispatcher = _NotificationDispatcher()
