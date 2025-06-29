"""Métricas."""

import logging

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


def earning_global_metrics(
    metrics: dict,
):
    logger.debug("Received following metrics: %s", metrics.keys())
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
            metrics.get("n_assets_with_earnings"),
            f"R$ {metrics.get('collected_earnings'):,.2f}",
            f"R$ {metrics.get('to_collect_earnings'):,.2f}",
            f"{metrics.get('mean_yoc'):.2f}%",
            *[
                f"{metrics.get(f'mean_yoc_{k}'):.2f}%"
                for k in ["1m", "3m", "6m", "12m"]
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


def montly_index_yoc_metrics(df: pd.DataFrame):
    for container, label, value, help in zip(
        [
            *st.columns(4 + 2)[1:-1],
            *st.columns(4 + 2)[1:-1],
            *st.columns(4 + 2)[1:-1],
            *st.columns(4 + 2)[1:-1],
        ],
        [
            "Total de Meses",
            "Meses Acima do CDI",
            "Meses Acima do IPCA",
            "Meses Acima do CDB",
            "YoC Total",
            "CDI Total",
            "CDB Total",
            "IPCA Total",
            "Equivalência LCI",
            "Equivalência CDB",
            "Equivalência CDI+",
            "Equivalência IPCA+",
            "Média do Preço Médio",
            "Provento Médio por Unidade",
            "Média de Proventos Totais",
            "Total de Proventos",
        ],
        [
            len(df),
            *[(df.yoc > df[c]).sum() for c in ["cdi", "ipca", "cdb"]],
            *[f"{df[c].sum():.2f}%" for c in ["yoc", "cdi", "cdb", "ipca"]],
            *[f"{100 * df.yoc.mean() / df[c].mean():.2f}%" for c in ["cdi", "cdb"]],
            *[f"{12 * (df.yoc - df[c]).mean():.2f}%" for c in ["cdi", "ipca"]],
            f"R$ {df.avg_price.mean():,.2f}",
            f"R$ {df.value_per_share.mean():,.2f}",
            f"R$ {df.total_earnings.mean():,.2f}",
            f"R$ {df.total_earnings.sum():,.2f}",
        ],
        [
            "Quantidade de meses presentes na análise",
            "Quantidade meses com rendimento maior ou igual ao CDI.",
            "Quantidade meses com rendimento maior ou igual ao IPCA.",
            "Quantidade meses com rendimento maior ou igual ao CDI Líquido (85% do CDI).",
            "YoC total.",
            "CDI total.",
            "IPCA total.",
            "85% do CDI total. Representa o equivalente ao CDB.",
            "Taxa de rendimento equivalente a um LCI/LCA atrlado ao CDI.",
            "Taxa de rendimento para um CDB (15% IR).",
            "Taxa de rendimento equivalente para investimentos CDI + X% a.a.",
            "Taxa de rendimento equivalente para IPCA + X% a.a.",
            "Média do preço médio pago no ativo durante a data de custódia.",
            "Média dos proventos por unidade pagos por mês.",
            "Média dos proventos total por mês.",
            "Total de proventos.",
        ],
    ):
        container.metric(label, value, help=help)
