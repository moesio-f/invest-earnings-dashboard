"""Gráficos para visualização
de entidades.
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from pandera.typing import DataFrame

from app.analytics.entities import (
    EarningYield,
    MonthlyEarning,
    MonthlyYoC,
    MonthlyIndexYoC,
)


def monthly_earnings(df: DataFrame[MonthlyEarning], show_table: bool = False):
    df = df.rename(
        columns=dict(
            reference_date="Mês",
            total_earnings="Proventos (R$)",
            group="Grupo",
        )
    )
    fig = px.bar(
        df,
        x="Mês",
        y="Proventos (R$)",
        color="Grupo",
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
    df: DataFrame[MonthlyYoC],
):
    # Show DataFrame with are chart
    fig = px.bar(
        df,
        x="reference_date",
        y="yoc",
        color="group",
        labels={"reference_date": "Mês", "yoc": "YoC Médio (%)", "group": "Grupo"},
        barmode="group",
    )
    fig.update_xaxes(
        tickmode="array", tickvals=df["reference_date"], tickformat="%b/%Y"
    )
    st.plotly_chart(fig)


def bar_yoc_variation(df: DataFrame[MonthlyIndexYoC], relative: bool):
    cols = ["Yield on Cost (YoC)", "CDI", "CDI Líquido", "IPCA"]
    if relative:
        df = df.copy()
        cols.pop(0)
        for c in ["cdi", "ipca", "cdb"]:
            df.loc[:, [c]] = df.yoc - df[c]

    fig = px.bar(
        df.rename(
            columns=dict(
                reference_date="Mês",
                yoc="Yield on Cost (YoC)",
                cdi="CDI",
                ipca="IPCA",
                cdb="CDI Líquido",
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


def earnings_by(df: DataFrame[EarningYield], by: str):
    fig = px.pie(df, names=by, values="total_earnings")
    fig.update_traces(textposition="inside", textinfo="label+percent+value")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)
