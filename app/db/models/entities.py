"""Classe que representa um ativo
que faz distribuição de proventos.
"""

from enum import Enum
from typing import Self


class StrEnum(Enum):
    @classmethod
    def from_value(cls, value: str) -> Self:
        try:
            return cls[value]
        except:
            return next(k for k in cls if k.value == value)


class AssetKind(StrEnum):
    stock = "Ação"
    bdr = "BDR"
    fii = "FII"
    etf = "ETF"


class TransactionKind(StrEnum):
    buy = "Compra"
    sell = "Venda"


class EarningKind(StrEnum):
    dividend = "Dividendo"
    jscp = "Juros sobre Capital Próprio"
    taxable = "Rendimento Tributável"


class EconomicIndex(StrEnum):
    cdi = "CDI"
    ipca = "IPCA"
    ima_b = "IMA-B"
    ima_b_5plus = "IMA-B 5+"
