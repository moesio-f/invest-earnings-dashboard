"""Scrapper de preços de mercado."""

import logging
import random
import re
import time
from datetime import date, datetime, timedelta

import click
import requests
import sqlalchemy as sa
from fake_useragent import UserAgent
from invest_earning.database.wallet import Asset, AssetKind, MarketPrice
from pydantic_settings import BaseSettings

from . import db
from .dispatcher import Dispatcher

logger = logging.getLogger(__name__)


class MarketPriceConfig(BaseSettings):
    previous_days: int = 30


def asset_codes() -> list[tuple[str, AssetKind]]:
    with db.get_db_session() as session:
        return session.query(Asset.b3_code, Asset.kind).all()


def min_max_dates_for(asset_code: str) -> tuple[date, date]:
    with db.get_db_session() as session:
        min_date, max_date = (
            session.query(
                sa.sql.func.min(MarketPrice.reference_date),
                sa.sql.func.max(MarketPrice.reference_date),
            )
            .where(MarketPrice.asset_b3_code == asset_code)
            .all()[0]
        )

    if min_date is None:
        min_date = date.max
        max_date = date.min

    return min_date, max_date


def extract_strategy_1(
    b3_code: str, kind: AssetKind, start_date: date, end_date: date
) -> list[dict]:
    def map_kind(k: AssetKind):
        match k:
            case AssetKind.stock:
                return "acao"
            case _:
                return k.name

    # Query prices
    url = f"https://statusinvest.com.br/{map_kind(kind)}/tickerprice?ticker={b3_code}&type=4&currences[]=1"
    response = requests.get(url, headers={"User-Agent": UserAgent().random})
    response.raise_for_status()

    # Get and parse data
    data = response.json()[0]["prices"]
    for d in data:
        d["date"] = datetime.strptime(d["date"], "%d/%m/%y %H:%M").date()

    # Filter to required period
    return list(filter(lambda d: d["date"] > start_date and d["date"] < end_date, data))


def extract_strategy_2(
    b3_code: str, kind: AssetKind, start_date: date, end_date: date
) -> list[dict]:
    def map_kind(k: AssetKind):
        match k:
            case AssetKind.stock:
                return "acoes"
            case _:
                return f"{k.name}s"

    # Base get
    url = f"https://investidor10.com.br/{map_kind(kind)}/{b3_code}/"
    response = requests.get(url, headers={"User-Agent": UserAgent().random})
    response.raise_for_status()

    # Find target url in page
    m = re.search(r"quotations: '(?P<data_url>.+)',", response.text)
    if m is not None:
        response = requests.get(
            m.group("data_url"), headers={"User-Agent": UserAgent().random}
        )
        response.raise_for_status()
        data = response.json()
        for d in data:
            d["date"] = datetime.strptime(d["created_at"], "%d/%m/%Y").date()
            del d["created_at"]
        return data

    return []


def extract_data(
    b3_code: str,
    kind: AssetKind,
    start_date: date,
    end_date: date,
    initial_strategy: int = 1,
):
    # Select initial strategy
    fst, snd = extract_strategy_1, extract_strategy_2
    if initial_strategy == 2:
        fst, snd = extract_strategy_2, extract_strategy_1

    # Try with strategies
    data = fst(b3_code, kind, start_date, end_date)
    if len(data) <= 0:
        logger.debug("Strategy one failed, trying with strategy 2.")
        data = snd(b3_code, kind, start_date, end_date)

    # If data available, persist
    if len(data) > 0:
        with db.get_db_session() as session:
            for d in data:
                session.merge(
                    MarketPrice(
                        reference_date=d["date"],
                        asset_b3_code=b3_code,
                        closing_price=d["price"],
                    )
                )
            session.commit()
        logger.info("Inserted %d rows to asset %s.", len(data), b3_code)
    else:
        logger.warning("No strategy could extract data for asset %s.", b3_code)


@click.command(name="market_price")
def main():
    # Get today
    today = date.today()

    # Get data for previous days required by the user
    start_date = today - timedelta(days=MarketPriceConfig().previous_days)

    # Scrape up to yesterday (i.e., no closing price for today yet)
    end_date = today - timedelta(days=1)

    # Obtain list of assets in random order
    codes = asset_codes()
    random.shuffle(codes)
    start_time = time.perf_counter()
    for b3_code, kind in codes:
        logger.info("Checking if asset %s requires extraction...", b3_code)

        # Find current available dates
        min_date, max_date = min_max_dates_for(b3_code)

        # Is extraction required?
        if min_date > start_date or max_date < end_date:
            logger.info("Extraction required.")

            # Update lower and upper limits for extraction
            min_date = min(min_date, start_date)
            max_date = max(max_date, end_date)

            try:
                # Run extraction
                extract_data(
                    b3_code,
                    kind,
                    min_date,
                    max_date,
                    initial_strategy=random.randint(1, 2),
                )

                # Notify successful extraction
                Dispatcher.notify_extraction(b3_code, min_date, max_date)
            except Exception as e:
                logger.exception(
                    "Extraction failed for asset %s (%s-%s): %s",
                    b3_code,
                    min_date.isoformat(),
                    max_date.isoformat(),
                    e,
                )
            finally:
                # Sleep random time before next extraction
                sleep = random.randint(1, 5)
                logger.info("Processing finished. Sleeping for %d seconds.", sleep)
                time.sleep(sleep)

    logger.info(
        "Extraction completed in %.4f seconds.", time.perf_counter() - start_time
    )


if __name__ == "__main__":
    main()
