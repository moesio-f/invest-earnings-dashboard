"""Gráficos para visualização
de entidades.
"""

import pandas as pd
import plotly.express as px
import streamlit as st


def wealth_history(df: pd.DataFrame):
    df = df.groupby("month").sum().reset_index(drop=False)[["month", "total_invested"]]
    df = df.rename(columns=dict(month="Mês", total_invested="Patrimônio (R$)"))
    fig = px.bar(
        df,
        x="Mês",
        y="Patrimônio (R$)",
    )
    fig.update_xaxes(tickmode="array", tickvals=df["Mês"], tickformat="%b/%Y")
    st.plotly_chart(fig)


def position_disitribution(df: pd.DataFrame):
    df = (
        df[["asset_kind", "total_invested"]].groupby(["asset_kind"]).sum().reset_index()
    )
    df = df.rename(
        columns=dict(asset_kind="Tipo", total_invested="Total Investido (R$)")
    )
    fig = px.pie(df, values="Total Investido (R$)", names="Tipo")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig)
