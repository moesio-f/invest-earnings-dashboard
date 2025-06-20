"""Configurações para o acesso
ao banco de dados.
"""

import logging

import pika
import sqlalchemy as sa
from invest_earning.database.analytic import EarningYield

from .config import ANALYTICS_CONFIG as config

logger = logging.getLogger(__name__)

# Private engine for sessions
_engine = sa.create_engine(config.ANALYTIC_DB_URL)


def get_session(**session_kwargs) -> sa.orm.Session:
    session = sa.orm.Session(_engine, **session_kwargs)

    @sa.event.listens_for(session, "do_orm_execute")
    def _notify_queue(state: sa.orm.ORMExecuteState):
        # Check whether entity is known for requiring notification
        statement: sa.orm.Query = state.statement
        description = statement.column_descriptions
        ents = set(d.get("entity", None) for d in description)

        # If entity is involved, notify
        if EarningYield in ents:
            # Notification properties
            kind = "GROUP"
            entity = "all"
            table = "earning_yield"

            # Find target entity based on heuristic
            # TODO:. use parser to always find targets
            try:
                where = statement.whereclause
                if where is not None:
                    # Get children
                    children = list(where.get_children())

                    # Two main scenarios:
                    #   1. Condition + bind
                    #   2. Multiple conditions
                    if hasattr(children[0], "name"):
                        col, bind = children
                        entity = bind.value
                        match col.name:
                            case "b3_code":
                                kind = "ASSET"
                            case "asset_kind":
                                kind = "GROUP"
                    else:
                        for child in children:
                            col, bind = child.get_children()
                            match col.name:
                                case "b3_code":
                                    kind = "ASSET"
                                case "asset_kind":
                                    kind = "GROUP"
                                case _:
                                    continue
                            entity = bind.value
            except:
                logger.warning(
                    "Couldn't infer entity/kind from heuristic. "
                    "Sending notification for GROUP/all instead."
                )

            # Create new connection to broker
            # TODO:. make connection persistent and shared
            conn = pika.BlockingConnection(pika.URLParameters(config.BROKER_URL))

            # Open communication channel
            ch = conn.channel()
            ch.queue_declare("", auto_delete=True)

            # Send message
            ch.basic_publish(
                exchange="",
                routing_key=config.NOTIFICATION_QUEUE,
                body=f"QUERIED {kind} {entity} ON {table}",
                properties=pika.BasicProperties(
                    content_type="text/plain",
                    content_encoding="utf-8",
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
            )

            # Close communication
            ch.close()
            conn.close()

    return session
