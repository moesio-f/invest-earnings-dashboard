from datetime import date

import pandas as pd
import streamlit as st
from pandera.typing import DataFrame

from app.analytics.entities import EarningMetrics


def earning_global_metrics(
    metrics: EarningMetrics,
):

    for container, label, value, help in zip(
        [*st.columns(4 + 2)[1:-1], *st.columns(4 + 2)[1:-1]],
        [
            "Ativos com Proventos",
            "Proventos Recebidos",
            "Proventos a Receber",
            "YoC Médio",
            "YoC Médio (1M)",
            "YoC Médio (3M)",
            "YoC Médio (6M)",
            "Yoc Médio (12M)",
        ],
        [
            metrics.n_assets_with_earnings,
            f"R$ {metrics.collected_earnings:.2f}",
            f"R$ {metrics.to_collect_earnings:.2f}",
            f"{metrics.mean_yoc:.2f}%",
            *[
                f"{getattr(metrics, f'mean_yoc_{k}'):.2f}%"
                for k in ["current_month", "3m", "6m", "12m"]
            ],
        ],
        [
            "Quantidade de ativos que possuem proventos.",
            "Total recebido em proventos (recebidos e a receber).",
            "Total a receber de proventos.",
            "Média dos YoC de cada provento (recebido e a receber): `mean(YoC)`.",
            "Média dos YoC de cada provento no mês corrente.",
            "Média dos YoC de cada provento nos últimos 3 meses.",
            "Média dos YoC de cada provento nos últimos 6 meses.",
            "Média dos YoC de cada provento nos últimos 12 meses.",
        ],
    ):
        container.metric(label, value, help=help)
