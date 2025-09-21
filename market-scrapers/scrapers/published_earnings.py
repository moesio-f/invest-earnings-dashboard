"""Scraper de proventos."""

import base64
import json
import logging
import random
import time
from datetime import date, datetime

import click
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pydantic import BaseModel

from .config import CONFIG as config

logger = logging.getLogger(__name__)


class AssetConfig(BaseModel):
    code: str
    supported_urls: list[str]
    default_ir: float | None = None


def has_in_wallet(asset_code: str) -> bool:
    return requests.get(
        f"{config.wallet_api}/v1/asset/info/{asset_code}",
        timeout=config.timeout,
    ).ok


def available_earnings(asset_code: str) -> set[tuple[date, date, str]]:
    response = requests.get(
        f"{config.wallet_api}/v1/earnings/info/{asset_code}",
        timeout=config.timeout,
    )
    response.raise_for_status()
    return set((d["hold_date"], d["payment_date"], d["kind"]) for d in response.json())


def extract_strategy_1(b3_code: str, url: str, default_ir: float = None) -> list[dict]:
    def _map_kind(v: str) -> tuple[str, float]:
        v = v.lower()
        if "jscp" in v:
            return "Juros sobre Capital Próprio", 15.0

        if "rend" in v and "trib" in v:
            return "Rendimento Tributável", 22.5

        return "Dividendo", 0.0

    # Base get
    response = requests.get(
        url, headers={"User-Agent": UserAgent().random}, timeout=config.timeout
    )
    response.raise_for_status()

    # Parsing
    data = []
    html = BeautifulSoup(response.text, features="html.parser")
    table = html.find(id="table-dividends-history")
    tbody = table.find("tbody")
    for row in tbody.find_all("tr"):
        contents = row.find_all("td")
        if len(contents) != 4:
            continue

        # Extract data
        contents = [c.text.strip() for c in contents]
        kind, hold, payment, value = contents

        # Add to dictionary
        kind, ir = _map_kind(kind)
        if default_ir is not None:
            ir = default_ir
        data.append(
            {
                "asset_b3_code": b3_code,
                "kind": kind,
                "hold_date": datetime.strptime(hold, "%d/%m/%Y").date().isoformat(),
                "payment_date": datetime.strptime(payment, "%d/%m/%Y")
                .date()
                .isoformat(),
                "ir_percentage": ir,
                "value_per_share": float(
                    value.replace(".", " ").replace(",", ".").replace(" ", "")
                ),
            }
        )

    return data


def extract_data(b3_code: str, url: str, default_ir: float = None):
    # Select strategy from url
    if base64.b64decode(b"aW52ZXN0aWRvcjEw").decode() in url.lower():
        fn = extract_strategy_1
    else:
        logger.warning("Unknown strategy for URL '%s'.", url)
        return

    # Extract with strategy
    data = fn(b3_code, url, default_ir)

    # If data available, filter and persist
    available = available_earnings(b3_code)
    data = [
        d
        for d in data
        if (d["hold_date"], d["payment_date"], d["kind"]) not in available
    ]
    if len(data) > 0:
        for d in data:
            requests.post(
                f"{config.wallet_api}/v1/earnings/create",
                json=d,
                timeout=config.timeout,
            ).raise_for_status()
        logger.info("Created %d earnings for asset %s.", len(data), b3_code)
    else:
        logger.info("Didn't create new earnings for %s.", b3_code)


@click.command(name="published_earnings")
def main():
    # Obtain registered assets
    with config.market_price_config_path.open("r") as f:
        assets = json.load(f)
    assets = [AssetConfig.model_validate(d) for d in assets]
    random.shuffle(assets)

    start_time = time.perf_counter()
    for asset in assets:
        url = random.choice(asset.supported_urls)
        logger.info("Running extraction for asset %s with URL '%s'.", asset.code, url)
        try:
            # Run extraction
            extract_data(asset.code, url, asset.default_ir)
        except Exception as e:
            logger.exception(
                "Extraction failed for asset %s: %s",
                asset.code,
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
