"""API para comunicação
nativa em Python através
de um facade.
"""

import functools
from datetime import date
from typing import Annotated

from app import utils as app_utils
from app.db import RequiresSession
from app.dispatcher import RequiresDispatcher
from fastapi import APIRouter, Body, HTTPException, Response
from invest_earning.database.wallet import (
    Asset,
    AssetKind,
    Earning,
    EarningKind,
    EconomicData,
    EconomicIndex,
    Position,
    Transaction,
    TransactionKind,
)

from . import utils
from .models import (
    AssetSchemaV1,
    EarningSchemaV1,
    EconomicSchemaV1,
    TransactionSchemaV1,
)

EmbedBody = functools.partial(Body, embed=True)

router = APIRouter()
asset = APIRouter(prefix="/asset", tags=["v1 · Ativos"])
earnings = APIRouter(prefix="/earnings", tags=["v1 · Proventos"])
transactions = APIRouter(prefix="/transactions", tags=["v1 · Transações"])
economic = APIRouter(prefix="/economic", tags=["v1 · Dados Econômicos"])
position = APIRouter(prefix="/position", tags=["v1 · Posições"])


@asset.get("/info/{b3_code}")
def get_asset(b3_code: str, session=RequiresSession) -> AssetSchemaV1:
    """Retorna dados do ativo."""
    asset = session.query(Asset).where(Asset.b3_code == b3_code).one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found.")
    return asset


@asset.get("/list")
def list_assets(session=RequiresSession) -> list[AssetSchemaV1]:
    """Retorna todos ativos cadastrados no sistema."""
    return list(session.query(Asset).all())


@asset.post("/create")
def create_asset(
    b3_code: Annotated[str, EmbedBody()],
    name: Annotated[str, EmbedBody()],
    kind: Annotated[AssetKind, EmbedBody()],
    description: Annotated[str, EmbedBody()] = "",
    added: Annotated[date, EmbedBody()] = None,
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
) -> AssetSchemaV1:
    """Realiza a criação de um ativo."""
    if added is None:
        added = date.today()

    # Check whether it already exists
    if session.query(Asset).where(Asset.b3_code == b3_code).one_or_none() is not None:
        raise HTTPException(status_code=400, detail="Asset already exists.")

    asset = Asset(
        b3_code=b3_code,
        name=name,
        description=description,
        kind=kind,
        added=added,
    )
    session.add(asset)
    session.commit()

    # Notify
    dispatcher.notify_asset_create(asset)
    return asset


@asset.patch("/update/{b3_code}")
def update_asset(
    b3_code: str,
    name: Annotated[str, EmbedBody()] = None,
    description: Annotated[str, EmbedBody()] = None,
    kind: Annotated[AssetKind, EmbedBody()] = None,
    added: Annotated[date, EmbedBody()] = None,
    session=RequiresSession,
) -> AssetSchemaV1:
    """Realiza a atualização de um ativo. Campos `null` são ignorados e não
    sofrem atualização.
    """
    asset = session.query(Asset).where(Asset.b3_code == b3_code).one_or_none()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found.")

    # Update fields
    for field, value in zip(
        ["name", "description", "kind", "added"],
        [name, description, kind, added],
    ):
        if value is not None:
            setattr(asset, field, value)

    # Commit
    session.commit()

    return asset


@asset.delete(
    "/delete/{b3_code}",
    response_class=Response,
    status_code=204,
)
def delete_asset(
    b3_code: str,
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
):
    """Remove um ativo do sistema."""
    # Query
    asset = session.query(Asset).where(Asset.b3_code == b3_code).one_or_none()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found.")

    # Delete
    session.delete(asset)

    # Commit
    session.commit()

    # Notify
    dispatcher.notify_asset_delete(asset)


@earnings.post("/create")
def create_earning(
    asset_b3_code: Annotated[str, EmbedBody()],
    hold_date: Annotated[date, EmbedBody()],
    payment_date: Annotated[date, EmbedBody()],
    value_per_share: Annotated[float, EmbedBody()],
    ir_percentage: Annotated[float, EmbedBody()],
    kind: Annotated[EarningKind, EmbedBody()],
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
) -> EarningSchemaV1:
    """Adiciona um novo provento para o ativo."""
    # Create earning
    earning = Earning(
        asset_b3_code=asset_b3_code,
        hold_date=hold_date,
        payment_date=payment_date,
        value_per_share=value_per_share,
        ir_percentage=ir_percentage,
        kind=kind,
    )
    session.add(earning)

    # Update earnings rights
    utils.update_earning_rights(earning=earning, session=session)

    # Commit
    session.commit()

    # Notify
    dispatcher.notify_earning_create(earning)

    return earning


@earnings.patch("/update/{earning_id}")
def update_earning(
    earning_id: int,
    asset_b3_code: Annotated[str, EmbedBody()] = None,
    hold_date: Annotated[date, EmbedBody()] = None,
    payment_date: Annotated[date, EmbedBody()] = None,
    value_per_share: Annotated[float, EmbedBody()] = None,
    ir_percentage: Annotated[float, EmbedBody()] = None,
    kind: Annotated[EarningKind, EmbedBody()] = None,
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
) -> EarningSchemaV1:
    """Atualiza dados de um provento previamente cadastrado. Campos `null` não
    são atualizados.
    """
    earning = session.query(Earning).where(Earning.id == earning_id).one_or_none()

    if earning is None:
        raise HTTPException(status_code=404, detail="Earning not found.")

    updated_fields = dict()

    # Update fields
    for field, value in zip(
        [
            "asset_b3_code",
            "hold_date",
            "payment_date",
            "value_per_share",
            "ir_percentage",
            "kind",
        ],
        [asset_b3_code, hold_date, payment_date, value_per_share, ir_percentage, kind],
    ):
        if value is not None:
            updated_fields[field] = (getattr(earning, field), value)
            setattr(earning, field, value)

    # Update rights
    utils.update_earning_rights(session=session, earning=earning)

    # Commit
    session.commit()

    # Notify
    dispatcher.notify_earning_update(earning, updated_fields)

    return earning


@earnings.delete(
    "/delete/{earning_id}",
    response_class=Response,
    status_code=204,
)
def delete_earning(
    earning_id: int,
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
):
    """Remove um provento previamente cadastrado."""
    # Query transaction
    earning = session.query(Earning).where(Earning.id == earning_id).one_or_none()

    if earning is None:
        raise HTTPException(status_code=404, detail="Earning not found.")

    # Delete
    session.delete(earning)

    # Commit
    session.commit()

    # Notify
    dispatcher.notify_earning_delete(earning)


@earnings.get("/info/{asset_b3_code}")
def asset_earnings(
    asset_b3_code: str, session=RequiresSession
) -> list[EarningSchemaV1]:
    """Retorna todos proventos cadastrados para um ativo."""
    return list(
        session.query(Earning).where(Earning.asset_b3_code == asset_b3_code).all()
    )


@earnings.get("/list")
def list_earnings(session=RequiresSession) -> list[EarningSchemaV1]:
    """Retorna todos os proventos cadastrados no sistema."""
    return list(session.query(Earning).all())


@transactions.post("/create")
def create_transaction(
    asset_b3_code: Annotated[str, EmbedBody()],
    date: Annotated[date, EmbedBody()],
    kind: Annotated[TransactionKind, EmbedBody()],
    value_per_share: Annotated[float, EmbedBody()],
    shares: Annotated[int, EmbedBody()],
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
) -> TransactionSchemaV1:
    """Cadastra uma nova transação envolvendo um ativo."""
    # Create transaction
    transaction = Transaction(
        asset_b3_code=asset_b3_code,
        date=date,
        kind=kind,
        value_per_share=value_per_share,
        shares=shares,
    )
    session.add(transaction)

    # Update earnings rights
    utils.update_earning_rights(transaction=transaction, session=session)

    # Commit
    session.commit()

    # Notify
    dispatcher.notify_transaction_create(transaction)

    return transaction


@transactions.patch("/update/{transaction_id}")
def update_transaction(
    transaction_id: int,
    asset_b3_code: Annotated[str, EmbedBody()] = None,
    date: Annotated[date, EmbedBody()] = None,
    kind: Annotated[TransactionKind, EmbedBody()] = None,
    value_per_share: Annotated[float, EmbedBody()] = None,
    shares: Annotated[int, EmbedBody()] = None,
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
) -> TransactionSchemaV1:
    """Atualiza informações de uma transação envolvendo um ativo. Campos `null`
    não são alterados."""
    transaction = (
        session.query(Transaction).where(Transaction.id == transaction_id).one_or_none()
    )

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    updated_fields = dict()

    # Update fields
    for field, value in zip(
        ["asset_b3_code", "kind", "value_per_share", "shares", "date"],
        [asset_b3_code, kind, value_per_share, shares, date],
    ):
        if value is not None:
            updated_fields[field] = (getattr(transaction, field), value)
            setattr(transaction, field, value)

    utils.update_earning_rights(transaction=transaction, session=session)

    # Commit
    session.commit()

    # Notify
    dispatcher.notify_transaction_update(transaction, updated_fields)
    return transaction


@transactions.delete(
    "/delete/{transaction_id}",
    response_class=Response,
    status_code=204,
)
def delete_transaction(
    transaction_id: int,
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
):
    """Remove uma transação previamente cadastrada."""
    # Query
    transaction = (
        session.query(Transaction).where(Transaction.id == transaction_id).one_or_none()
    )

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # Delete
    session.delete(transaction)

    # Commit
    session.commit()

    # Notify
    dispatcher.notify_transaction_delete(transaction)


@transactions.get("/info/{asset_b3_code}")
def asset_transactions(
    asset_b3_code: str, session=RequiresSession
) -> list[TransactionSchemaV1]:
    """Retorna todas transações para o ativo."""
    return list(
        session.query(Transaction)
        .where(Transaction.asset_b3_code == asset_b3_code)
        .all()
    )


@transactions.get("/list")
def list_transactions(session=RequiresSession) -> list[TransactionSchemaV1]:
    """Retorna todas transações cadastradas no sistema."""
    return list(session.query(Transaction).all())


@economic.post("/add")
def add_economic_data(
    data: Annotated[list[EconomicSchemaV1], EmbedBody()],
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
) -> list[EconomicSchemaV1]:
    """Adiciona dados econômicos em bulk."""
    objects = []
    for idx, d in enumerate(data):
        d = d.dict()
        d["reference_date"] = app_utils.to_last_day_of_the_month(d["reference_date"])

        # Check whether it already exists
        if (
            session.query(EconomicData)
            .where(EconomicData.index == d["index"])
            .where(EconomicData.reference_date == d["reference_date"])
            .one_or_none()
            is not None
        ):
            raise HTTPException(
                status_code=400,
                detail="Economic data already exists for "
                f"<{d['index']}, {d['reference_date']}> (index={idx}).",
            )

        objects.append(EconomicData(**d))
        session.add(objects[-1])

    # Save all transactions
    session.commit()

    # Notify
    for obj in objects:
        dispatcher.notify_economic_add(obj)

    return objects


@economic.delete(
    "/{economic_index}/{reference_date}",
    response_class=Response,
    status_code=204,
)
def delete_economic_data(
    economic_index: EconomicIndex,
    reference_date: date,
    session=RequiresSession,
    dispatcher=RequiresDispatcher,
):
    """Remove dados econômicos para um dado índice em uma data."""
    # Query
    economic = (
        session.query(EconomicData)
        .where(EconomicData.index == economic_index)
        .where(
            EconomicData.reference_date
            == app_utils.to_last_day_of_the_month(reference_date)
        )
        .one_or_none()
    )

    if economic is None:
        raise HTTPException(status_code=404, detail="Economic data not found.")

    # Delete
    session.delete(economic)

    # Commit
    session.commit()

    # Notify
    dispatcher.notify_economic_delete(economic)
    return Response(status_code=200)


@economic.get("/info/{economic_index}")
def index_economic_data(
    economic_index: EconomicIndex, session=RequiresSession
) -> list[EconomicSchemaV1]:
    """Retorna todos os dados para o índice econômico."""
    return list(
        session.query(EconomicData).where(EconomicData.index == economic_index).all()
    )


@economic.get("/list")
def list_economic_data(session=RequiresSession) -> list[EconomicSchemaV1]:
    """Retorna todos os dados econômicos cadastrados."""
    return list(session.query(EconomicData).all())


@position.get("/on/{reference_date}")
def position_on_date(reference_date: date, session=RequiresSession) -> list[Position]:
    """Retorna a posição de investimentos em uma data."""
    return Position.get(session, reference_date)


router.include_router(asset)
router.include_router(earnings)
router.include_router(transactions)
router.include_router(economic)
router.include_router(position)
