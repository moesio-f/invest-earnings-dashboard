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
from invest_earning.database.analytic import EarningYield
from invest_earning.database.wallet import (
    Asset,
    Earning,
    EconomicData,
    EconomicIndex,
    Position,
    Transaction,
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
            self._setup_connections()
            logger.info(
                "YoC processor has started. Listening to '%s'.",
                self._queue,
            )
            self._ch.start_consuming()
        finally:
            self._stop_connections()

    def _setup_connections(self):
        assert self._conn is None
        assert self._wallet_engine is None
        assert self._analytic_engine is None

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
        if header_frame.content_type == "application/json":
            event = AnalyticEvent(
                **json.loads(body.decode(header_frame.content_encoding))
            )
            logger.info("Procesing event:\n%s", event.model_dump_json(indent=2))

            # Select processing function
            match event.trigger:
                case AnalyticTrigger.wallet_update:
                    self._process_wallet_update(event.update_information)
                case AnalyticTrigger.dashboard_query:
                    self._process_dashboard_query(event.query_information)

        # Work has been done
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def _process_wallet_update(self, event: WalletUpdateInformation):
        match event.operation:
            case DatabaseOperation.CREATED:
                match event.entity:
                    case WalletEntity.earning:
                        logger.debug("Creating single entry for new earning.")
                        self._create_or_update_earning_yield(int(event.entity_id))
                    case WalletEntity.transaction:
                        # A transaction might affect a variable number
                        #   of yields. We should manage sessions to guarantee
                        #   all yields are updated or none at all.
                        wsession = sa.orm.Session(
                            self._wallet_engine, expire_on_commit=False
                        )
                        asession = sa.orm.Session(self._analytic_engine)
                        affected = self._get_affected_earnings(
                            int(event.entity_id), wallet_session=wsession
                        )

                        # For each affected earning, update
                        logger.debug(
                            "Transaction affects %d earnings. Create or update "
                            "entry for each one in a single transaction.",
                            len(affected),
                        )
                        for earning_id in affected:
                            self._create_or_update_earning_yield(
                                earning_id,
                                wallet_session=wsession,
                                analytic_session=asession,
                            )

                        # Commit changes and close sessions
                        logger.debug(
                            "Commiting changes of affected earnings to database."
                        )
                        wsession.close()
                        asession.commit()
                        asession.close()
            case DatabaseOperation.UPDATED:
                ...
            case DatabaseOperation.DELETED:
                ...

    def _process_dashboard_query(self, event: QueryInformation): ...

    def _get_affected_earnings(
        self, transaction_id: int, wallet_session: sa.orm.Session = None
    ) -> list[int]:
        should_manage = wallet_session is None
        if should_manage:
            wallet_session = sa.orm.Session(self._wallet_engine)

        # Query with selectinload
        transaction: Transaction = (
            wallet_session.query(Transaction)
            .options(sa.orm.selectinload(Transaction.entitled_to_earnings))
            .where(Transaction.id == transaction_id)
            .one_or_none()
        )

        if should_manage:
            wallet_session.close()

        return (
            list(set(e.id for e in transaction.entitled_to_earnings))
            if transaction
            else []
        )

    def _create_or_update_earning_yield(
        self,
        earning_id: int,
        wallet_session: sa.orm.Session = None,
        analytic_session: sa.orm.Session = None,
    ):
        assert (wallet_session is None) == (analytic_session is None)
        should_manage = wallet_session is None

        if should_manage:
            wallet_session = sa.orm.Session(self._wallet_engine, expire_on_commit=False)
            analytic_session = sa.orm.Session(self._analytic_engine)

        # Data about the earning is required for the yield
        earning: Earning = (
            wallet_session.query(Earning)
            .options(sa.orm.selectinload(Earning.asset))
            .where(Earning.id == earning_id)
            .one()
        )

        # Position is required for yield. There might be cases
        #   where the user doesn't hold any shares for the asset,
        #   in such cases a default position of 0 is returned.
        def _get_default() -> Position:
            logger.debug(
                "No shares found for asset %s on earning %d. "
                "Yield will contain zero data.",
                earning.asset_b3_code,
                earning.id,
            )
            return Position(b3_code=earning.asset_b3_code, shares=0, avg_price=0.0)

        position = next(
            (
                p
                for p in Position.get(
                    session=wallet_session, reference_date=earning.hold_date
                )
                if p.b3_code == earning.asset_b3_code
            ),
            _get_default(),
        )

        # Economic data is also needed
        economic = (
            wallet_session.query(EconomicData)
            .where(
                sa.extract("month", EconomicData.reference_date)
                == sa.extract("month", earning.hold_date)
            )
            .all()
        )

        # Maybe close session
        if should_manage:
            wallet_session.close()

        # Compute required fields for earning yield
        cdi_on_hold_month = 0.0
        ipca_on_hold_month = 0.0
        for e in economic:
            v = e.percentage_change
            match e.index:
                case EconomicIndex.cdi:
                    cdi_on_hold_month = v
                case EconomicIndex.ipca:
                    ipca_on_hold_month = v
                case _:
                    continue

        ir_adjusted_value_per_share = (
            1 - earning.ir_percentage
        ) * earning.value_per_share
        earning_yield = EarningYield(
            b3_code=earning.asset_b3_code,
            asset_kind=earning.asset.kind,
            earning_id=earning.id,
            earning_kind=earning.kind,
            hold_date=earning.hold_date,
            payment_date=earning.payment_date,
            ir=earning.ir_percentage,
            value_per_share=earning.value_per_share,
            ir_adjusted_value_per_share=ir_adjusted_value_per_share,
            shares=position.shares,
            avg_price=position.avg_price,
            yoc=(
                (100 * (ir_adjusted_value_per_share / position.shares))
                if position.shares > 0
                else 0.0
            ),
            cdi_on_hold_month=cdi_on_hold_month,
            ipca_on_hold_month=ipca_on_hold_month,
        )

        # Add to session
        analytic_session.add(earning_yield)

        # Save state (if it exists, will be updated)
        if should_manage:
            analytic_session.commit()
            analytic_session.close()
