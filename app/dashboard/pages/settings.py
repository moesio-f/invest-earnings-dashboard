from datetime import date
from enum import Enum
from io import StringIO
from typing import Callable

import pandas as pd
import streamlit as st

from app.dashboard.api import api
from app.dashboard.components import dataframes as cdf
from app.dashboard.components import form_dialogs as cfd
from app.dashboard.scoped_state import ScopedState
from app.db.models import AssetKind, EarningKind, EconomicIndex, TransactionKind

state = ScopedState("settings")


# === Funções utilitárias ===
def create_asset(data: ScopedState):
    api.create_asset(
        b3_code=data.b3_code(),
        name=data.name(),
        description=data.description(),
        kind=AssetKind.from_value(data.kind()),
        added=date.today(),
    )
    update_state(update_assets=True)


def add_transaction(data: ScopedState):
    api.add_transaction(
        asset_b3_code=data.asset_b3_code(),
        date=data.date(),
        value_per_share=data.value_per_share(),
        shares=data.shares(),
        kind=TransactionKind.from_value(data.kind()),
    )
    update_state(update_transactions=True, filter_transactions=True)


def add_earning(data: ScopedState):
    api.add_earning(
        asset_b3_code=data.asset_b3_code(),
        hold_date=data.hold_date(),
        payment_date=data.payment_date(),
        value_per_share=data.value_per_share(),
        ir_percentage=data.ir_percentage(),
        kind=EarningKind.from_value(data.kind()),
    )
    update_state(update_earnings=True, filter_earnings=True)


def add_economic(data: ScopedState):
    api.add_economic_data(
        index=data.index(),
        reference_date=data.reference_date(),
        percentage_change=data.percentage_change(),
    )
    update_state(update_economic_data=True)


def load_economic_data(data: ScopedState):
    io = StringIO(data.csv_contents())
    io.seek(0)
    data = pd.read_csv(io).to_dict("records")
    for d in data:
        d["index"] = EconomicIndex.from_value(d["index"])

    api.load_economic_data(*data)


def filter_transactions():
    update_state(filter_transactions=True)


def filter_earnings():
    update_state(filter_earnings=True)


def csv_insert(data: ScopedState, add_fn: Callable[[ScopedState], None]):
    io = StringIO(data.csv_contents())
    io.seek(0)
    df = pd.read_csv(io)

    class _Proxy:
        def __init__(self, v):
            self.v = v

        def __call__(self):
            return self.v

    for _, row in df.iterrows():
        # Prepare scope
        scope = ScopedState("csv_insert")
        for idx, value in row.items():
            if isinstance(value, Enum):
                value = value.from_value(value)

            if "date" in idx:
                value = date.fromisoformat(value)

            scope[idx] = _Proxy(value)

        # Add for this row
        add_fn(scope)

        # Clear scope to avoid any
        #   mismatch
        scope.clear()


# === Inicializando estado da página ===
def update_state(
    update_assets: bool = False,
    update_transactions: bool = False,
    update_earnings: bool = False,
    update_economic_data: bool = False,
    filter_transactions: bool = False,
    filter_earnings: bool = False,
    *args,
    **kwargs,
):
    # Is page initialized?
    initialize = not state.get("initialized", False)

    # Update assets
    if update_assets or initialize:
        state.assets = api.assets()
        state.asset_codes = list(sorted([a.b3_code for a in state.assets]))

    # Update transactions
    if update_transactions or initialize:
        state.transactions = api.transactions()

    # Update earnings
    if update_earnings or initialize:
        state.earnings = api.earnings()

    # Update economic data
    if update_economic_data or initialize:
        state.economic = api.economic_data()

    # Apply filters
    for cond, default, st_key in zip(
        [filter_transactions, filter_earnings],
        [
            ("Todos", [k.value for k in TransactionKind]),
            ("Todos", [k.value for k in EarningKind]),
        ],
        ["transaction", "earning"],
    ):
        if cond or initialize:
            try:
                code = st.session_state[f"filter_{st_key}_code"]
                kind = st.session_state[f"filter_{st_key}_kind"]
            except:
                code, kind = default

            def _filter(obj) -> bool:
                return (code == "Todos" or obj.asset_b3_code == code) and (
                    obj.kind.value in kind
                )

            key = f"{st_key}s"
            state[key] = list(filter(_filter, state[key]))

    # If we initialized, set flag
    if initialize:
        state.initialized = True


update_state()


# === Título ===
st.title("Configurações")
st.markdown("Cadastro e gerenciamento de ativos, proventos e transações.")

# ==== Ativos ===
st.subheader("Ativos Financeiros", divider="gray")

# Menu
if st.button(
    "Adicionar ativo",
    icon=":material/add_circle:",
    help="Cadastrar um novo ativo no sistema.",
    use_container_width=True,
):
    cfd.asset_create(create_asset)

# Listagem de ativos
cdf.asset_dataframe(state.assets)


if st.button(
    "Importar ativos",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    cfd.text_upload(
        lambda d: csv_insert(d, create_asset),
        "Cole no espaço abaixo o conteúdo do arquivo CSV contendo os proventos "
        "a serem importadas. Deve possuir cabeçalho: `b3_code,name,description,"
        "kind`",
    )

# ==== Transações ===
st.subheader("Transações", divider="gray")

# Adicionar transação
if st.button(
    "Adicionar transação",
    icon=":material/add_circle:",
    help="Cadastrar uma nova transação no sistema.",
    use_container_width=True,
):
    cfd.add_transaction(state.asset_codes, add_transaction)

# Filtros
cols = st.columns(2)
cols[0].selectbox(
    "Ativo:",
    ["Todos"] + state.asset_codes,
    key="filter_transaction_code",
    on_change=filter_transactions,
)
cols[1].pills(
    "Tipo:",
    (values := [k.value for k in TransactionKind]),
    selection_mode="multi",
    default=values,
    key="filter_transaction_kind",
    on_change=filter_transactions,
)

# Listagem de transações
cdf.transaction_dataframe(state.transactions)

if st.button(
    "Importar transações",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    cfd.text_upload(
        lambda d: csv_insert(d, add_transaction),
        "Cole no espaço abaixo o conteúdo do arquivo CSV contendo os proventos "
        "a serem importadas. Deve possuir cabeçalho: `asset_b3_code,date,kind,"
        "value_per_share,shares`",
    )

# === Proventos ===
st.subheader("Proventos", divider="gray")


# Adicionar provento
if st.button(
    "Adicionar provento",
    icon=":material/add_circle:",
    help="Cadastrar um novo provento no sistema.",
    use_container_width=True,
):
    cfd.add_earning(state.asset_codes, add_earning)

# Filtros
cols = st.columns(2)
cols[0].selectbox(
    "Ativo:",
    ["Todos"] + state.asset_codes,
    key="filter_earning_code",
    on_change=filter_earnings,
)
cols[1].pills(
    "Tipo:",
    (values := [k.value for k in EarningKind]),
    selection_mode="multi",
    default=values,
    key="filter_earning_kind",
    on_change=filter_earnings,
)

# Listagem de proventos
cdf.earning_dataframe(state.earnings)

if st.button(
    "Importar proventos",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    cfd.text_upload(
        lambda d: csv_insert(d, add_earning),
        "Cole no espaço abaixo o conteúdo do arquivo CSV contendo os proventos "
        "a serem importadas. Deve possuir cabeçalho: `asset_b3_code,hold_date,"
        "payment_date,value_per_share,kind,ir_percentage`",
    )


# === Dados Econômicos ===
st.subheader("Dados Econômicos", divider="gray")

# Adicionar dado
if st.button(
    "Adicionar dado",
    icon=":material/add_circle:",
    help="Cadastrar um novo dado econônico no sistema.",
    use_container_width=True,
):
    cfd.add_economic_data(add_economic)

# Listagem
cdf.economic_data_dataframe(state.economic)

if st.button(
    "Importar índices econônomicos",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    cfd.text_upload(
        load_economic_data,
        "Cole no espaço abaixo o conteúdo do arquivo CSV contendo os proventos "
        "a serem importadas. Deve possuir cabeçalho: `index,reference_date,"
        "percentage_change,index_number`",
    )
