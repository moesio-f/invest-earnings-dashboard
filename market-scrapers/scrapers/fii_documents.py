"""Scraper de relatórios gerenciais
de FIIs."""

import base64
import logging
import random
import re
import time
from datetime import date, datetime

import click
import requests
from fake_useragent import UserAgent
from unidecode import unidecode

from .config import CONFIG as config

logger = logging.getLogger(__name__)
CNPJ_REGEX = re.compile(r"[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/0001-[0-9]{2}")
URL = base64.b64decode(
    "aHR0cHM6Ly9mbmV0LmJtZmJvdmVzcGEuY29tLmJyL2ZuZXQvcHVibGljby"
    "9wZXNxdWlzYXJHZXJlbmNpYWRvckRvY3VtZW50b3NEYWRvcz9kPTAmcz0wJ"
    "mw9MjAmbyU1QjAlNUQlNUJkYXRhRW50cmVnYSU1RD1kZXNjJmNucGpGdW5kbz0="
).decode()
DOC_URL = base64.b64decode(
    "aHR0cHM6Ly9mbmV0LmJtZmJvdmVzcGEuY29tLmJyL2ZuZXQvcHVibGl"
    "jby9leGliaXJEb2N1bWVudG8/"
).decode()


def get_current_fiis() -> list[str]:
    positions = requests.get(
        f"{config.wallet_api}/v1/position/on/{date.today().isoformat()}"
    ).json()
    return [p["b3_code"] for p in positions if p["asset_kind"] == "FII"]


def get_fiis_cnpjs() -> list[tuple[str, str]]:
    cnpjs = []
    for asset in get_current_fiis():
        info = requests.get(f"{config.wallet_api}/v1/asset/info/{asset}").json()
        matches = CNPJ_REGEX.findall(info["description"])
        if matches:
            cnpjs.append((asset, matches[0]))
    return cnpjs


@click.command(name="fii_documents")
def main():
    documents = requests.get(f"{config.wallet_api}/v1/document/list").json()
    fiis = get_fiis_cnpjs()
    random.shuffle(fiis)

    for asset, cnpj in fiis:
        asset_docs = set(d["url"] for d in documents if d["asset_b3_code"] == asset)

        try:
            response = requests.get(
                f"{URL}{cnpj}",
                headers={"User-Agent": UserAgent().random},
                timeout=config.timeout,
            )
            response.raise_for_status()
        except Exception as e:
            logger.exception(e)
            continue

        available_docs = [
            (
                d["tipoDocumento"],
                datetime.strptime(d["dataEntrega"], "%d/%m/%Y %H:%M")
                .date()
                .isoformat(),
                f"{DOC_URL}id={d['id']}&cvm=true",
            )
            for d in response.json()["data"]
            if "relatorio" in unidecode(d["categoriaDocumento"]).lower()
        ]

        for title, publish_date, url in available_docs:
            if url in asset_docs:
                continue

            try:
                body = dict(
                    asset_b3_code=asset,
                    title=title,
                    publish_date=publish_date,
                    url=url,
                )
                requests.post(
                    f"{config.wallet_api}/v1/document/add",
                    json=body,
                ).raise_for_status()
                asset_docs.add(url)
            except Exception as e:
                logger.exception("Unable to add document: %s\n\nBody: %s", e, body)
                continue

        time.sleep(random.random() * 2)


if __name__ == "__main__":
    main()
