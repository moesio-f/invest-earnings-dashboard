from datetime import date

import streamlit as st

from app.config import DASHBOARD_CONFIG as config
from app.dashboard import utils
from app.dashboard.api import api
from app.dashboard.components import charts
from app.dashboard.components import dataframes as cdf
from app.dashboard.components import metrics as cme
from app.dashboard.state import Manager
from app.db.models import AssetKind, EarningKind

# Estados da página
state = Manager.get_page_state("home")
state.today = date.today()
section_prefix = "__home_{}"
section_component_prefix = section_prefix + "_{}"
section_data_proxy = {
    name: Manager.get_proxied_data_state(name, section_prefix.format(name))
    for name in ["monthly_yoc", "earnings_by_asset"]
}


# === Inicializando estado de página ===
def update_state():
    # Is page initialized?
    initialize = not state.get("initialized", False)

    # Maybe update earning yield and others
    if initialize:
        # API Queries
        state.has_economic = len(api.economic_data()) > 0
        state.metrics = api.earning_metrics()
        state.earning_yield = api.earning_yield()
        state.earning_yield["kind"] = state.earning_yield.kind.map(
            lambda k: EarningKind.from_value(k).value
        )
        state.earning_yield["asset_kind"] = state.earning_yield.asset_kind.map(
            lambda k: AssetKind.from_value(k).value
        )

        # Get asset codes
        state.asset_codes = sorted(state.earning_yield.b3_code.unique().tolist())

        # Get minimum and max dates
        cols = ["hold_date", "payment_date"]
        state.min_date = state.earning_yield[cols].min(axis=None)
        state.max_date = state.earning_yield[cols].max(axis=None)

        # Get current month ey
        state.current_month_ey = state.earning_yield[
            state.earning_yield.payment_date.map(
                lambda d: (d.month == state.today.month)
                and (d.year == state.today.year)
            )
        ]

        # Set initialized flag
        state.initialized = True

    # === Section `mean_yoc` query/filtering ===
    section = section_data_proxy.get("monthly_yoc")
    asset = utils.safe_get_from_proxied_data(
        section, key="filter_asset", default="Todos"
    )
    date_col = utils.safe_get_from_proxied_data(
        section, key="filter_date_col", default="payment_date"
    )

    # Avoid re-query whenever possible
    if asset != state.get("monthly_yoc_asset", None) or date_col != state.get(
        "monthly_yoc_date_col", None
    ):
        if asset == "Todos":
            asset = None

        state.monthly_yoc = api.monthly_yoc(asset, date_col)
        state.monthly_yoc_asset = asset
        state.monthly_yoc_date_col = date_col

    # Filter
    min_date = utils.safe_get_from_proxied_data(
        section, key="filter_start_date", default=state.min_date
    )
    max_date = utils.safe_get_from_proxied_data(
        section, key="filter_end_date", default=state.max_date
    )
    state.filtered_monthly_yoc = (df := state.monthly_yoc)[
        (df.reference_date >= min_date) & (df.reference_date <= max_date)
    ]

    # === Section `earnings_by_asset` filtering ===
    df = state.earning_yield
    section = section_data_proxy.get("earnings_by_asset")
    if (
        not df.empty
        and (
            asset := utils.safe_get_from_proxied_data(
                section, key="filter_asset", default="Todos"
            )
        )
        != "Todos"
    ):
        df = df[df.b3_code == asset]

    if not df.empty:
        kind = utils.safe_get_from_proxied_data(
            section, key="filter_earning_kind", default=[k.value for k in EarningKind]
        )
        df = df[df.kind.isin(kind)]

    if not df.empty:
        dcol = {"Pagamento": "payment_date", "Custódia": "hold_date"}[
            utils.safe_get_from_proxied_data(
                section, key="filter_date_kind", default="Pagamento"
            )
        ]
        ds, de = (
            utils.safe_get_from_proxied_data(
                section, key="filter_start_date", default=state.min_date
            ),
            utils.safe_get_from_proxied_data(
                section, key="filter_end_date", default=state.max_date
            ),
        )
        df = df[(df[dcol] >= ds) & (df[dcol] <= de)]

    # Make the filtered version available
    state.filtered_ey = df


update_state()


# ==== Título ====
st.title("Análise de Proventos")

# Caso existam proventos, exibir
if state.asset_codes and state.has_economic:
    # Métricas
    cme.earning_global_metrics(state.metrics)

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
            state.current_month_ey.payment_date <= state.today,
            state.current_month_ey.payment_date > state.today,
        ],
    ):
        df = state.current_month_ey[cond]
        st.markdown(f"### {title} no Mês: `R$ {df.total_earnings.sum():.2f}`")
        cdf.earning_yield_dataframe(df)

    # ==== Evolução do YoC ====
    st.subheader("Yield on Cost Médio Mensal", divider="gray")
    section = "monthly_yoc"

    # YoC mensal por diferentes grupos
    cols = st.columns(4)
    cols[0].selectbox(
        "Ativo base:",
        ["Todos"] + state.asset_codes,
        key=section_component_prefix.format(section, "filter_asset"),
    )
    cols[1].selectbox(
        "Agrupar por data de:",
        ["payment_date", "hold_date"],
        key=section_component_prefix.format(section, "filter_date_col"),
        format_func=dict(payment_date="Pagamento", hold_date="Custódia").get,
    )
    cols[2].date_input(
        "Data inicial:",
        key=section_component_prefix.format(section, "filter_start_date"),
        value=state.min_date,
        max_value=state.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=update_state,
    )
    cols[3].date_input(
        "Data final:",
        key=section_component_prefix.format(section, "filter_end_date"),
        value=state.max_date,
        max_value=state.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=update_state,
    )
    cumulative = st.toggle(
        "Cumulativo",
        value=False,
    )
    charts.monthly_yoc(state.filtered_monthly_yoc, cumulative)

    # ==== Proventos por Ativo ====
    st.subheader("Proventos por Ativo", divider="gray")
    section = "earnings_by_asset"

    # Filtros
    cols = st.columns(5)
    cols[0].selectbox(
        "Ativo:",
        ["Todos"] + state.asset_codes,
        key=section_component_prefix.format(section, "filter_asset"),
        on_change=update_state,
    )
    cols[1].pills(
        "Tipo de provento:",
        (values := [k.value for k in EarningKind]),
        selection_mode="multi",
        default=values,
        key=section_component_prefix.format(section, "filter_earning_kind"),
        on_change=update_state,
    )
    cols[2].selectbox(
        "Filtrar data de:",
        ["Pagamento", "Custódia"],
        key=section_component_prefix.format(section, "filter_date_kind"),
        on_change=update_state,
    )
    cols[3].date_input(
        "Data inicial:",
        key=section_component_prefix.format(section, "filter_start_date"),
        value=state.min_date,
        max_value=state.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=update_state,
    )
    cols[4].date_input(
        "Data final:",
        key=section_component_prefix.format(section, "filter_end_date"),
        value=state.max_date,
        max_value=state.max_date,
        format=config.ST_DATE_FORMAT,
        on_change=update_state,
    )

    # Listagem de proventos
    cdf.earning_yield_dataframe(state.filtered_ey)
else:
    st.markdown("> Cadastre proventos e índices ecônomicos para acessar o dashboard.")
