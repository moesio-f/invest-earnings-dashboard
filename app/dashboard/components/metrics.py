from datetime import date

import pandas as pd
import streamlit as st
from pandera.typing import DataFrame

from app.analytics.entities import EarningYield


def earning_global_metrics(
    df: DataFrame[EarningYield],
):
    dt = pd.to_datetime(df.payment_date)

    def _between(start, end):
        return df[(dt >= start) & (dt <= end)]

    def _last_months(n: int):
        today = pd.to_datetime(date.today())
        start = today + pd.offsets.MonthBegin(-n)
        end = today + pd.offsets.MonthEnd()
        return _between(start, end)

    for container, label, value, help in zip(
        [*st.columns(4 + 2)[1:-1], *st.columns(4 + 2)[1:-1]],
        [
            "Ativos com Proventos",
            "Total de Proventos",
            "Proventos a Receber",
            "YoC Médio",
            "YoC Médio (1M)",
            "YoC Médio (3M)",
            "YoC Médio (6M)",
            "Yoc Médio (12M)",
        ],
        [
            df.b3_code.nunique(),
            f"R$ {df.total_earnings.sum():.2f}",
            f"R$ {df[df.payment_date > date.today()].total_earnings.sum():.2f}",
            f"{df.yoc.mean():.2f}%",
            *[f"{_last_months(n).yoc.mean():.2f}%" for n in (1, 3, 6, 12)],
        ],
        [
            "Quantidade de ativos que possuem proventos.",
            "Total recebido em proventos (recebidos e a receber).",
            "Total a receber de proventos.",
            "Média dos YoC de cada provento em todo período: `mean(sum(100 * Provento por Unidade / PM Ativo))`.",
            "Média dos YoC de cada provento no mês corrente.",
            "Média dos YoC de cada provento nos últimos 3 meses.",
            "Média dos YoC de cada provento nos últimos 6 meses.",
            "Média dos YoC de cada provento nos últimos 12 meses.",
        ],
    ):
        container.metric(label, value, help=help)
