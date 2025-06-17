"""Classe Router responsável por
organizar notificações e enviar
para as respectivas filas.
"""

import logging
import re

import pika
from engine.utils.messages import AnalyticEvent
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class Router:
    def __init__(
        self,
        notification_queue: str,
        yoc_queue: str,
        connection_url: str,
        notification_exchange: str = "",
        yoc_exchange: str = "",
    ):
        self._conn = None
        self._ch = None
        self._url = connection_url
        self._notif_queue = notification_queue
        self._notif_exchange = notification_exchange
        self._yoc_queue = yoc_queue
        self._yoc_exchange = yoc_exchange
        self._notification_pattern = re.compile(r"\[(?P<source>.+)\] (?P<message>.+)")
        self._wallet_pattern = re.compile(
            r"(?P<operation>CREATE|UPDATE|DELETE) (?P<entity>\w+) WITH ID (?P<target>\w+).*",
        )
        self._dashboard_pattern = re.compile(
            r"QUERY (?P<kind>ASSET|GROUP) (?P<entity>\w+) ON (?P<table>\w+)",
        )

    def run(self):
        try:
            self._setup_connection()
            self._ch.start_consuming()
        finally:
            self._stop_connection()

    def _setup_connection(self):
        assert self._conn is None
        self._conn = pika.BlockingConnection(pika.URLParameters(self._url))
        self._ch = self._conn.channel()

        # Setup notification queue
        self._ch.queue_declare(queue=self._notif_queue)
        self._ch.basic_consume(self._notif_queue, self._on_notification, auto_ack=False)

        # Setup yoc queue
        self._ch.queue_declare(queue=self._yoc_queue)

    def _stop_connection(self):
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
        # Only process text events
        if header_frame.content_type == "text/plain":
            # Read text
            data = body.decode(header_frame.content_encoding)
            logger.debug(f'Received message: "{data}"')

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

        # Work has been done
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def _process_message(self, source: str, message: str) -> AnalyticEvent | None:
        # Parse source and message to expected format
        data = dict(query_information=dict(), update_information=dict())
        match, key = None, ""
        if source == "wallet-api":
            data["trigger"] = "wallet_update"
            match = self._wallet_pattern.match(message)
            key = "update_information"
        elif source == "dashboard":
            data["trigger"] = "dashboard_query"
            match = self._dashboard_pattern.match(message)
            key = "query_information"

        # If matched, add to data
        if match:
            data[key] = match.groupdict({})

        try:
            return AnalyticEvent(**data)
        except ValidationError as e:
            logger.warning(e)
            return None

    def _send_event(self, event: AnalyticEvent):
        self._ch.basic_publish(
            exchange=self._yoc_exchange,
            routing_key=self._yoc_queue,
            body=event.model_dump_json(indent=2),
            properties=pika.BasicProperties(
                content_type="application/json",
                content_encoding="utf-8",
            ),
        )
