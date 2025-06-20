"""Home do dashboard."""

import streamlit as st
from app.analytics import constants
from app.analytics.components import charts, dataframes, metrics
from app.analytics.states.home import HomeState
from app.config import ST_CONFIG as config

# ===== Inicialização da página =====
state = HomeState()
state.update_state()

# ==== Título ====
st.title("Análise de Proventos")

# Caso existam proventos, exibir
if len(state.variables.asset_codes) > 0:
    # Métricas
    metrics.earning_global_metrics(state.variables.metrics)

    # Gráfico de proventos por mês
    charts.monthly_earnings(state.variables.earning_yield, show_table=True)

    # ==== Posição Atual ====
    st.subheader("Posição Atual", divider="gray")

    st.markdown("### Total de Proventos por Classes")
    cols = st.columns(2)

    # Proventos por Classe de Ativo
    with cols[0]:
        charts.earnings_by(state.variables.earning_yield, "asset_kind")

    # Proventos por ativo
    with cols[1]:
        charts.earnings_by(state.variables.earning_yield, "b3_code")

    # Proventos recebidos e a receber
    for title, cond in zip(
        ["Recebidos", "A Receber"],
        [
            state.variables.current_month_ey.payment_date <= state.variables.today,
            state.variables.current_month_ey.payment_date > state.variables.today,
        ],
    ):
        df = state.current_month_ey[cond]
        st.markdown(f"### {title} no Mês: `R$ {df.total_earnings.sum():.2f}`")
        dataframes.earning_yield_dataframe(df)

    # ==== Proventos por Ativo ====
    st.subheader("Proventos por Ativo", divider="gray")
    section = "earnings_by_asset"

    # Filtros
    cols = st.columns(5)
    cols[0].selectbox(
        "Ativo:",
        ["Todos"] + state.variables.asset_codes,
        key=state.register_component("filter_asset"),
        on_change=state.update_state,
    )
    cols[1].pills(
        "Tipo de provento:",
        constants.EarningKinds,
        selection_mode="multi",
        default=constants.EarningKinds,
        key=state.register_component("filter_earning_kind"),
        on_change=state.update_state,
    )
    cols[2].selectbox(
        "Filtrar data de:",
        ["Pagamento", "Custódia"],
        key=state.register_component("filter_date_kind"),
        on_change=state.update_state,
    )
    cols[3].date_input(
        "Data inicial:",
        key=state.register_component("filter_start_date"),
        value=state.variables.min_date,
        max_value=state.variables.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=state.update_state,
    )
    cols[4].date_input(
        "Data final:",
        key=state.register_component("filter_end_date"),
        value=state.variables.max_date,
        max_value=state.variables.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=state.update_state,
    )

    # Listagem de proventos
    dataframes.earning_yield_dataframe(state.variables.filtered_ey)
else:
    st.markdown("> Cadastre proventos e índices ecônomicos para acessar o dashboard.")
