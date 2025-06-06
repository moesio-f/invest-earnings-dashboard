import functools

import pandas as pd
import streamlit as st

from app.dashboard import utils
from app.dashboard.api import api
from app.dashboard.components import dataframes as cdf
from app.dashboard.components import form_dialogs as cfd
from app.dashboard.state import Manager, ScopedState
from app.db.models import EarningKind, TransactionKind

state = Manager.get_page_state("settings")


# === Inicializando estado da página ===
def update_state(
    update_assets: bool = False,
    update_transactions: bool = False,
    update_earnings: bool = False,
    update_economic_data: bool = False,
):
    # Is page initialized?
    initialize = not state.get("initialized", False)

    # Update assets
    if update_assets or initialize:
        data = dict(
            b3_code=[],
            name=[],
            description=[],
            kind=[],
            added=[],
        )

        for a in api.assets():
            for k in data.keys():
                # Obter valor do modelo
                v = getattr(a, k)

                # Se for tipo do ativo,
                #   mapear para representação
                #   textual
                if k == "kind":
                    v = v.value

                # Adicionar dado do ativo
                data[k].append(v)

        state.assets = pd.DataFrame(data).sort_values(["kind", "b3_code"])
        state.asset_codes = sorted(state.assets.b3_code.sort_values().tolist())

    # Update transactions
    if update_transactions or initialize:
        data = dict(
            id=[],
            asset_b3_code=[],
            kind=[],
            date=[],
            value_per_share=[],
            shares=[],
        )

        for t in api.transactions():
            for k in data.keys():
                # Obter valor do modelo
                v = getattr(t, k)

                # Se for tipo do ativo,
                #   mapear para representação
                #   textual
                if k == "kind":
                    v = v.value

                # Adicionar dado do ativo
                data[k].append(v)

        state.transactions = pd.DataFrame(data).sort_values("date", ascending=False)

    # Update earnings
    if update_earnings or initialize:
        data = dict(
            id=[],
            asset_b3_code=[],
            kind=[],
            hold_date=[],
            payment_date=[],
            value_per_share=[],
            ir_percentage=[],
        )

        for e in api.earnings():
            for k in data.keys():
                # Obter valor do modelo
                v = getattr(e, k)

                # Se for tipo do ativo,
                #   mapear para representação
                #   textual
                if k == "kind":
                    v = v.value

                # Adicionar dado do ativo
                data[k].append(v)

        state.earnings = pd.DataFrame(data).sort_values("payment_date", ascending=False)

    # Update economic data
    if update_economic_data or initialize:
        state.economic = api.economic_data()

    # Apply filters
    for default, st_key in zip(
        [
            ("Todos", [k.value for k in TransactionKind]),
            ("Todos", [k.value for k in EarningKind]),
        ],
        ["transaction", "earning"],
    ):
        try:
            code = st.session_state[f"filter_{st_key}_code"]
            kind = st.session_state[f"filter_{st_key}_kind"]
        except:
            code, kind = default

        def _filter(row) -> bool:
            return (code == "Todos" or row.asset_b3_code == code) and (row.kind in kind)

        key = f"{st_key}s"
        state[key] = state[key][state[key].apply(_filter, axis=1)]

    # If we initialized, set flag
    if initialize:
        state.initialized = True


update_state()

# === Funções utilitárias ===
create_asset = functools.partial(
    utils.create_asset, callback=functools.partial(update_state, update_assets=True)
)

add_transaction = functools.partial(
    utils.add_transaction,
    callback=functools.partial(update_state, update_transactions=True),
)

add_earning = functools.partial(
    utils.add_earning,
    callback=functools.partial(update_state, update_earnings=True),
)

add_economic = functools.partial(
    utils.add_economic,
    callback=functools.partial(update_state, update_economic_data=True),
)

load_economic_data = functools.partial(
    utils.load_economic_data,
    callback=functools.partial(update_state, update_economic_data=True),
)


def update_asset(data: ScopedState):
    event = data.event()["selection"]
    if event["rows"]:
        item = state.assets.iloc[event["rows"][0]]
        cfd.asset_update(
            b3_code=item.b3_code,
            name=item["name"],
            description=item.description,
            kind=item.kind,
            added=item.added,
            update_fn=utils.update_asset,
        )
    update_state(update_assets=True)


def update_transaction(data: ScopedState):
    event = data.event()["selection"]
    if event["rows"]:
        item = state.transactions.iloc[event["rows"][0]]

        cfd.transaction_update(
            asset_code=item.asset_b3_code,
            kind=item.kind,
            transaction_date=item.date,
            value_per_share=item.value_per_share,
            shares=item.shares,
            update_fn=functools.partial(
                utils.transaction_update, transaction_id=item["id"].item()
            ),
        )
    update_state(update_transactions=True)


def update_earning(data: ScopedState):
    event = data.event()["selection"]
    if event["rows"]:
        item = state.earnings.iloc[event["rows"][0]]

        cfd.earning_update(
            asset_code=item.asset_b3_code,
            kind=item.kind,
            hold_date=item.hold_date,
            payment_date=item.payment_date,
            value_per_share=item.value_per_share,
            ir_percentage=item.ir_percentage,
            update_fn=functools.partial(
                utils.earning_update, earning_id=item["id"].item()
            ),
        )
    update_state(update_earnings=True)


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
cdf.asset_dataframe(
    state.assets, selection_mode="single-row", selection_callable=update_asset
)


if st.button(
    "Importar ativos",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    cfd.text_upload(
        lambda d: utils.csv_insert(d, create_asset),
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
    on_change=update_state,
)
cols[1].pills(
    "Tipo:",
    (values := [k.value for k in TransactionKind]),
    selection_mode="multi",
    default=values,
    key="filter_transaction_kind",
    on_change=update_state,
)

# Listagem de transações
cdf.transaction_dataframe(
    state.transactions,
    selection_mode="single-row",
    selection_callable=update_transaction,
)

if st.button(
    "Importar transações",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    cfd.text_upload(
        lambda d: utils.csv_insert(d, add_transaction),
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
    on_change=update_state,
)
cols[1].pills(
    "Tipo:",
    (values := [k.value for k in EarningKind]),
    selection_mode="multi",
    default=values,
    key="filter_earning_kind",
    on_change=update_state,
)

# Listagem de proventos
cdf.earning_dataframe(
    state.earnings,
    selection_mode="single-row",
    selection_callable=update_earning,
)

if st.button(
    "Importar proventos",
    icon=":material/file_upload:",
    help="Importar de arquivo CSV.",
    use_container_width=True,
):
    cfd.text_upload(
        lambda d: utils.csv_insert(d, add_earning),
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
