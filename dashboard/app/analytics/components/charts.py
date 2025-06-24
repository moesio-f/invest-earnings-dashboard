"""Gráficos para visualização
de entidades.
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from app.analytics import colors


def monthly_earnings(df: pd.DataFrame, show_table: bool = False):
    # Maybe move calculation elsewhere?
    df = df[["asset_kind", "payment_date", "total_earnings"]].copy()
    df["payment_date"] = (
        pd.to_datetime(df["payment_date"])
        + pd.offsets.MonthEnd(0)
        - pd.offsets.MonthBegin(1)
    )
    df = df.groupby(["asset_kind", "payment_date"]).sum().reset_index()

    # Format DataFrame
    df = df.rename(
        columns=dict(
            payment_date="Mês",
            total_earnings="Proventos (R$)",
            asset_kind="Grupo",
        )
    )
    fig = px.bar(
        df,
        x="Mês",
        y="Proventos (R$)",
        color="Grupo",
        color_discrete_map=colors.AssetKindColors,
    )
    fig.update_xaxes(tickmode="array", tickvals=df["Mês"], tickformat="%b/%Y")
    st.plotly_chart(fig)

    if show_table:
        df = df.drop(columns=["Grupo"]).groupby("Mês").sum().reset_index()
        df["date"] = pd.to_datetime(df["Mês"])
        df["Ano"] = df["Mês"].map(lambda d: d.year)
        df["Mês"] = df["Mês"].map(
            lambda d: {
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
            }[d.month]
        )

        st.dataframe(
            df.pivot_table(index=["Ano", "Mês"], values=["date", "Proventos (R$)"])
            .sort_values("date")
            .drop(columns=["date"]),
            column_config={
                "Proventos (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
            },
        )


def monthly_yoc(
    df: pd.DataFrame,
    cumulative: bool,
):
    # Cumsum
    if cumulative:
        df["yoc"] = df.groupby("b3_code").yoc.cumsum()

    # Show DataFrame with are chart
    fig = px.bar(
        df,
        x="reference_date",
        y="yoc",
        color="b3_code",
        labels={"reference_date": "Mês", "yoc": "YoC Médio (%)", "b3_code": "Ativo"},
        barmode="group",
    )
    fig.update_xaxes(
        tickmode="array", tickvals=df["reference_date"], tickformat="%b/%Y"
    )
    st.plotly_chart(fig)


def bar_yoc_variation(df: pd.DataFrame, cumulative: bool, relative: bool):
    assert df.b3_code.nunique() == 1
    df = df.drop(columns="b3_code")
    cols = ["Yield on Cost (YoC)", "CDI", "CDB", "IPCA"]
    numeric_cols = list(set(df.columns) - set(["reference_date"]))

    if relative:
        df = df.copy()
        cols.pop(0)
        for c in numeric_cols:
            if c != "yoc":
                df[c] = df.yoc - df[c]

    if cumulative:
        df.loc[:, numeric_cols] = df[numeric_cols].cumsum()

    fig = px.bar(
        df.rename(
            columns=dict(
                reference_date="Mês",
                yoc="Yield on Cost (YoC)",
                cdi="CDI",
                ipca="IPCA",
                cdb="CDB",
            )
        ),
        x="Mês",
        y=cols,
        barmode="group",
    )
    fig.update_yaxes(title="Variação (%)")
    fig.update_xaxes(
        tickmode="array", tickvals=df["reference_date"], tickformat="%b/%Y"
    )
    st.plotly_chart(fig)


def earnings_by_asset_kind(df: pd.DataFrame):
    _earning_by(df, "asset_kind", colors.AssetKindColors)


def earnings_by_asset_code(df: pd.DataFrame):
    _earning_by(df, "b3_code")


def _earning_by(df: pd.DataFrame, by: str, color_map: dict[str, str] = None):
    if color_map is None:
        color_map = dict()

    fig = px.pie(
        df, names=by, color=by, values="total_earnings", color_discrete_map=color_map
    )
    fig.update_traces(textposition="inside", textinfo="label+percent+value")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)
