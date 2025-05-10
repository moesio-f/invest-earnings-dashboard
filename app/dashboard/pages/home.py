from datetime import date

import streamlit as st

from app.config import DASHBOARD_CONFIG as config
from app.dashboard.api import api
from app.dashboard.components import charts
from app.dashboard.components import dataframes as cdf
from app.dashboard.components import metrics as cme
from app.dashboard.state import Manager
from app.db.models import AssetKind, EarningKind

state = Manager.get_page_state("home")
today = date.today()


# === Inicializando estado de página ===
def update_state(update_earning_yield: bool = False):
    # Is page initialized?
    initialize = not state.get("initialized", False)

    # Maybe update earning yield and others
    state.earning_yield = state.get("_earning_yield", None)
    if state.earning_yield is None or update_earning_yield:
        state.earning_yield = api.earning_yield()
        state.earning_yield["kind"] = state.earning_yield.kind.map(
            lambda k: EarningKind.from_value(k).value
        )
        state.earning_yield["asset_kind"] = state.earning_yield.asset_kind.map(
            lambda k: AssetKind.from_value(k).value
        )
        state.asset_codes = state.earning_yield.b3_code.unique().tolist()

    # Filter
    df = state.earning_yield
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
    state.filtered_ey = df
    state.current_month_ey = state.earning_yield[
        state.earning_yield.payment_date.map(
            lambda d: (d.month == today.month) and (d.year == today.year)
        )
    ]

    # If we initialized, set flag
    if initialize:
        state.initialized = True


update_state()


# ==== Título ====
st.title("Análise de Proventos")

# Caso existam proventos, exibir
if state.asset_codes:
    # Métricas
    cme.earning_global_metrics(api.earning_metrics())

    # Gráfico de proventos por mês
    charts.monthly_earnings(api.monthly_earning(), show_table=True)

    # ==== Posição Atual ====
    st.subheader("Posição Atual", divider="gray")

    st.markdown("### Total de Proventos por Classes")
    cols = st.columns(2)

    # Proventos por Classe de Ativo
    with cols[0]:
        charts.earnings_by(state.earning_yield, "asset_kind")

    # Proventos por ativo
    with cols[1]:
        charts.earnings_by(state.earning_yield, "b3_code")

    # Proventos recebidos e a receber
    for title, cond in zip(
        ["Recebidos", "A Receber"],
        [
            state.current_month_ey.payment_date <= today,
            state.current_month_ey.payment_date > today,
        ],
    ):
        df = state.current_month_ey[cond]
        st.markdown(f"### {title} no Mês: `R$ {df.total_earnings.sum():.2f}`")
        cdf.earning_yield_dataframe(df)

    # ==== Evolução do YoC ====
    st.subheader("Yield on Cost Médio Mensal", divider="gray")

    # YoC mensal por diferentes grupos
    cols = st.columns(2)
    asset = cols[0].selectbox(
        "Ativo base:",
        [None] + state.asset_codes,
        format_func=lambda a: "Todos" if not a else a,
    )
    date_col = cols[1].selectbox(
        "Agrupar por data de:",
        ["payment_date", "hold_date"],
        format_func=dict(payment_date="Pagamento", hold_date="Custódia").get,
    )
    charts.monthly_yoc(api.monthly_yoc(asset, date_col))

    # ==== Proventos por Ativo ====
    st.subheader("Proventos por Ativo", divider="gray")

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
        max_value=date(2050, 1, 1),
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
    cdf.earning_yield_dataframe(state.filtered_ey)
else:
    st.markdown("> Cadastre proventos para acessar o dashboard.")
