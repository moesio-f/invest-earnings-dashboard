from datetime import date
from typing import Callable

import streamlit as st
from app.config import DASHBOARD_CONFIG as config
from app.dashboard.state import Manager, ScopedState
from app.db.models import AssetKind, EarningKind, EconomicIndex, TransactionKind

_PREFIX = "__form_dialog_{}"


def _asset_dialog(
    prefix: str,
    on_click: Callable[[ScopedState], None] = None,
    on_click_delete: Callable[[], None] = None,
    b3_code=None,
    b3_editable: bool = True,
    name=None,
    name_editable: bool = True,
    description=None,
    description_editable: bool = True,
    kind=None,
    kind_editable: bool = True,
    added=None,
    added_editable: bool = False,
    submit_text: str = "Adicionar",
):
    prefix = _PREFIX.format(prefix)
    with st.form(f"{prefix}_form", enter_to_submit=False, border=False):
        st.text_input(
            "Código B3:",
            key=f"{prefix}_b3_code",
            value=b3_code,
            disabled=not b3_editable,
        )
        st.text_input(
            "Nome do ativo:",
            key=f"{prefix}_name",
            value=name,
            disabled=not name_editable,
        )
        st.text_area(
            "Descrição do ativo:",
            key=f"{prefix}_description",
            value=description,
            disabled=not description_editable,
        )
        st.pills(
            "Tipo do ativo:",
            [k.value for k in AssetKind],
            key=f"{prefix}_kind",
            default=kind,
            disabled=not kind_editable,
        )

        if added_editable:
            st.date_input(
                "Data de adição:",
                key=f"{prefix}_added",
                format=config.ST_DATE_FORMAT,
                value=added,
            )

        submit = st.form_submit_button(
            submit_text,
            on_click=on_click,
            args=[Manager.get_proxied_data_state("asset_dialog", prefix)],
        )

        # If submit, run on_click and rerun app
        if submit:
            st.rerun()


def _transaction_dialog(
    prefix: str,
    asset_codes: list[str],
    on_click: Callable[[ScopedState], None] = None,
    asset_code_editable: bool = True,
    kind=None,
    kind_editable: bool = True,
    transaction_date=None,
    transaction_date_editable: bool = True,
    value_per_share=0.0,
    value_per_share_editable: bool = True,
    shares=0,
    shares_editable: bool = True,
    submit_text="Adicionar",
):
    prefix = _PREFIX.format(prefix)
    with st.form(f"{prefix}_form", enter_to_submit=False, border=False):
        st.selectbox(
            "Ativo:",
            asset_codes,
            key=f"{prefix}_asset_b3_code",
            disabled=not asset_code_editable,
        )
        st.pills(
            "Tipo da transação:",
            [k.value for k in TransactionKind],
            default=kind,
            disabled=not kind_editable,
            key=f"{prefix}_kind",
        )
        st.date_input(
            "Data da transação:",
            key=f"{prefix}_date",
            format=config.ST_DATE_FORMAT,
            value=transaction_date,
            disabled=not transaction_date_editable,
        )
        st.number_input(
            "Valor por unidade (R$):",
            key=f"{prefix}_value_per_share",
            min_value=0.0,
            value=value_per_share,
            step=1.0,
            format="%0.5f",
            disabled=not value_per_share_editable,
        )
        st.number_input(
            "Quantidade de unidades:",
            key=f"{prefix}_shares",
            min_value=0,
            value=shares,
            step=1,
            format="%d",
            disabled=not shares_editable,
        )

        submit = st.form_submit_button(
            submit_text,
            on_click=on_click,
            args=[Manager.get_proxied_data_state("transaction_dialog", prefix)],
        )

        # If submit, run on_click and rerun app
        if submit:
            st.rerun()


def _earning_dialog(
    prefix: str,
    asset_codes: list[str],
    on_click: Callable[[ScopedState], None] = None,
    asset_code_editable: bool = True,
    hold_date=None,
    hold_date_editable: bool = True,
    payment_date=None,
    payment_date_editable: bool = True,
    kind=None,
    kind_editable: bool = True,
    value_per_share=0.0,
    value_per_share_editable: bool = True,
    ir_percentage=0.0,
    ir_percentage_editable: bool = True,
    submit_text="Adicionar",
):
    prefix = _PREFIX.format(prefix)
    with st.form(f"{prefix}_form", enter_to_submit=False, border=False):
        st.selectbox(
            "Ativo:",
            asset_codes,
            key=f"{prefix}_asset_b3_code",
            disabled=not asset_code_editable,
        )
        st.date_input(
            "Data de custódia:",
            key=f"{prefix}_hold_date",
            format=config.ST_DATE_FORMAT,
            value=hold_date,
            disabled=not hold_date_editable,
        )
        st.date_input(
            "Data de pagamento:",
            key=f"{prefix}_payment_date",
            format=config.ST_DATE_FORMAT,
            value=payment_date,
            disabled=not payment_date_editable,
        )
        st.number_input(
            "Valor por unidade (R$):",
            key=f"{prefix}_value_per_share",
            min_value=0.0,
            step=0.01,
            value=value_per_share,
            format="%0.5f",
            disabled=not value_per_share_editable,
        )
        st.pills(
            "Tipo de provento:",
            [k.value for k in EarningKind],
            key=f"{prefix}_kind",
            default=kind,
            disabled=not kind_editable,
        )
        st.number_input(
            "Imposto de Renda Retido na Fonte (%):",
            key=f"{prefix}_ir_percentage",
            min_value=0.0,
            step=0.01,
            value=ir_percentage,
            format="%0.2f",
            disabled=not ir_percentage_editable,
        )

        submit = st.form_submit_button(
            submit_text,
            on_click=on_click,
            args=[Manager.get_proxied_data_state("earning_create", prefix)],
        )

        # If submit, run on_click and rerun app
        if submit:
            st.rerun()


@st.dialog("Adicionar ativo")
def asset_create(create_fn: Callable[[ScopedState], None]):
    _asset_dialog("asset_create", on_click=create_fn)


@st.dialog("Atualizar ativo")
def asset_update(
    b3_code: str,
    name: str,
    description: str,
    kind: str,
    added: date,
    update_fn: Callable[[ScopedState], None],
):
    _asset_dialog(
        "asset_update",
        on_click=update_fn,
        b3_editable=False,
        b3_code=b3_code,
        name=name,
        description=description,
        kind=kind,
        submit_text="Atualizar",
        added=added,
        added_editable=True,
    )


@st.dialog("Adicionar transação")
def add_transaction(
    asset_codes: list[str],
    create_fn: Callable[[ScopedState], None],
):
    _transaction_dialog(
        "transaction_create", asset_codes=asset_codes, on_click=create_fn
    )


@st.dialog("Atualizar transação")
def transaction_update(
    asset_code: str,
    kind: str,
    transaction_date: date,
    value_per_share: float,
    shares: int,
    update_fn: Callable[[ScopedState], None],
):
    _transaction_dialog(
        "transaction_update",
        asset_codes=[asset_code],
        kind=kind,
        transaction_date=transaction_date,
        value_per_share=value_per_share,
        shares=shares,
        asset_code_editable=False,
        kind_editable=True,
        value_per_share_editable=True,
        shares_editable=True,
        transaction_date_editable=False,
        on_click=update_fn,
        submit_text="Atualizar",
    )


@st.dialog("Cadastrar Provento")
def add_earning(
    asset_codes: list[str],
    create_fn: Callable[[ScopedState], None],
):
    _earning_dialog("earning_create", asset_codes=asset_codes, on_click=create_fn)


@st.dialog("Atualizar Provento")
def earning_update(
    asset_code: str,
    kind: str,
    hold_date: date,
    payment_date: date,
    value_per_share: float,
    ir_percentage: float,
    update_fn: Callable[[ScopedState], None],
):
    _earning_dialog(
        "earning_update",
        asset_codes=[asset_code],
        asset_code_editable=False,
        kind=kind,
        kind_editable=True,
        hold_date=hold_date,
        hold_date_editable=False,
        payment_date=payment_date,
        payment_date_editable=True,
        value_per_share=value_per_share,
        value_per_share_editable=True,
        ir_percentage=ir_percentage,
        ir_percentage_editable=True,
        on_click=update_fn,
        submit_text="Atualizar",
    )


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
