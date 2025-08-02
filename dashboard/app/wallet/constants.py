"""Definições de constantes."""

EconomicIndices: list[str] = ["CDI", "IPCA"]
AssetKinds: list[str] = ["Ação", "BDR", "FII", "ETF"]
AssetKindMapper: dict[str, str] = {
    "Ação": "Ação",
    "BDR": "Brazilian Depositary Receipt (BDR)",
    "FII": "Fundo de Investimento Imobiliário (FII)",
    "ETF": "Exchange Traded Fund (ETF)",
}
TransactionKinds: list[str] = ["Compra", "Venda"]
EarningKinds: list[str] = [
    "Dividendo",
    "Juros sobre Capital Próprio",
    "Rendimento Tributável",
]
