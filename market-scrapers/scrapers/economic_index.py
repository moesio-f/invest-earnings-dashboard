"""Scraper para dados econômicos."""

import base64
import logging

import click
import requests
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

URL_CDI = base64.b64decode(
    "aHR0cHM6Ly9hcGkuYmNiLmdvdi5ici9kYWRvcy9zZXJpZS9iY2RhdGEuc2dzLjQzOTEvZGFkb3M/Zm9ybWF0bz1qc29u"
).decode()
URL_IPCA = base64.b64decode(
    "aHR0cHM6Ly9hcGkuYmNiLmdvdi5ici9kYWRvcy9zZXJpZS9iY2RhdGEuc2dzLjQzMy9kYWRvcz9mb3JtYXRvPWpzb24="
).decode()


class EconomicIndexConfig(BaseSettings):
    wallet_api: str


@click.command(name="economic_index")
def main():
    wallet_api = EconomicIndexConfig().wallet_api

    for index, url in zip(["CDI", "IPCA"], [URL_CDI, URL_IPCA]):
        for last in requests.get(url).json()[-4:]:
            try:
                date = last["data"].split("/")
                requests.post(
                    f"{wallet_api}/v1/economic/add",
                    json=dict(
                        data=[
                            dict(
                                index=index,
                                reference_date=f"{date[2]}-{date[1]}-01",
                                percentage_change=last["valor"],
                            )
                        ]
                    ),
                )
            except Exception as e:
                logger.info("Couldn't update %s on date %s: %s", index, last["data"], e)
                pass


if __name__ == "__main__":
    main()
