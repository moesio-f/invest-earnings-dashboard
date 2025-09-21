"""Exibição de DataFrames."""

from typing import Callable

import pandas as pd
import streamlit as st
from app.config import ST_CONFIG as config
from app.utils.state import Manager, ScopedState

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


def economic_data_dataframe(economic_data: pd.DataFrame):
    st.dataframe(
        economic_data,
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
        },
    )


def position_dataframe(position: pd.DataFrame):
    position = position[position.shares != 0].copy()
    position["price_variation"] = (
        100 * (position.current_price - position.avg_price) / position.avg_price
    )

    def format(styler):
        styler.text_gradient(
            cmap="RdYlGn",
            subset=["price_variation", "yield_on_cost", "rate_of_return"],
            vmin=-0.001,
            vmax=0.001,
        )
        return styler

    st.dataframe(
        position.style.pipe(format),
        column_order=[
            "b3_code",
            "asset_kind",
            "shares",
            "avg_price",
            "current_price",
            "price_variation",
            "yield_on_cost",
            "rate_of_return",
            "total_invested",
            "balance",
            "total_ir_adjusted_earnings",
        ],
        hide_index=True,
        column_config={
            "b3_code": st.column_config.TextColumn(
                "Ativo", pinned=True, width="medium"
            ),
            "asset_kind": st.column_config.TextColumn("Classe do Ativo"),
            "shares": st.column_config.NumberColumn("Quantidade", format="%d"),
            "avg_price": st.column_config.NumberColumn("Preço Médio", format="R$ %.2f"),
            "total_invested": st.column_config.NumberColumn(
                "Total Investido", format="R$ %.2f"
            ),
            "current_price": st.column_config.NumberColumn(
                "Preço Atual", format="R$ %.2f"
            ),
            "balance": st.column_config.NumberColumn("Saldo", format="R$ %.2f"),
            "price_variation": st.column_config.NumberColumn(
                "Variação", format="%.2f%%"
            ),
            "yield_on_cost": st.column_config.NumberColumn(
                "Yield on Cost", format="%.2f%%"
            ),
            "rate_of_return": st.column_config.NumberColumn(
                "Rentabilidade", format="%.2f%%"
            ),
            "total_ir_adjusted_earnings": st.column_config.NumberColumn(
                "Total de Proventos", format="R$ %.2f"
            ),
        },
    )


def document_dataframe(document: pd.DataFrame):
    st.dataframe(
        document,
        column_order=[
            "asset_b3_code",
            "title",
            "publish_date",
            "url",
        ],
        hide_index=True,
        column_config={
            "asset_b3_code": st.column_config.TextColumn(
                "Ativo", pinned=True, width="medium"
            ),
            "title": st.column_config.TextColumn("Título"),
            "publish_date": st.column_config.DateColumn(
                "Data de Publicação", format=config.ST_DATE_FORMAT
            ),
            "url": st.column_config.LinkColumn("URL"),
        },
    )
