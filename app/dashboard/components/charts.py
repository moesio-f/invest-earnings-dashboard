import pandas as pd
import plotly.express as px
import streamlit as st
from pandera.typing import DataFrame

from app.analytics.entities import EarningYield


def monthly_earnings(df: DataFrame[EarningYield], show_table: bool = False):
    df = df[["asset_kind", "payment_date", "total_earnings"]].copy()
    df["payment_date"] = pd.to_datetime(df.payment_date) + pd.offsets.MonthEnd()

    agg = df.groupby(["payment_date", "asset_kind"]).sum().reset_index()
    agg = agg.rename(
        columns=dict(
            payment_date="Mês",
            total_earnings="Proventos Recebidos (R$)",
            asset_kind="Classe de Ativo",
        )
    )

    fig = px.bar(
        agg,
        x="Mês",
        y="Proventos Recebidos (R$)",
        color="Classe de Ativo",
    )
    fig.update_xaxes(tickformat="%b/%Y", dtick="M1")
    st.plotly_chart(fig)

    if show_table:
        agg = (
            agg.rename(columns={"Proventos Recebidos (R$)": "Proventos (R$)"})
            .drop(columns=["Classe de Ativo"])
            .groupby("Mês")
            .sum()
            .reset_index()
        )
        agg["date"] = agg["Mês"]
        agg["Ano"] = agg["Mês"].dt.year
        agg["Mês"] = agg["Mês"].dt.month.map(
            {
                1: "Janeiro",
                2: "Fevereiro",
                3: "Março",
                4: "Abril",
                5: "Maio",
                6: "Junho",
                7: "Julho",
                8: "Agosto",
                9: "Setembro",
                10: "Outubro",
                11: "Novembro",
                12: "Dezembro",
            }
        )

        st.dataframe(
            agg.pivot_table(index=["Ano", "Mês"], values=["date", "Proventos (R$)"])
            .sort_values("date")
            .drop(columns=["date"]),
            column_config={
                "Proventos (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
            },
        )


def monthly_yoc(df: DataFrame[EarningYield], target_asset: str):
    # Prepare dataframe
    df = df[["b3_code", "payment_date", "asset_kind", "yoc"]].copy()
    df["payment_date"] = pd.to_datetime(df.payment_date) + pd.offsets.MonthEnd()

    # Find target asset rows
    is_global = target_asset == "Todos"
    df_asset = (df if is_global else df[df.b3_code == target_asset]).drop(
        columns=["asset_kind", "b3_code"]
    )
    df = df.drop(columns="b3_code")

    # Find target YoC
    df_asset = (
        df_asset.groupby("payment_date")
        .mean()
        .reset_index()
        .assign(asset_kind=target_asset)
    )

    # Find YoC by asset class
    df_kind = df.groupby(["payment_date", "asset_kind"]).mean().reset_index()

    # Maybe target is not global?
    if not is_global:
        df_kind = pd.concat(
            [
                df_kind,
                df.drop(columns="asset_kind")
                .groupby("payment_date")
                .mean()
                .reset_index()
                .assign(asset_kind="Todos"),
            ]
        )

    # Unify DataFrame
    df = pd.concat([df_kind, df_asset])

    # Show DataFrame with are chart
    fig = px.bar(
        df,
        x="payment_date",
        y="yoc",
        color="asset_kind",
        labels=dict(payment_date="Mês", yoc="YoC Médio (%)", asset_kind="Grupo"),
        barmode="group",
    )
    fig.update_xaxes(tickformat="%b/%Y", dtick="M1")
    st.plotly_chart(fig)


def earnings_by(df: DataFrame[EarningYield], by: str):
    fig = px.pie(df, names=by, values="total_earnings")
    fig.update_traces(textposition="inside", textinfo="label+percent+value")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)
