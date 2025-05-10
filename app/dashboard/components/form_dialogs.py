from typing import Callable

import streamlit as st

from app.config import DASHBOARD_CONFIG as config
from app.dashboard.state import Manager, ScopedState
from app.db.models import AssetKind, EarningKind, EconomicIndex, TransactionKind

_PREFIX = "__form_create_dialog_{}"


@st.dialog("Adicionar ativo")
def asset_create(create_fn: Callable[[ScopedState], None]):
    prefix = _PREFIX.format("asset")

    with st.form("asset_create", enter_to_submit=False, border=False):
        st.text_input("Código B3:", key=f"{prefix}_b3_code")
        st.text_input("Nome do ativo:", key=f"{prefix}_name")
        st.text_area("Descrição do ativo:", key=f"{prefix}_description")
        st.pills(
            "Tipo do ativo:",
            [k.value for k in AssetKind],
            key=f"{prefix}_kind",
        )

        submit = st.form_submit_button(
            "Adicionar",
            on_click=create_fn,
            args=[Manager.get_proxied_data_state("asset_create", prefix)],
        )

        # If submit, run on_click and rerun app
        if submit:
            st.rerun()


@st.dialog("Adicionar transação")
def add_transaction(
    asset_codes: list[str],
    create_fn: Callable[[ScopedState], None],
):
    prefix = _PREFIX.format("transaction")
    with st.form("transaction_create", enter_to_submit=False, border=False):
        st.selectbox(
            "Ativo:",
            asset_codes,
            key=f"{prefix}_asset_b3_code",
        )
        st.pills(
            "Tipo da transação:",
            [k.value for k in TransactionKind],
            key=f"{prefix}_kind",
        )
        st.date_input(
            "Data da transação:",
            key=f"{prefix}_date",
            format=config.ST_DATE_FORMAT,
        )
        st.number_input(
            "Valor por unidade (R$):",
            key=f"{prefix}_value_per_share",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%0.2f",
        )
        st.number_input(
            "Quantidade de unidades:",
            key=f"{prefix}_shares",
            min_value=0,
            value=0,
            step=1,
            format="%d",
        )
        submit = st.form_submit_button(
            "Adicionar",
            on_click=create_fn,
            args=[Manager.get_proxied_data_state("transaction_create", prefix)],
        )

        # If submit, run on_click and rerun app
        if submit:
            st.rerun()


@st.dialog("Cadastrar Provento")
def add_earning(
    asset_codes: list[str],
    create_fn: Callable[[ScopedState], None],
):
    prefix = _PREFIX.format("earning")
    with st.form("earning_create", enter_to_submit=False, border=False):
        st.selectbox("Ativo:", asset_codes, key=f"{prefix}_asset_b3_code")
        st.date_input(
            "Data de custódia:",
            key=f"{prefix}_hold_date",
            format=config.ST_DATE_FORMAT,
        )
        st.date_input(
            "Data de pagamento:",
            key=f"{prefix}_payment_date",
            format=config.ST_DATE_FORMAT,
        )
        st.number_input(
            "Valor por unidade (R$):",
            key=f"{prefix}_value_per_share",
            min_value=0.0,
            step=0.01,
            value=0.0,
            format="%0.2f",
        )
        st.pills(
            "Tipo de provento:",
            [k.value for k in EarningKind],
            key=f"{prefix}_kind",
        )
        st.number_input(
            "Imposto de Renda Retido na Fonte (%):",
            key=f"{prefix}_ir_percentage",
            min_value=0.0,
            step=0.01,
            value=0.0,
            format="%0.2f",
        )
        submit = st.form_submit_button(
            "Adicionar",
            on_click=create_fn,
            args=[Manager.get_proxied_data_state("earning_create", prefix)],
        )

        # If submit, run on_click and rerun app
        if submit:
            st.rerun()


@st.dialog("Cadastrar Dado Econômico")
def add_economic_data(
    create_fn: Callable[[ScopedState], None],
):
    prefix = _PREFIX.format("economic_data")
    with st.form("economic_data_create", enter_to_submit=False, border=False):
        st.pills(
            "Índice:",
            list(EconomicIndex),
            format_func=lambda e: e.value,
            key=f"{prefix}_index",
        )
        st.date_input(
            "Data de referência:",
            key=f"{prefix}_reference_date",
            format=config.ST_DATE_FORMAT,
        )
        st.number_input(
            "Variação (%):",
            key=f"{prefix}_percentage_change",
            min_value=0.0,
            step=0.01,
            value=0.0,
            format="%0.2f",
        )
        submit = st.form_submit_button(
            "Adicionar",
            on_click=create_fn,
            args=[Manager.get_proxied_data_state("economic_data_create", prefix)],
        )

        # If submit, run on_click and rerun app
        if submit:
            st.rerun()


@st.dialog("Upload de CSV")
def text_upload(fn: Callable[[ScopedState], None], help: str):
    prefix = _PREFIX.format("text_upload")

    with st.form("text_upload", enter_to_submit=False, border=False):
        st.markdown(help)
        st.text_area("Conteúdo do CSV:", key=f"{prefix}_csv_contents")
        submit = st.form_submit_button(
            "Adicionar",
            on_click=fn,
            args=[Manager.get_proxied_data_state("text_upload", prefix)],
        )

        # If submit, run on_click and rerun app
        if submit:
            st.rerun()
