"""YoC vs Índices Econômicos."""

from datetime import date

import streamlit as st
from app.analytics.components import charts, metrics
from app.analytics.states.economic_index import EconomicIndexState
from app.config import ST_CONFIG as config

# ===== Inicialização do estado da página =====
state = EconomicIndexState()
state.update_state()

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
    )
    asset = cols[1].selectbox(
        "Ativo:",
        ["Todos"] + state.variables.asset_codes,
    )
    start_date = cols[2].date_input(
        "Data inicial:",
        value=state.min_date,
        max_value=state.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=update_state,
    )
    end_date = cols[3].date_input(
        "Data final:",
        value=state.max_date,
        max_value=state.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=update_state,
    )

    cumulative = st.toggle("Cumulativo", value=False)
    relative_bars = st.toggle("Valores relativos", value=False)

    # Load DataFrame
    df = state.variables.earning_yield.copy()
    df["group"] = df.b3_code
    df = df.drop(columns=["b3_code", "earning_kind"])

    # Filter dates
    df = df[(df.reference_date >= start_date) & (df.reference_date <= end_date)]

    # Maybe target is group of assets?
    if asset not in state.variables.asset_codes:
        if asset == "Todos":
            df["group"] = "Todos"
        else:
            df["group"] = df.asset_kind
        df = df.drop(columns=["asset_kind"])

    # Filter group/asset
    df = df[(df.group == asset)]

    # Show charts and metrics
    metrics.montly_index_yoc_metrics(df)
    charts.bar_yoc_variation(
        df,
        cumulative,
        relative_bars,
    )
else:
    st.markdown("> Cadastre proventos e índices ecônomicos para acessar o dashboard.")
