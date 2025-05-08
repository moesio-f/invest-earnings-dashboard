from datetime import date

import streamlit as st
from pandera.typing import DataFrame

from app.analytics.entities import EarningYield
from app.dashboard.scoped_state import ScopedState


def earning_global_metrics(
    df: DataFrame[EarningYield],
):

    for container, label, value, help in zip(
        [*st.columns(6)[1:-1]],
        [
            "Ativos com Proventos",
            "Total de Proventos",
            "Proventos a Receber",
            "YoC Médio",
        ],
        [
            df.b3_code.nunique(),
            f"R$ {df.total_earnings.sum():.2f}",
            f"R$ {df[df.payment_date > date.today()].total_earnings.sum():.2f}",
            f"{df.yoc.mean():.2f}%",
        ],
        [
            "Quantidade de ativos que possuem proventos.",
            "Total recebido em proventos (recebidos e a receber).",
            "Total a receber de proventos.",
            "Yield on Cost médio de todos os proventos recebidos.",
        ],
    ):
        container.metric(label, value, help=help)
