"""Modelos de retorno com pydantic."""

from datetime import date

from invest_earning.database.wallet import (
    AssetKind,
    EarningKind,
    EconomicIndex,
    TransactionKind,
)
from pydantic import BaseModel, ConfigDict


class AssetSchemaV1(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    b3_code: str
    kind: AssetKind
    name: str
    description: str
    added: date


class EarningSchemaV1(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_b3_code: str
    hold_date: date
    payment_date: date
    value_per_share: float
    ir_percentage: float
    kind: EarningKind


class TransactionSchemaV1(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_b3_code: str
    date: date
    kind: TransactionKind
    value_per_share: float
    shares: int


class EconomicSchemaV1(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    index: EconomicIndex
    reference_date: date
    percentage_change: float
