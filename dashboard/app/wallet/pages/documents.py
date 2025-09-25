"""Página de visualização das posições."""

from datetime import date

import streamlit as st
from app.config import ST_CONFIG as config
from app.utils.state import PageState
from app.wallet.client import WalletApi
from app.wallet.components import dataframes

# ===== Inicialização da página =====
state = PageState("documents")
today = date.today()
documents = WalletApi.list_documents().sort_values("publish_date", ascending=False)

# ==================================================================
# === Título ===
st.title("Relatórios & Documentos")

# === Documentos ===
cols = st.columns(3)
asset = cols[0].selectbox(
    "Ativo:",
    ["Todos"] + documents.asset_b3_code.sort_values().unique().tolist(),
    key=state.register_component("filter_asset_code"),
)
start_date = cols[1].date_input(
    "Data inicial:",
    key=state.register_component("filter_start_date"),
    value=today.replace(day=1),
    format=config.ST_DATE_FORMAT,
)
end_date = cols[2].date_input(
    "Data final:",
    key=state.register_component("filter_end_date"),
    value=today,
    format=config.ST_DATE_FORMAT,
)


documents = documents[
    (documents.publish_date >= start_date) & (documents.publish_date <= end_date)
]
if asset != "Todos":
    documents = documents[documents.asset_b3_code == asset]

dataframes.document_dataframe(documents)
