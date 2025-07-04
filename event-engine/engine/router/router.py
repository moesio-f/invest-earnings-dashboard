"""Classe Router responsável por
organizar notificações e enviar
para as respectivas filas.
"""

import logging
import re

import pika
from engine.utils.messages import AnalyticEvent, AnalyticTrigger
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class Router:
    def __init__(
        self,
        notification_queue: str,
        yoc_queue: str,
        broker_url: str,
    ):
        self._conn = None
        self._ch = None
        self._url = broker_url
        self._notif_queue = notification_queue
        self._yoc_queue = yoc_queue
        self._notification_pattern = re.compile(r"\[(?P<source>.+)\] (?P<message>.+)")
        self._wallet_pattern = re.compile(
            r"(?P<operation>CREATED|UPDATED|DELETED) (?P<entity>\w+) WITH ID (?P<entity_id>\w+)(?: WITH REFERENCE TO (?P<reference>\w+) WITH ID (?P<reference_id>\w+))?",
        )
        self._dashboard_pattern = re.compile(
            r"QUERIED (?P<kind>ASSET|GROUP) (?P<entity>\w+) ON (?P<table>\w+)",
        )
        self._price_pattern = re.compile(
            r"SCRAPPED PRICES FOR asset WITH ID (?P<asset_id>\w+) BETWEEN (?P<start_date>.+) AND (?P<end_date>.+)"
        )

    def run(self):
        try:
            logger.debug("Setting up connection for router...")
            self._setup_connection()
            logger.info(
                "Router has started. Listening to '%s' and publishing to '%s'.",
                self._notif_queue,
                self._yoc_queue,
            )
            self._ch.start_consuming()
        finally:
            self._stop_connection()

    def _setup_connection(self):
        assert self._conn is None
        self._conn = pika.BlockingConnection(pika.URLParameters(self._url))
        self._ch = self._conn.channel()

        # Setup notification queue
        self._ch.queue_declare(queue=self._notif_queue, durable=True)
        self._ch.basic_consume(self._notif_queue, self._on_notification, auto_ack=False)

    def _stop_connection(self):
        if self._ch is not None:
            self._ch.stop_consuming()
            self._ch.close()
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
        # Only process text events
        if header_frame.content_type == "text/plain":
            # Read text
            data = body.decode(header_frame.content_encoding)
            logger.debug(f'Received message from queue: "{data}"')

            # Check formatting
            match = self._notification_pattern.match(data)

            # If follows expected format, proceed
            if match:
                # Get source system that sent the message
                source = match.group("source")

                # Get message contents
                message = match.group("message")

                # Convert to analytic event
                event = self._process_message(source, message)

                # If is an analytic event, send to appropriate processor
                if event:
                    self._send_event(event)
                    logger.debug(f"Sent event:\n{event.model_dump_json(indent=2)}")
        else:
            logger.debug(
                "Message content_type (%s) didn't match "
                "expected type (text/plain). Silently ignored.",
                header_frame.content_type,
            )

        # Work has been done
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def _process_message(self, source: str, message: str) -> AnalyticEvent | None:
        # Parse source and message to expected format
        data = dict(query_information=dict(), update_information=dict())
        match, key = None, ""
        if source == "wallet-api":
            data["trigger"] = AnalyticTrigger.wallet_update
            match = self._wallet_pattern.match(message)
            key = "update_information"
        elif source == "dashboard":
            data["trigger"] = AnalyticTrigger.dashboard_query
            match = self._dashboard_pattern.match(message)
            key = "query_information"
        elif source == "market-scraper":
            data["trigger"] = AnalyticTrigger.price_scraper
            match = self._price_pattern.match(message)
            key = "price_scraper_information"

        # If matched, add to data
        if match:
            data[key] = match.groupdict()

        try:
            return AnalyticEvent(**data)
        except ValidationError as e:
            logger.warning(f"Ignored source message due to validation error: {e}")
            return None

    def _send_event(self, event: AnalyticEvent):
        self._ch.basic_publish(
            exchange="",
            routing_key=self._yoc_queue,
            body=event.model_dump_json(indent=2),
            properties=pika.BasicProperties(
                content_type="application/json",
                content_encoding="utf-8",
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
        )
