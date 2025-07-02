"""Dataframes."""

import pandas as pd
import streamlit as st
from app.config import ST_CONFIG as config


def earning_yield_dataframe(df: pd.DataFrame):
    # Colunas derivadas
    df = df.copy()
    df["cdb_yield"] = 0.85 * df.cdi_on_hold_month
    df["total_earnings"] = df.shares * df.ir_adjusted_value_per_share

    st.dataframe(
        df.sort_values("payment_date", ascending=False),
        hide_index=True,
        column_order=[
            "b3_code",
            "asset_kind",
            "earning_kind",
            "hold_date",
            "payment_date",
            "shares",
            "avg_price",
            "value_per_share",
            "ir_adjusted_value_per_share",
            "total_earnings",
            "yoc",
            "cdb_yield",
            "cdi_on_hold_month",
            "ipca_on_hold_month",
        ],
        column_config={
            "b3_code": st.column_config.TextColumn("Código do Ativo (B3)", pinned=True),
            "asset_kind": st.column_config.TextColumn(
                "Classe do Ativo", help="Classe do ativo."
            ),
            "earning_kind": st.column_config.TextColumn(
                "Tipo", help="Tipo de provento."
            ),
            "shares": st.column_config.NumberColumn(
                "Unidades",
                help="Quantidade de unidades elegíveis para proventos.",
                format="%d",
            ),
            **{
                k: st.column_config.DateColumn(label, format=config.ST_DATE_FORMAT)
                for k, label in zip(
                    ["hold_date", "payment_date"],
                    ["Data de Custódia", "Data de Pagamento"],
                )
            },
            **{
                k: st.column_config.NumberColumn(label, help=help, format="R$ %.2f")
                for k, label, help in zip(
                    [
                        "value_per_share",
                        "ir_adjusted_value_per_share",
                        "avg_price",
                        "total_earnings",
                    ],
                    ["Valor Bruto", "Valor Líquido", "Preço Médio", "Total"],
                    [
                        "Proventos brutos por ação.",
                        "Proventos por ação após IR.",
                        "Preço médio até a data de custódia. Considera apenas transações de compra elegíveis.",
                        "Total de proventos com base na quantidade de unidades e valor líquido por unidade.",
                    ],
                )
            },
            **{
                k: st.column_config.NumberColumn(label, help=help, format="%.2f%%")
                for k, label, help in zip(
                    ["yoc", "cdb_yield", "cdi_on_hold_month", "ipca_on_hold_month"],
                    [
                        "Yield on Cost (YoC)",
                        "CDB",
                        "CDI",
                        "IPCA",
                    ],
                    [
                        "Porcentagem de retorno com relação ao preço medio.",
                        "Rendimento de um CDB 100% do CDI considerando a alíquota de 15%. Conhecido como 'CDI Líquido'.",
                        "CDI no mês de custódia (proxy com relação a data da compentência).",
                        "IPCA no mês de custódia (proxy com relação a data da competência).",
                    ],
                )
            },
        },
    )
