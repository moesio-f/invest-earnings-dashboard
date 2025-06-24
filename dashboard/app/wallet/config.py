"""Configuração da API da carteira."""

import re

from pydantic import HttpUrl, model_validator
from pydantic_settings import BaseSettings


class WalletConfig(BaseSettings):
    WALLET_API_URL: HttpUrl

    @model_validator(mode="after")
    def validate_wallet_api(self):
        base = str(self.WALLET_API_URL).rstrip("/").split("/")[-1]
        if re.match(r"v[0-9]+", base):
            raise ValueError("Wallet API URL shouldn't include version prefixes.")
        return self


WALLET_CONFIG = WalletConfig()
