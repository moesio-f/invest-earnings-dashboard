from datetime import date

import streamlit as st

from app.dashboard.api import api
from app.dashboard.components import charts
from app.dashboard.state import Manager

state = Manager.get_page_state("economic_index")
today = date.today()


# === Inicializando estado de página ===
def update_state():
    # Is page initialized?
    initialize = not state.get("initialized", False)

    if initialize:
        state.asset_codes = list(sorted(set(e.asset_b3_code for e in api.earnings())))
        state.initialized = True


update_state()


# ==== Título ====
st.title("Yield on Cost (YoC) vs Indicadores Ecônomicos")

# Caso existam proventos, exibir
if state.asset_codes:
    cols = st.columns(2)
    date_col = cols[0].selectbox(
        "Agrupar por data de:",
        ["hold_date", "payment_date"],
        format_func=dict(payment_date="Pagamento", hold_date="Custódia").get,
    )
    asset = cols[1].selectbox(
        "Ativo:",
        ["Todos"] + state.asset_codes,
    )
    cumulative = st.toggle("Cumulativo", value=False)
    relative_bars = st.toggle("Valores relativos", value=False)
    charts.bar_yoc_variation(
        (df := api.monthly_index_yoc(asset if asset != "Todos" else None, date_col))[
            df.group == asset
        ],
        cumulative,
        relative_bars,
    )
else:
    st.markdown("> Cadastre proventos para acessar o dashboard.")
