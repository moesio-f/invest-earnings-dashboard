"""Página de gerenciamento de carteira."""

import functools

import streamlit as st
from app.utils.state import ScopedState
from app.wallet import callbacks, constants
from app.wallet.components import dataframes, dialogs
from app.wallet.states.settings import SettingState

# === Inicialização da página ===
state = SettingState()
state.update_state()

# === Callbacks aliases ===
create_asset = functools.partial(
    callbacks.create_asset,
    callback=functools.partial(state.update_state, update_assets=True),
)

add_transaction = functools.partial(
    callbacks.create_transaction,
    callback=functools.partial(state.update_state, update_transactions=True),
)

add_earning = functools.partial(
    callbacks.create_earning,
    callback=functools.partial(state.update_state, update_earnings=True),
)

add_economic = functools.partial(
    callbacks.add_economic,
    callback=functools.partial(state.update_state, update_economic_data=True),
)


# === Selection callbacks ===
def select_asset(data: ScopedState):
    event = data.event()["selection"]
    if event["rows"]:
        item = state.variables.assets.iloc[event["rows"][0]]
        dialogs.asset_update(
            b3_code=item.b3_code,
            name=item["name"],
            description=item.description,
            kind=item.kind,
            added=item.added,
            update_fn=callbacks.update_asset,
        )


def select_transaction(data: ScopedState):
    event = data.event()["selection"]
    if event["rows"]:
        item = state.variables.filtered_transactions.iloc[event["rows"][0]]
        dialogs.transaction_update(
            asset_code=item.asset_b3_code,
            kind=item.kind,
            transaction_date=item.date,
            value_per_share=item.value_per_share,
            shares=item.shares,
            update_fn=functools.partial(
                callbacks.update_transaction, transaction_id=item["id"].item()
            ),
        )


def select_earning(data: ScopedState):
    event = data.event()["selection"]
    if event["rows"]:
        item = state.variables.filtered_earnings.iloc[event["rows"][0]]
        dialogs.earning_update(
            asset_code=item.asset_b3_code,
            kind=item.kind,
            hold_date=item.hold_date,
            payment_date=item.payment_date,
            value_per_share=item.value_per_share,
            ir_percentage=item.ir_percentage,
            update_fn=functools.partial(
                callbacks.update_or_delete_earning, earning_id=item["id"].item()
            ),
        )


# =========================================================================
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
    dialogs.asset_create(create_asset)

# Listagem de ativos
dataframes.asset_dataframe(
    state.variables.assets, selection_mode="single-row", selection_callable=select_asset
)


if st.button(
    "Importar ativos",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    dialogs.text_upload(
        lambda d: callbacks.csv_insert(d, create_asset),
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
    dialogs.add_transaction(state.variables.asset_codes, add_transaction)

# Filtros
cols = st.columns(2)
cols[0].selectbox(
    "Ativo:",
    ["Todos"] + state.variables.asset_codes,
    key=state.register_component("transaction_filter_code"),
    on_change=state.update_state,
)
cols[1].pills(
    "Tipo:",
    (values := constants.TransactionKinds),
    selection_mode="multi",
    default=values,
    key=state.register_component("transaction_filter_kind"),
    on_change=state.update_state,
)

# Listagem de transações
dataframes.transaction_dataframe(
    state.variables.filtered_transactions,
    selection_mode="single-row",
    selection_callable=select_transaction,
)

if st.button(
    "Importar transações",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    dialogs.text_upload(
        lambda d: callbacks.csv_insert(d, add_transaction),
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
    dialogs.add_earning(state.variables.asset_codes, add_earning)

# Filtros
cols = st.columns(2)
cols[0].selectbox(
    "Ativo:",
    ["Todos"] + state.variables.asset_codes,
    key=state.register_component("earning_filter_code"),
    on_change=state.update_state,
)
cols[1].pills(
    "Tipo:",
    (values := constants.EarningKinds),
    selection_mode="multi",
    default=values,
    key=state.register_component("earning_filter_kind"),
    on_change=state.update_state,
)

# Listagem de proventos
dataframes.earning_dataframe(
    state.variables.filtered_earnings,
    selection_mode="single-row",
    selection_callable=select_earning,
)

if st.button(
    "Importar proventos",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    dialogs.text_upload(
        lambda d: callbacks.csv_insert(d, add_earning),
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
    dialogs.add_economic_data(add_economic)

# Listagem
dataframes.economic_data_dataframe(state.variables.economic)

if st.button(
    "Importar índices econônomicos",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    dialogs.text_upload(
        add_economic,
        "Cole no espaço abaixo o conteúdo do arquivo CSV contendo os proventos "
        "a serem importadas. Deve possuir cabeçalho: `index,reference_date,"
        "percentage_change,index_number`",
    )
