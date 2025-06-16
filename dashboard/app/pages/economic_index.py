from datetime import date

import streamlit as st

from app.config import DASHBOARD_CONFIG as config
from app.dashboard.api import api
from app.dashboard.components import charts, metrics
from app.dashboard.state import Manager

state = Manager.get_page_state("economic_index")
today = date.today()


# === Inicializando estado de página ===
def update_state():
    # Is page initialized?
    initialize = not state.get("initialized", False)

    if initialize:
        state.has_economic = len(api.economic_data()) > 0
        cols = ["hold_date", "payment_date"]
        earning_yield = api.earning_yield()
        state.asset_codes = sorted(earning_yield.b3_code.unique().tolist())
        state.min_date = earning_yield[cols].min(axis=None)
        state.max_date = earning_yield[cols].max(axis=None)
        state.initialized = True


update_state()


# ==== Título ====
st.title("Yield on Cost (YoC) vs Indicadores Econômicos")

# Caso existam proventos, exibir
if state.asset_codes and state.has_economic:
    cols = st.columns(4)
    date_col = cols[0].selectbox(
        "Agrupar por data de:",
        ["hold_date", "payment_date"],
        format_func=dict(payment_date="Pagamento", hold_date="Custódia").get,
    )
    asset = cols[1].selectbox(
        "Ativo:",
        ["Todos"] + state.asset_codes,
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
    df = api.monthly_index_yoc(asset if asset != "Todos" else None, date_col)
    df = df[
        (df.group == asset)
        & (df.reference_date >= start_date)
        & (df.reference_date <= end_date)
    ]
    metrics.montly_index_yoc_metrics(df)
    charts.bar_yoc_variation(
        df,
        cumulative,
        relative_bars,
    )
else:
    st.markdown("> Cadastre proventos e índices ecônomicos para acessar o dashboard.")
