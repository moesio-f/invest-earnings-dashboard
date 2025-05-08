from datetime import date

import streamlit as st

from app.api.v1_facade import v1Facade
from app.config import DASHBOARD_CONFIG as config
from app.dashboard.components import dataframes as cdf
from app.dashboard.scoped_state import ScopedState
from app.db.models import EarningKind

state = ScopedState("home")
api = v1Facade()


# === Inicializando estado de página ===
def update_state(update_earning_yield: bool = False):
    # Is page initialized?
    initialize = not state.get("initialized", False)

    # Update earnings
    state.earnings = api.earnings()
    state.asset_codes = list(set(e.asset_b3_code for e in state.earnings))

    # Maybe update earning yield
    state._earning_yield = state.get("_earning_yield", None)
    if state._earning_yield is None or update_earning_yield:
        state._earning_yield = api.earning_yield()
        state._earning_yield["kind"] = state._earning_yield.kind.map(
            lambda k: EarningKind.from_value(k).value
        )

    # Filter
    df = state._earning_yield
    if (
        not df.empty
        and (asset := st.session_state.get("filter_asset", "Todos")) != "Todos"
    ):
        df = df[df.b3_code == asset]

    if not df.empty:
        kind = st.session_state.get(
            "filter_earning_kind", [k.value for k in EarningKind]
        )
        df = df[df.kind.isin(kind)]

    if not df.empty:
        dcol = {"Pagamento": "payment_date", "Custódia": "hold_date"}[
            st.session_state.get("filter_date_kind", "Pagamento")
        ]
        ds, de = st.session_state.get(
            "filter_start_date", date(2000, 1, 1)
        ), st.session_state.get("filter_end_date", date.today())
        df = df[(df[dcol] >= ds) & (df[dcol] <= de)]

    # Make the filtered version available
    state.earning_yield = df

    # If we initialized, set flag
    if initialize:
        state.initialized = True


update_state()

# ==== Título ====
st.title("Análise de Proventos")

# === Listagem de proventos ===
st.subheader("Lista de Proventos", divider="gray")

# Filtros
cols = st.columns(5)
cols[0].selectbox(
    "Ativo:",
    ["Todos"] + state.asset_codes,
    key="filter_asset",
    on_change=update_state,
)
cols[1].pills(
    "Tipo de provento:",
    (values := [k.value for k in EarningKind]),
    selection_mode="multi",
    default=values,
    key="filter_earning_kind",
    on_change=update_state,
)
cols[2].selectbox(
    "Filtrar data de:",
    ["Pagamento", "Custódia"],
    key="filter_date_kind",
    on_change=update_state,
)
cols[3].date_input(
    "Data inicial:",
    key="filter_start_date",
    value=date(2000, 1, 1),
    max_value="today",
    format=config.ST_DATE_FORMAT,
    on_change=update_state,
)
cols[4].date_input(
    "Data final:",
    key="filter_end_date",
    value="today",
    format=config.ST_DATE_FORMAT,
    on_change=update_state,
)

# Listagem de proventos
cdf.earning_yield_dataframe(state.earning_yield)
