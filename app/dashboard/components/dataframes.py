import pandas as pd
import streamlit as st
from pandera.typing import DataFrame

from app.analytics.entities import EarningYield
from app.config import DASHBOARD_CONFIG as config
from app.db.models import Asset, Earning, Transaction, EconomicData


def asset_dataframe(assets: list[Asset]):
    data = dict(
        b3_code=[],
        name=[],
        description=[],
        kind=[],
        added=[],
    )

    if assets:
        for a in assets:
            for k in data.keys():
                # Obter valor do modelo
                v = getattr(a, k)

                # Se for tipo do ativo,
                #   mapear para representação
                #   textual
                if k == "kind":
                    v = v.value

                # Adicionar dado do ativo
                data[k].append(v)

    st.dataframe(
        pd.DataFrame(data).sort_values(["kind", "b3_code"]),
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
    )


def transaction_dataframe(transactions: list[Transaction]):
    data = dict(
        asset_b3_code=[],
        kind=[],
        date=[],
        value_per_share=[],
        shares=[],
    )

    if transactions:
        for t in transactions:
            for k in data.keys():
                # Obter valor do modelo
                v = getattr(t, k)

                # Se for tipo do ativo,
                #   mapear para representação
                #   textual
                if k == "kind":
                    v = v.value

                # Adicionar dado do ativo
                data[k].append(v)

    st.dataframe(
        pd.DataFrame(data).sort_values("date"),
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
    )


def earning_dataframe(earnings: list[Earning]):
    data = dict(
        asset_b3_code=[],
        kind=[],
        hold_date=[],
        payment_date=[],
        value_per_share=[],
        ir_percentage=[],
    )

    if earnings:
        for e in earnings:
            for k in data.keys():
                # Obter valor do modelo
                v = getattr(e, k)

                # Se for tipo do ativo,
                #   mapear para representação
                #   textual
                if k == "kind":
                    v = v.value

                # Adicionar dado do ativo
                data[k].append(v)

    st.dataframe(
        pd.DataFrame(data).sort_values("payment_date"),
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
    st.dataframe(
        df,
        hide_index=True,
        column_order=[
            "b3_code",
            "asset_kind",
            "kind",
            "ir",
            "hold_date",
            "payment_date",
            "shares",
            "avg_price",
            "value_per_share",
            "ir_adjusted_value_per_share",
            "total_earnings",
            "yoc",
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
                    ["ir", "yoc"],
                    ["Imposto de Renda Retido na Fonte (IRRF)", "Yield on Cost (YoC)"],
                    [
                        "Porcentagem de IR sobre o provento.",
                        "Porcentagem de retorno com relação ao preço medio.",
                    ],
                )
            },
        },
    )
