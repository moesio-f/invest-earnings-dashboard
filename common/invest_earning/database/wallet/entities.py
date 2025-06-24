"""Enumerações."""

from invest_earning.database.utils import StrEnum


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
