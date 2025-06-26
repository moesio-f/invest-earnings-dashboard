"""Gráficos para visualização
de entidades.
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from app.wallet import colors


def wealth_history(df: pd.DataFrame):
    df = (
        df.groupby("month")
        .sum()
        .reset_index(drop=False)[["month", "total_invested", "balance"]]
    )
    df = df.rename(
        columns=dict(
            month="Mês", total_invested="Total Investido (R$)", balance="Saldo (R$)"
        )
    )
    fig = px.bar(
        df,
        x="Mês",
        y=["Total Investido (R$)", "Saldo (R$)"],
        barmode="group",
    )
    fig.update_yaxes(title="Patrimônio (R$)")
    fig.update_xaxes(tickmode="array", tickvals=df["Mês"], tickformat="%b/%Y")
    st.plotly_chart(fig)


def position_disitribution(df: pd.DataFrame):
    df = df[["asset_kind", "balance"]].groupby(["asset_kind"]).sum().reset_index()
    df = df.rename(columns=dict(asset_kind="Tipo", balance="Saldo (R$)"))
    fig = px.pie(
        df,
        values="Saldo (R$)",
        names="Tipo",
        color="Tipo",
        color_discrete_map=colors.AssetKindColors,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig)
