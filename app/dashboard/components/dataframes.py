from typing import Callable

import pandas as pd
import streamlit as st
from pandera.typing import DataFrame

from app.analytics.entities import EarningYield
from app.config import DASHBOARD_CONFIG as config
from app.dashboard.state import Manager, ScopedState
from app.db.models import EconomicData

_PREFIX = "__dataframe_{}"


def asset_dataframe(
    assets: pd.DataFrame,
    selection_mode=None,
    selection_callable: Callable[[ScopedState], None] = None,
):
    prefix = _PREFIX.format("asset")

    if selection_callable is not None:

        def on_select():
            selection_callable(
                Manager.get_proxied_data_state("asset_dataframe", prefix)
            )

    else:
        on_select = "ignore"

    st.dataframe(
        assets,
        hide_index=True,
        column_config={
            "b3_code": st.column_config.TextColumn("Código do Ativo (B3)", pinned=True),
            "name": st.column_config.TextColumn("Nome"),
            "description": st.column_config.TextColumn("Descrição"),
            "kind": st.column_config.TextColumn("Tipo"),
            "added": st.column_config.DateColumn(
                "Adicionado", format=config.ST_DATE_FORMAT
            ),
        },
        key=f"{prefix}_event",
        selection_mode=selection_mode,
        on_select=on_select,
    )


def transaction_dataframe(
    transactions: pd.DataFrame,
    selection_mode=None,
    selection_callable: Callable[[ScopedState], None] = None,
):
    prefix = _PREFIX.format("transaction")

    if selection_callable is not None:

        def on_select():
            selection_callable(
                Manager.get_proxied_data_state("transaction_dataframe", prefix)
            )

    else:
        on_select = "ignore"

    st.dataframe(
        transactions.drop(columns="id"),
        hide_index=True,
        column_config={
            "asset_b3_code": st.column_config.TextColumn(
                "Código do Ativo (B3)", pinned=True
            ),
            "kind": st.column_config.TextColumn("Tipo"),
            "date": st.column_config.DateColumn("Data", format=config.ST_DATE_FORMAT),
            "value_per_share": st.column_config.NumberColumn(
                "Valor por unidade:", format="R$ %.2f"
            ),
            "shares": st.column_config.NumberColumn("Unidades", format="%d"),
        },
        key=f"{prefix}_event",
        selection_mode=selection_mode,
        on_select=on_select,
    )


def earning_dataframe(
    earnings: pd.DataFrame,
    selection_mode=None,
    selection_callable: Callable[[ScopedState], None] = None,
):
    prefix = _PREFIX.format("earning")

    if selection_callable is not None:

        def on_select():
            selection_callable(
                Manager.get_proxied_data_state("earning_dataframe", prefix)
            )

    else:
        on_select = "ignore"

    st.dataframe(
        earnings.drop(columns="id"),
        hide_index=True,
        column_config={
            "asset_b3_code": st.column_config.TextColumn(
                "Código do Ativo (B3)", pinned=True
            ),
            "kind": st.column_config.TextColumn("Tipo"),
            **{
                k: st.column_config.DateColumn(label, format=config.ST_DATE_FORMAT)
                for k, label in zip(
                    ["hold_date", "payment_date"],
                    ["Data de Custódia", "Data de Pagamento"],
                )
            },
            "value_per_share": st.column_config.NumberColumn(
                "Valor por unidade", format="R$ %.2f"
            ),
            "ir_percentage": st.column_config.NumberColumn(
                "Imposto de Renda (%)", format="%.2f%%"
            ),
        },
        key=f"{prefix}_event",
        selection_mode=selection_mode,
        on_select=on_select,
    )


def economic_data_dataframe(economic_data: list[EconomicData]):
    data = dict(index=[], reference_date=[], percentage_change=[], number_index=[])

    if economic_data:
        for ed in economic_data:
            for k in data.keys():
                # Obter valor do modelo
                v = getattr(ed, k)

                # Se for um índice, mapear
                #   pro nome
                if k == "index":
                    v = v.value

                # Adicionar dado do ativo
                data[k].append(v)

    st.dataframe(
        pd.DataFrame(data).sort_values(["index", "reference_date"]),
        hide_index=True,
        column_config={
            "index": st.column_config.TextColumn("Índice Econômico", pinned=True),
            "kind": st.column_config.TextColumn("Tipo"),
            "reference_date": st.column_config.DateColumn(
                "Mês de Referência", format="MM/YYYY"
            ),
            "percentage_change": st.column_config.NumberColumn(
                "Variação (%)", format="%.2f%%"
            ),
            "number_index": st.column_config.NumberColumn(
                "Número Índice", format="%.3f"
            ),
        },
    )


def earning_yield_dataframe(df: DataFrame[EarningYield]):
    # Colunas derivadas
    df = df.copy()
    df["cdb_yield"] = 0.85 * df.cdi_on_hold_month

    st.dataframe(
        df,
        hide_index=True,
        column_order=[
            "b3_code",
            "asset_kind",
            "kind",
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
            "kind": st.column_config.TextColumn("Tipo", help="Tipo de provento."),
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
