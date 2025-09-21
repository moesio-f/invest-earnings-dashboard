"""YoC vs Índices Econômicos."""

from datetime import date

import pandas as pd
import streamlit as st
from app.analytics.components import charts, metrics
from app.analytics.states.economic_index import EconomicIndexState
from app.config import ST_CONFIG as config

# ===== Inicialização do estado da página =====
state = EconomicIndexState()
state.update_state()
today = date.today()

# =============================================
# ==== Título ====
st.title("Yield on Cost (YoC) vs Indicadores Econômicos")

# Caso existam proventos, exibir
if len(state.variables.earning_yield) > 0:
    cols = st.columns(4)
    date_col = cols[0].selectbox(
        "Agrupar por data de:",
        ["hold_date", "payment_date"],
        format_func=dict(payment_date="Pagamento", hold_date="Custódia").get,
        disabled=True,
    )
    asset = cols[1].selectbox(
        "Ativo:",
        ["Todos"] + state.variables.asset_codes,
    )
    start_date = cols[2].date_input(
        "Data inicial:",
        value=today.replace(day=1, month=today.month - 1),
        max_value=state.variables.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=state.update_state,
    )
    end_date = cols[3].date_input(
        "Data final:",
        value=today,
        max_value=state.variables.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=state.update_state,
    )

    cumulative = st.toggle("Cumulativo", value=False)
    relative_bars = st.toggle("Valores relativos", value=False)

    # Load DataFrame
    df = state.variables.earning_yield.copy().rename(
        columns=dict(ipca_on_hold_month="ipca", cdi_on_hold_month="cdi")
    )

    # Guarantee dates are end of month
    df["reference_date"] = (
        pd.to_datetime(df[date_col]) + pd.offsets.MonthEnd(0)
    ).dt.date

    # Drop unused columns
    df = df[
        [
            "b3_code",
            "reference_date",
            "yoc",
            "cdi",
            "ipca",
            "avg_price",
            "value_per_share",
            "total_earnings",
        ]
    ]

    # Add CDB column
    df["cdb"] = 0.85 * df.cdi

    # Filter dates
    df = df[(df.reference_date >= start_date) & (df.reference_date <= end_date)]

    # Maybe target is group of assets?
    if asset == "Todos":
        df["b3_code"] = "Todos"

    # Filter group/asset
    df = df[df.b3_code == asset]

    # Apply aggregate function
    df = (
        df.groupby(["b3_code", "reference_date"])
        .agg(
            {
                "yoc": "mean",
                "cdi": "mean",
                "ipca": "mean",
                "cdb": "mean",
                "avg_price": "mean",
                "value_per_share": "sum",
                "total_earnings": "sum",
            }
        )
        .reset_index()
    )

    # Show charts and metrics
    metrics.montly_index_yoc_metrics(df)
    charts.bar_yoc_variation(
        df,
        cumulative,
        relative_bars,
    )
else:
    st.markdown("> Cadastre proventos e índices ecônomicos para acessar o dashboard.")
