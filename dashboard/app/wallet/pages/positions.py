"""Página de visualização das posições."""

import streamlit as st
from app.wallet import constants
from app.wallet.components import charts, dataframes, metrics
from app.wallet.states.positions import PositionsState

# ===== Inicialização da página =====
state = PositionsState()
state.update_state()

# ==================================================================
# === Título ===
st.title("Posição de Investimentos")

# === Patrimônio e Distribuição ===
st.pills(
    "Meses:",
    ["3M", "6M", "12M", "24M"],
    key=state.register_component("n_months_history"),
    default="3M",
)

col_a, col_b = st.columns(2)

with col_a:
    charts.wealth_history(state.variables.history)

with col_b:
    charts.return_history(state.variables.history)


# === Métricas globais ===
metrics.position_metrics(state.variables.history)

# === Posição por classe de ativo ===
total_balance = state.variables.current_position.balance.sum()
for idx, kind in enumerate(constants.AssetKinds):
    df = state.variables.current_position[
        state.variables.current_position.asset_kind == kind
    ].drop(columns=["asset_kind"])
    if len(df) > 0:
        with st.expander(
            constants.AssetKindMapper.get(kind, kind), expanded=(idx == 0)
        ):
            metrics.current_position_metrics(df, total_balance)
            dataframes.position_dataframe(df.sort_values("b3_code"))
