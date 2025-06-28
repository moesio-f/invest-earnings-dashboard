"""Métricas."""

import logging

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


def position_metrics(history: pd.DataFrame):
    # Find two most recent dates
    most_recent_dates = history.month.unique()
    most_recent_dates.sort()
    most_recent_dates = most_recent_dates[::-1][:2]

    # Find complete DataFrame
    df = (
        history[["month", "total_invested", "balance", "total_ir_adjusted_earnings"]][
            history.month.isin(most_recent_dates)
        ]
        .groupby("month")
        .sum()
        .reset_index()
    )
    df["variation"] = 100 * (df.balance - df.total_invested) / df.total_invested
    df["return"] = (
        100
        * (df.balance + df.total_ir_adjusted_earnings - df.total_invested)
        / df.total_invested
    )

    # Get current and previous
    current = df.iloc[0]
    old = df.iloc[1] if len(df) > 1 else current

    for container, label, value, delta, help in zip(
        [
            *st.columns(5),
        ],
        [
            "Total Investido (R$)",
            "Patrimônio (R$)",
            "Variação (%)",
            "Rentabilidade (%)",
            "Proventos Recebidos (R$)",
        ],
        [
            f"R$ {current.total_invested:,.2f}",
            f"R$ {current.balance:,.2f}",
            f"{current.variation:.2f}%",
            f"{current['return']:.2f}%",
            f"R$ {current.total_ir_adjusted_earnings:,.2f}",
        ],
        [
            f"{current.total_invested - old.total_invested:,.2f}",
            f"{current.balance - old.balance:,.2f}",
            f"{current.variation - old.variation:.2f}",
            f"{current['return'] - old['return']:,.2f}",
            f"{current.total_ir_adjusted_earnings - old.total_ir_adjusted_earnings:,.2f}",
        ],
        [
            "Total investido: `sum(PM * #Unidades)`.",
            "Patrimônio: `sum(Preço Atual * #Unidades)`.",
            "Variação do patrimônio com relação ao total investido.",
            "Variação do patrimônio + proventos com relação ao total investido.",
            "Total recebido em proventos.",
        ],
    ):
        container.metric(label, value, delta=delta, help=help)
