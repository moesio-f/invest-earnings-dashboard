"""Classe cliente para a API
de gerenciamento da carteira.
"""

import json
import logging
from datetime import date

import pandas as pd
import requests

from .config import WALLET_CONFIG as config

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = str(config.WALLET_API_URL)

        self._url = self._join(base_url, "v1")
        self._asset_url = self._join(self._url, "asset")
        self._earning_url = self._join(self._url, "earnings")
        self._transaction_url = self._join(self._url, "transactions")
        self._economic_url = self._join(self._url, "economic")
        self._position_url = self._join(self._url, "position")

    def list_assets(self) -> pd.DataFrame:
        response = requests.get(self._join(self._asset_url, "list"))
        response.raise_for_status()
        df = pd.DataFrame(
            response.json(), columns=["b3_code", "kind", "name", "description", "added"]
        )
        return df.assign(added=df.added.map(date.fromisoformat))

    def create_asset(
        self,
        b3_code: str,
        name: str,
        kind: str,
        description: str = "",
        added: date | None = None,
    ):
        data = dict(
            b3_code=b3_code,
            name=name,
            kind=kind,
            description=description,
            added=self._maybe_date_to_isoformat(added),
        )
        try:
            requests.post(
                self._join(self._asset_url, "create"),
                json=data,
            ).raise_for_status()
        except Exception as e:
            logger.critical(
                "%s:\n%s", e, json.dumps(data, indent=2, ensure_ascii=False)
            )
            raise

    def update_asset(
        self,
        b3_code: str,
        name: str = None,
        kind: str = None,
        description: str = None,
        added: date | None = None,
        delete: bool = False,
    ):
        if delete:
            requests.delete(
                self._join(self._asset_url, "delete", b3_code)
            ).raise_for_status()
            return

        requests.patch(
            self._join(self._asset_url, "update", b3_code),
            json=dict(
                name=name,
                kind=kind,
                added=self._maybe_date_to_isoformat(added),
            ),
        ).raise_for_status()

    def list_earnings(self) -> pd.DataFrame:
        response = requests.get(self._join(self._earning_url, "list"))
        response.raise_for_status()
        df = pd.DataFrame(
            response.json(),
            columns=[
                "id",
                "asset_b3_code",
                "hold_date",
                "payment_date",
                "value_per_share",
                "ir_percentage",
                "kind",
            ],
        )
        return df.assign(
            **{k: df[k].map(date.fromisoformat) for k in ["hold_date", "payment_date"]}
        )

    def create_earning(
        self,
        asset_b3_code: str,
        hold_date: date,
        payment_date: date,
        value_per_share: float,
        ir_percentage: float,
        kind: str,
    ) -> int:
        data = dict(
            asset_b3_code=asset_b3_code,
            hold_date=self._maybe_date_to_isoformat(hold_date),
            payment_date=self._maybe_date_to_isoformat(payment_date),
            value_per_share=value_per_share,
            ir_percentage=ir_percentage,
            kind=kind,
        )
        response = requests.post(
            self._join(self._earning_url, "create"),
            json=data,
        )
        try:
            response.raise_for_status()
        except Exception as e:
            logger.critical(
                "%s:\n%s", e, json.dumps(data, indent=2, ensure_ascii=False)
            )
            raise
        return response.json()["id"]

    def update_earning(
        self,
        earning_id: int,
        asset_b3_code: str = None,
        hold_date: date = None,
        payment_date: date = None,
        value_per_share: float = None,
        ir_percentage: float = None,
        kind: str = None,
        delete: bool = False,
    ):
        if delete:
            requests.delete(
                self._join(self._earning_url, "delete", earning_id)
            ).raise_for_status()
            return

        data = dict(
            asset_b3_code=asset_b3_code,
            hold_date=self._maybe_date_to_isoformat(hold_date),
            payment_date=self._maybe_date_to_isoformat(payment_date),
            value_per_share=value_per_share,
            ir_percentage=ir_percentage,
            kind=kind,
        )

        try:
            requests.patch(
                self._join(self._earning_url, "update", earning_id),
                json=data,
            ).raise_for_status()
        except Exception as e:
            logger.critical(
                "%s:\n%s", e, json.dumps(data, indent=2, ensure_ascii=False)
            )
            raise

    def delete_earning(self, earning_id: int):
        requests.delete(
            self._join(
                self._earning_url,
                "delete",
                earning_id,
            )
        ).raise_for_status()

    def list_transactions(self) -> pd.DataFrame:
        response = requests.get(self._join(self._transaction_url, "list"))
        response.raise_for_status()
        df = pd.DataFrame(
            response.json(),
            columns=[
                "id",
                "asset_b3_code",
                "date",
                "kind",
                "value_per_share",
                "shares",
            ],
        )
        return df.assign(date=df["date"].map(date.fromisoformat))

    def create_transaction(
        self,
        asset_b3_code: str,
        date: date,
        kind: str,
        value_per_share: float,
        shares: int,
    ) -> int:
        data = dict(
            asset_b3_code=asset_b3_code,
            date=self._maybe_date_to_isoformat(date),
            kind=kind,
            value_per_share=value_per_share,
            shares=shares,
        )
        response = requests.post(self._join(self._transaction_url, "create"), json=data)
        try:
            response.raise_for_status()
        except Exception as e:
            logger.critical(
                "%s:\n%s", e, json.dumps(data, indent=2, ensure_ascii=False)
            )
            raise
        return response.json()["id"]

    def update_transaction(
        self,
        transaction_id: int,
        asset_b3_code: str = None,
        date: date = None,
        kind: str = None,
        value_per_share: float = None,
        delete: bool = False,
    ):
        if delete:
            requests.delete(
                self._join(self._transaction_url, "delete", transaction_id)
            ).raise_for_status()
            return

        requests.patch(
            self._join(self._transaction_url, "update", transaction_id),
            json=dict(
                asset_b3_code=asset_b3_code,
                date=self._maybe_date_to_isoformat(date),
                kind=kind,
                value_per_share=value_per_share,
            ),
        ).raise_for_status()

    def list_economic(self) -> pd.DataFrame:
        response = requests.get(self._join(self._economic_url, "list"))
        response.raise_for_status()
        df = pd.DataFrame(
            response.json(), columns=["index", "reference_date", "percentage_change"]
        )
        return df.assign(reference_date=df["reference_date"].map(date.fromisoformat))

    def economic_add(self, data: list[dict] | pd.DataFrame):
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")

        for d in data:
            k = "reference_date"
            d[k] = self._maybe_date_to_isoformat(d[k])

        try:
            requests.post(
                self._join(self._economic_url, "add"), json=dict(data=data)
            ).raise_for_status()
        except Exception as e:
            logger.critical(
                "%s:\n%s", e, json.dumps(data, indent=2, ensure_ascii=False)
            )

    def delete_economic(self, index: str, reference_date: date):
        requests.delete(
            self._join(
                self._economic_url,
                "delete",
                index,
                reference_date.isoformat(),
            )
        ).raise_for_status()

    def get_position(self, reference_date: date = None):
        if reference_date is None:
            reference_date = date.today()

        response = requests.get(
            self._join(self._position_url, "on", reference_date.isoformat())
        )
        response.raise_for_status()
        return pd.DataFrame(
            response.json(),
            columns=[
                "b3_code",
                "shares",
                "avg_price",
                "total_invested",
                "asset_kind",
                "current_price",
                "balance",
                "total_earnings",
                "total_ir_adjusted_earnings",
                "yield_on_cost",
                "rate_of_return",
            ],
        )

    @staticmethod
    def _maybe_date_to_isoformat(v: date | None) -> str | None:
        if isinstance(v, date):
            return v.isoformat()
        return v

    @staticmethod
    def _join(*v: str) -> str:
        return "/".join(str(v_).rstrip("/") for v_ in v)


# Default client
WalletApi = Client()
