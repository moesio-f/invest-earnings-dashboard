"""Processador de Yield On Cost (YoC)."""

import json
import logging
import random
from datetime import date, datetime

import pika
import sqlalchemy as sa
from engine.utils.messages import (
    AnalyticEvent,
    AnalyticTrigger,
    DatabaseOperation,
    QueryInformation,
    WalletEntity,
    WalletUpdateInformation,
)
from invest_earning.database.analytic import EarningYield
from invest_earning.database.wallet import (
    Earning,
    EconomicData,
    EconomicIndex,
    Position,
    Transaction,
)

logger = logging.getLogger(__name__)


class YoCProcessor:
    def __init__(
        self,
        queue: str,
        broker_url: str,
        wallet_db_url: str,
        analytic_db_url: str,
        temperature: float,
    ):
        self._conn, self._ch = None, None
        self._wallet_engine = None
        self._analytic_engine = None
        self._broker_url = broker_url
        self._queue = queue
        self._wallet_url = wallet_db_url
        self._analytic_url = analytic_db_url
        self._t = temperature

        if self._t > 0:
            logger.info(
                "Processor has positive temperature "
                "(%.2f), updates might occur spontaneously.",
                self._t,
            )

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
        # Preprocessing of known instances of id formats
        try:
            int_event_id = int(event.entity_id)
        except Exception:
            int_event_id = None

        # Pattern matching
        match (event.operation, event.entity):
            # Earning
            case (
                DatabaseOperation.CREATED | DatabaseOperation.UPDATED,
                WalletEntity.earning,
            ):
                logger.debug(
                    "Updating yield entry for earning with id %d.", int_event_id
                )
                self._create_or_update_earning_yield(int_event_id)
            case (DatabaseOperation.DELETED, WalletEntity.earning):
                logger.debug(
                    "Dropping all earning yields entries where earning_id == %d.",
                )
                self._drop_earning_yield_where(EarningYield.earning_id == int_event_id)

            # Transaction
            case (
                DatabaseOperation.CREATED | DatabaseOperation.UPDATED,
                WalletEntity.transaction,
            ):
                logger.debug(
                    "Bulk updating yield affected by transaction with id %d.",
                    int_event_id,
                )
                self._create_or_update_multiple(
                    self._get_earnings_affected_by_transaction(int_event_id)
                )
            case (DatabaseOperation.DELETED, WalletEntity.transaction):
                if event.reference == WalletEntity.earning:
                    logger.debug(
                        "Bulk updating yield affected by deletion of "
                        "transaction for asset %s.",
                        event.reference_id,
                    )
                    self._create_or_update_multiple(
                        self._get_earnings_affected_by_asset(event.reference_id)
                    )
                else:
                    logger.warning(
                        "Unhandled reference for Transaction "
                        "deletion: reference=%s, id=%s. Ignored event.",
                        event.reference,
                        event.reference_id,
                    )

            # Economic data
            case (_, WalletEntity.economic_data):
                # EconomicData has composite key of form `index`_`date`
                splits = event.entity_id.split("_", maxsplit=1)
                if len(splits) == 2:
                    e_index = EconomicIndex.from_value(splits[0])
                    ref_date = datetime.strptime(splits[1], "%Y_%m_%d").date()
                    self._create_or_update_multiple(
                        self._get_earnings_affected_by_economic(e_index, ref_date)
                    )
                else:
                    logger.warning(
                        "Unknown format for EconomicData " "ID: '%s'. Ignored event.",
                        event.entity_id,
                    )

            # Asset
            case (DatabaseOperation.DELETED, WalletEntity.asset):
                self._drop_earning_yield_where(EarningYield.b3_code == event.entity_id)

    def _process_dashboard_query(self, event: QueryInformation):
        # TODO: improve checking and message processing
        n_earnings = self._earnings_count()
        n_yield = self._earning_yield_count()
        has_missing_yield = n_yield < n_earnings
        should_random_update = random.random() > (1 - self._t)

        if has_missing_yield or should_random_update:
            earnings_ids = self._all_earnings_ids()
            if has_missing_yield:
                logger.debug(
                    "n_yield (%d) < n_earnings (%d), running analysis "
                    "for all earnings (%d).",
                    n_yield,
                    n_earnings,
                    len(earnings_ids),
                )
            else:
                logger.debug(
                    "Random update triggered by RNG. "
                    "Running analyis for %d earnings.",
                    len(earnings_ids),
                )
            # First drop possibly missing ids (prune)
            self._drop_earning_yield_where(EarningYield.earning_id.not_in(earnings_ids))

            # Then, create or update existing ones
            self._create_or_update_multiple(earnings_ids)
        else:
            logger.debug(
                "Database has yield for all earnings and "
                "no random update triggered. Skipping."
            )

    def _all_earnings_ids(self) -> list[int]:
        with sa.orm.Session(self._wallet_engine) as session:
            return [e.id for e in session.query(Earning).all()]

    def _earnings_count(self) -> int:
        with sa.orm.Session(self._wallet_engine) as session:
            return session.query(Earning).count()

    def _earning_yield_count(self) -> int:
        with sa.orm.Session(self._analytic_engine) as session:
            return session.query(EarningYield).count()

    def _get_earnings_affected_by_asset(self, b3_code: str):
        with sa.orm.Session(self._analytic_engine) as analytic_session:
            return [
                ey.earning_id
                for ey in analytic_session.query(EarningYield)
                .where(EarningYield.b3_code == b3_code)
                .all()
            ]

    def _get_earnings_affected_by_economic(
        self, index: EconomicIndex, reference_date: date
    ) -> list[int]:
        # EarningYield only uses those indices
        if index not in {EconomicIndex.cdi, EconomicIndex.ipca}:
            return []

        # We must find which EarningYield rows are affected
        with sa.orm.Session(self._analytic_engine) as analytic_session:
            return [
                ey.earning_id
                for ey in analytic_session.query(EarningYield)
                .where(
                    sa.extract("year", EarningYield.hold_date) == reference_date.year
                )
                .where(
                    sa.extract("month", EarningYield.hold_date) == reference_date.month
                )
                .all()
            ]

    def _get_earnings_affected_by_transaction(
        self,
        transaction_id: int,
    ) -> list[int]:
        with sa.orm.Session(self._wallet_engine) as wallet_session:
            transaction: Transaction = (
                wallet_session.query(Transaction)
                .options(sa.orm.selectinload(Transaction.entitled_to_earnings))
                .where(Transaction.id == transaction_id)
                .one_or_none()
            )

            return (
                list(set(e.id for e in transaction.entitled_to_earnings))
                if transaction
                else []
            )

    def _create_or_update_multiple(self, earnings_ids: list[int]):
        # Create sessions to group all changes into single transaction
        wsession = sa.orm.Session(self._wallet_engine, expire_on_commit=False)
        asession = sa.orm.Session(self._analytic_engine)

        # For each affected earning, update
        logger.debug(
            "Processing %d affected earnings by creating or "
            "updating earning yield entry for each one.",
            len(earnings_ids),
        )
        for earning_id in earnings_ids:
            self._create_or_update_earning_yield(
                earning_id,
                wallet_session=wsession,
                analytic_session=asession,
            )

        # Commit changes and close sessions
        logger.debug("Commiting changes of affected earnings to database.")
        wsession.close()
        asession.commit()
        asession.close()

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

        try:
            position = next(
                p
                for p in Position.get(
                    session=wallet_session, reference_date=earning.hold_date
                )
                if p.b3_code == earning.asset_b3_code
            )
        except StopIteration:
            position = _get_default()

        # Economic data is also needed
        economic = (
            wallet_session.query(EconomicData)
            .where(
                sa.extract("year", EconomicData.reference_date)
                == sa.extract("year", earning.hold_date)
            )
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
            1 - (earning.ir_percentage / 100)
        ) * earning.value_per_share
        data = dict(
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
            total_earnings=position.shares * ir_adjusted_value_per_share,
            yoc=(
                (100 * (ir_adjusted_value_per_share / position.avg_price))
                if position.shares > 0
                else 0.0
            ),
            cdi_on_hold_month=cdi_on_hold_month,
            ipca_on_hold_month=ipca_on_hold_month,
        )

        # Check if object already exists
        earning_yield = analytic_session.get(EarningYield, earning_id)

        # If it exists, simply update
        if earning_yield is not None:
            for k, v in data.items():
                setattr(earning_yield, k, v)
        else:
            # Otherwise, create new one
            analytic_session.add(EarningYield(**data))

        # Save state (if it exists, will be updated)
        if should_manage:
            analytic_session.commit()
            analytic_session.close()

    def _drop_earning_yield_where(
        self,
        clause,
        analytic_session: sa.orm.Session = None,
    ):
        should_manage = analytic_session is None
        if should_manage:
            analytic_session = sa.orm.Session(self._analytic_engine)

        objects = analytic_session.query(EarningYield).where(clause).all()
        for obj in objects:
            analytic_session.delete(obj)

        logger.debug("Marked %d rows of EarningYield to deletion.", len(objects))
        if should_manage:
            analytic_session.commit()
            analytic_session.close()
